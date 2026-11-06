"""Offline-only synthetic OCI canaries; no Docker daemon, secrets or network."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from capabilities.oci.verify_oci import OCIError, inspect_archive, main


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jbytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fixture(root: Path, *, mutate_layer: bool = False, duplicate: bool = False,
            unsafe: bool = False, multi: bool = False, docker_only: bool = False,
            short_diffid: bool = False) -> tuple[Path, str, str]:
    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode="w") as layer_tar:
        item = tarfile.TarInfo("hello.txt")
        item.size = len(b"test")
        layer_tar.addfile(item, io.BytesIO(b"test"))
    plain = inner.getvalue()
    layer = gzip.compress(plain, mtime=0)
    layer_hex = sha(layer)
    config = {
        "architecture": "amd64", "os": "linux",
        "config": {"User": "1000:1000", "WorkingDir": "/workspace"},
        "rootfs": {"type": "layers", "diff_ids": [] if short_diffid else ["sha256:" + sha(plain)]},
    }
    cfg = jbytes(config)
    manifest = {
        "schemaVersion": 2, "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {"mediaType": "application/vnd.oci.image.config.v1+json",
                   "digest": "sha256:" + sha(cfg), "size": len(cfg)},
        "layers": [{"mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                    "digest": "sha256:" + layer_hex, "size": len(layer)}],
    }
    mb = jbytes(manifest)
    manifest_digest = "sha256:" + sha(mb)
    descriptor = {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": manifest_digest, "size": len(mb),
        "platform": {"os": "linux", "architecture": "amd64"},
    }
    index = {"schemaVersion": 2, "manifests": [descriptor, descriptor] if multi else [descriptor]}
    files = {
        "oci-layout": jbytes({"imageLayoutVersion": "1.0.0"}),
        "index.json": jbytes(index),
        "blobs/sha256/" + sha(cfg): cfg,
        "blobs/sha256/" + sha(mb): mb,
        "blobs/sha256/" + layer_hex: (layer + b"corrupt") if mutate_layer else layer,
    }
    if docker_only:
        files = {"manifest.json": b"[]"}
    archive = root / "fixture.tar"
    with tarfile.open(archive, "w") as tf:
        for name, data in files.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            tf.addfile(entry, io.BytesIO(data))
        if duplicate:
            data = files["index.json"]
            entry = tarfile.TarInfo("index.json")
            entry.size = len(data)
            tf.addfile(entry, io.BytesIO(data))
        if unsafe:
            entry = tarfile.TarInfo("../escape")
            entry.type = tarfile.SYMTYPE
            entry.linkname = "/etc/passwd"
            tf.addfile(entry)
    return archive, sha(archive.read_bytes()), manifest_digest


class OCIArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_inspect_single_manifest(self):
        archive, outer, manifest = fixture(self.root)
        v = inspect_archive(archive)
        self.assertEqual(v["validation"], "OCI_DESCRIPTOR_BYTES_VERIFIED")
        self.assertEqual(v["archive"]["sha256"], outer)
        self.assertEqual(v["image"]["manifest_digest"], manifest)
        self.assertEqual(v["image"]["platform"], "linux/amd64")
        self.assertEqual(v["image"]["oci_blob_count"], 3)
        self.assertFalse(v["image"]["uncompressed_layer_diff_ids_recomputed"])
        self.assertIn("ACTUAL_IMAGE_RUNTIME", v["not_proven"])

    def test_verify_exact_expected(self):
        archive, outer, manifest = fixture(self.root)
        v = inspect_archive(archive, expected_archive_sha256=outer,
                            expected_manifest_digest=manifest,
                            expected_platform="linux/amd64")
        self.assertEqual(v["expected"]["archive_sha256"], outer)
        self.assertEqual(v["expected"]["manifest_digest"], manifest)

    def test_wrong_archive_sha_fails(self):
        archive, _, manifest = fixture(self.root)
        with self.assertRaisesRegex(OCIError, "archive SHA-256"):
            inspect_archive(archive, expected_archive_sha256="0" * 64,
                            expected_manifest_digest=manifest)

    def test_wrong_manifest_sha_fails(self):
        archive, outer, _ = fixture(self.root)
        with self.assertRaisesRegex(OCIError, "manifest digest"):
            inspect_archive(archive, expected_archive_sha256=outer,
                            expected_manifest_digest="sha256:" + "0" * 64)

    def test_platform_drift_fails(self):
        archive, _, _ = fixture(self.root)
        with self.assertRaisesRegex(OCIError, "platform"):
            inspect_archive(archive, expected_platform="linux/arm64")

    def test_tampered_blob_fails(self):
        archive, _, _ = fixture(self.root, mutate_layer=True)
        with self.assertRaisesRegex(OCIError, "descriptor size mismatch"):
            inspect_archive(archive)

    def test_unsafe_tar_member_fails(self):
        archive, _, _ = fixture(self.root, unsafe=True)
        with self.assertRaisesRegex(OCIError, "unsafe"):
            inspect_archive(archive)

    def test_duplicate_archive_path_fails(self):
        archive, _, _ = fixture(self.root, duplicate=True)
        with self.assertRaisesRegex(OCIError, "duplicate"):
            inspect_archive(archive)

    def test_multi_manifest_is_unsupported(self):
        archive, _, _ = fixture(self.root, multi=True)
        with self.assertRaisesRegex(OCIError, "single-manifest"):
            inspect_archive(archive)

    def test_docker_only_tar_is_not_oci(self):
        archive, _, _ = fixture(self.root, docker_only=True)
        with self.assertRaisesRegex(OCIError, "missing OCI JSON"):
            inspect_archive(archive)

    def test_diff_id_count_must_match(self):
        archive, _, _ = fixture(self.root, short_diffid=True)
        with self.assertRaisesRegex(OCIError, "diff_ids"):
            inspect_archive(archive)

    def test_cli_verify_requires_trusted_expected(self):
        archive, _, _ = fixture(self.root)
        self.assertEqual(main(["verify", str(archive)]), 2)

    def test_cli_writes_new_receipt(self):
        archive, outer, manifest = fixture(self.root)
        report = self.root / "receipt.json"
        self.assertEqual(main(["verify", str(archive),
                               "--expected-archive-sha256", outer,
                               "--expected-manifest-digest", manifest,
                               "--report", str(report)]), 0)
        stored = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(stored["image"]["manifest_digest"], manifest)
        self.assertEqual(main(["inspect", str(archive), "--report", str(report)]), 2)


if __name__ == "__main__":
    unittest.main()
