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
            short_diffid: bool = False, tamper_same_size: bool = False,
            mutate_config=None, mutate_manifest=None, mutate_index=None,
            omit_blob: str | None = None) -> tuple[Path, str, str]:
    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode="w") as layer_tar:
        item = tarfile.TarInfo("hello.txt")
        item.size = len(b"test")
        layer_tar.addfile(item, io.BytesIO(b"test"))
    plain = inner.getvalue()
    layer = gzip.compress(plain, mtime=0)
    layer_hex = sha(layer)
    changed_layer = (layer[:-1] + bytes([layer[-1] ^ 1])) if tamper_same_size else layer
    config = {
        "architecture": "amd64", "os": "linux",
        "config": {"User": "1000:1000", "WorkingDir": "/workspace"},
        "rootfs": {"type": "layers", "diff_ids": [] if short_diffid else ["sha256:" + sha(plain)]},
    }
    if mutate_config is not None:
        mutate_config(config)
    cfg = jbytes(config)
    manifest = {
        "schemaVersion": 2, "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {"mediaType": "application/vnd.oci.image.config.v1+json",
                   "digest": "sha256:" + sha(cfg), "size": len(cfg)},
        "layers": [{"mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                    "digest": "sha256:" + layer_hex, "size": len(layer)}],
    }
    if mutate_manifest is not None:
        mutate_manifest(manifest)
    mb = jbytes(manifest)
    manifest_digest = "sha256:" + sha(mb)
    descriptor = {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": manifest_digest, "size": len(mb),
        "platform": {"os": "linux", "architecture": "amd64"},
    }
    index = {"schemaVersion": 2, "manifests": [descriptor, descriptor] if multi else [descriptor]}
    if mutate_index is not None:
        mutate_index(index)
    files = {
        "oci-layout": jbytes({"imageLayoutVersion": "1.0.0"}),
        "index.json": jbytes(index),
        "blobs/sha256/" + sha(cfg): cfg,
        "blobs/sha256/" + sha(mb): mb,
        "blobs/sha256/" + layer_hex: (layer + b"corrupt") if mutate_layer else changed_layer,
    }
    if omit_blob is not None:
        blob_hash = {"config": sha(cfg), "manifest": sha(mb), "layer": layer_hex}[omit_blob]
        files.pop("blobs/sha256/" + blob_hash)
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

    def test_tamper_same_size_fails_digest_check(self):
        archive, _, _ = fixture(self.root, tamper_same_size=True)
        with self.assertRaisesRegex(OCIError, "descriptor digest/size mismatch"):
            inspect_archive(archive)

    def test_compressed_oci_tar_gzip(self):
        archive, _, manifest = fixture(self.root)
        zipped = self.root / "fixture.tar.gz"
        zipped.write_bytes(gzip.compress(archive.read_bytes(), mtime=0))
        actual = sha(zipped.read_bytes())
        report = inspect_archive(
            zipped, expected_archive_sha256=actual,
            expected_manifest_digest=manifest,
            expected_platform="linux/amd64",
        )
        self.assertEqual(report["archive"]["sha256"], actual)
        self.assertEqual(report["image"]["manifest_digest"], manifest)

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

    def test_explicit_index_type_and_absent_manifest_type_are_valid(self):
        archive, outer, manifest = fixture(
            self.root,
            mutate_index=lambda v: v.update(mediaType="application/vnd.oci.image.index.v1+json"),
            mutate_manifest=lambda v: v.pop("mediaType"),
        )
        self.assertEqual(inspect_archive(
            archive, expected_archive_sha256=outer, expected_manifest_digest=manifest,
        )["image"]["manifest_digest"], manifest)

    def test_explicit_wrong_top_level_media_types_fail_with_matching_hashes(self):
        for field in ("mutate_index", "mutate_manifest"):
            for wrong in ("application/example", None, []):
                with self.subTest(field=field, wrong=wrong):
                    archive, outer, manifest = fixture(
                        self.root, **{field: lambda v, w=wrong: v.update(mediaType=w)},
                    )
                    with self.assertRaisesRegex(OCIError, "mediaType"):
                        inspect_archive(archive, expected_archive_sha256=outer,
                                        expected_manifest_digest=manifest)

    def test_embedded_descriptor_data_is_unsupported(self):
        # Base64 decodes to {}, conflicting with the referenced config.
        archive, outer, manifest = fixture(
            self.root, mutate_manifest=lambda v: v["config"].update(data="e30="),
        )
        with self.assertRaisesRegex(OCIError, "descriptor data"):
            inspect_archive(archive, expected_archive_sha256=outer,
                            expected_manifest_digest=manifest)

    def test_artifact_and_subject_semantics_are_unsupported(self):
        for level in ("mutate_index", "mutate_manifest"):
            for field, value in (("artifactType", "application/example"), ("subject", {})):
                with self.subTest(level=level, field=field):
                    archive, _, _ = fixture(
                        self.root, **{level: lambda v, f=field, x=value: v.update({f: x})},
                    )
                    with self.assertRaisesRegex(OCIError, "unsupported OCI"):
                        inspect_archive(archive)
        archive, _, _ = fixture(
            self.root, mutate_index=lambda v: v["manifests"][0].update(artifactType="application/example"),
        )
        with self.assertRaisesRegex(OCIError, "descriptor artifactType"):
            inspect_archive(archive)

    def test_invalid_explicit_index_platform_fails(self):
        for value in ("linux/amd64", [], None, {}, {"os": "linux"},
                      {"os": "", "architecture": "amd64"}):
            with self.subTest(platform=value):
                archive, _, _ = fixture(
                    self.root, mutate_index=lambda v, p=value: v["manifests"][0].update(platform=p),
                )
                with self.assertRaisesRegex(OCIError, "platform"):
                    inspect_archive(archive)

    def test_absent_index_platform_is_allowed(self):
        archive, _, _ = fixture(
            self.root, mutate_index=lambda v: v["manifests"][0].pop("platform"),
        )
        self.assertEqual(inspect_archive(archive)["image"]["platform"], "linux/amd64")

    def test_empty_or_missing_config_platform_fails(self):
        for field in ("os", "architecture"):
            for value in ("", None, " "):
                with self.subTest(field=field, value=value):
                    archive, _, _ = fixture(
                        self.root, mutate_config=lambda v, f=field, x=value: v.update({f: x}),
                    )
                    with self.assertRaisesRegex(OCIError, "platform"):
                        inspect_archive(archive)

    def test_platform_receipt_limits_are_explicit(self):
        archive, _, _ = fixture(self.root)
        unbound = inspect_archive(archive)
        self.assertIsNone(unbound["expected"]["platform"])
        self.assertIn("TARGET_PLATFORM_MATCH", unbound["not_proven"])
        matched = inspect_archive(archive, expected_platform="linux/amd64")
        self.assertNotIn("TARGET_PLATFORM_MATCH", matched["not_proven"])
        self.assertIn("PLATFORM_VARIANT_OR_OS_VERSION_COMPATIBILITY", matched["not_proven"])
        for invalid in ("", "linux/amd64/v3"):
            with self.subTest(expected=invalid):
                with self.assertRaisesRegex(OCIError, "platform"):
                    inspect_archive(archive, expected_platform=invalid)

    def test_empty_expected_digests_are_invalid_not_absent(self):
        archive, _, _ = fixture(self.root)
        for key in ("expected_archive_sha256", "expected_manifest_digest"):
            with self.subTest(key=key):
                with self.assertRaises(OCIError):
                    inspect_archive(archive, **{key: ""})
        self.assertEqual(main(["inspect", str(archive), "--expected-archive-sha256", ""]), 2)

    def test_missing_config_descriptor_fails(self):
        archive, _, _ = fixture(self.root, mutate_manifest=lambda v: v.pop("config"))
        with self.assertRaisesRegex(OCIError, "config: unsupported or missing"):
            inspect_archive(archive)

    def test_missing_layer_descriptor_fields_fail(self):
        for field in ("mediaType", "digest", "size"):
            with self.subTest(field=field):
                archive, _, _ = fixture(
                    self.root, mutate_manifest=lambda v, f=field: v["layers"][0].pop(f),
                )
                with self.assertRaisesRegex(OCIError, r"layer\[0\]"):
                    inspect_archive(archive)

    def test_missing_referenced_blobs_fail(self):
        for blob in ("config", "manifest", "layer"):
            with self.subTest(blob=blob):
                archive, _, _ = fixture(self.root, omit_blob=blob)
                with self.assertRaisesRegex(OCIError, "missing referenced blob"):
                    inspect_archive(archive)

    def test_embedded_digest_is_strict_but_external_hex_is_normalized(self):
        archive, outer, manifest = fixture(self.root)
        inspected = inspect_archive(
            archive, expected_archive_sha256=outer.upper(),
            expected_manifest_digest="sha256:" + manifest[7:].upper(),
        )
        self.assertEqual(inspected["expected"]["manifest_digest"], manifest)
        archive, _, _ = fixture(
            self.root,
            mutate_manifest=lambda v: v["config"].update(
                digest="sha256:" + v["config"]["digest"][7:].upper()),
        )
        with self.assertRaisesRegex(OCIError, "lowercase"):
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
