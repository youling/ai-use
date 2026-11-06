#!/usr/bin/env python3
"""Read-only OCI image-layout tar verifier. No Fleet, registry or container engine.

V0.1 accepts a single OCI image manifest (one platform), not Docker-only save
archives, multi-manifest indexes, artifact manifests or runtime/signer proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tarfile
from typing import Any

SCHEMA = "ai-use/oci-archive-verification/v0.1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MANIFEST_TYPE = "application/vnd.oci.image.manifest.v1+json"
CONFIG_TYPE = "application/vnd.oci.image.config.v1+json"
LAYER_TYPES = {
    "application/vnd.oci.image.layer.v1.tar",
    "application/vnd.oci.image.layer.v1.tar+gzip",
    "application/vnd.oci.image.layer.v1.tar+zstd",
}
MAX_JSON = 8 * 1024 * 1024
CHUNK = 1024 * 1024


class OCIError(ValueError):
    """An archive cannot be accepted at the claimed verification level."""


def _hex(value: str, label: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value.lower()):
        raise OCIError(f"{label}: expected 64 hexadecimal SHA-256 characters")
    return value.lower()


def _digest(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise OCIError(f"{label}: expected sha256:<64hex>")
    return "sha256:" + _hex(value[7:], label)


def _stream_hash(stream) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    while True:
        data = stream.read(CHUNK)
        if not data:
            break
        digest.update(data)
        total += len(data)
    return digest.hexdigest(), total


def _safe_member_name(raw: str, directory: bool) -> str:
    if not raw or raw.startswith("/") or "\\" in raw or "\x00" in raw:
        raise OCIError("unsafe tar member name")
    name = raw
    while name.startswith("./"):
        name = name[2:]
    if directory:
        name = name.rstrip("/")
    if name in {"", "."} and directory:
        return "."
    bits = name.split("/")
    if any(x in {"", ".", ".."} for x in bits) or ":" in bits[0]:
        raise OCIError("unsafe tar member name")
    return name


def _members(tar: tarfile.TarFile) -> dict[str, tarfile.TarInfo]:
    files: dict[str, tarfile.TarInfo] = {}
    for item in tar:
        name = _safe_member_name(item.name, item.isdir())
        if not (item.isfile() or item.isdir()):
            raise OCIError("archive contains nonregular member (link/device/etc)")
        if name == ".":
            continue
        if name in files:
            raise OCIError(f"duplicate archive path: {name}")
        files[name] = item
    return files


def _read_json(tar: tarfile.TarFile, members: dict, path: str) -> dict[str, Any]:
    item = members.get(path)
    if item is None or not item.isfile():
        raise OCIError(f"missing OCI JSON: {path}")
    if item.size > MAX_JSON:
        raise OCIError(f"OCI JSON exceeds size bound: {path}")
    stream = tar.extractfile(item)
    if stream is None:
        raise OCIError(f"unreadable OCI JSON: {path}")
    try:
        value = json.loads(stream.read(MAX_JSON + 1))
    except (ValueError, UnicodeDecodeError) as exc:
        raise OCIError(f"invalid OCI JSON: {path}") from exc
    finally:
        stream.close()
    if not isinstance(value, dict):
        raise OCIError(f"OCI JSON object required: {path}")
    return value


def _descriptor(tar: tarfile.TarFile, members: dict, descriptor: Any, label: str, allowed: set[str]) -> tuple[str, str, int]:
    if not isinstance(descriptor, dict) or descriptor.get("mediaType") not in allowed:
        raise OCIError(f"{label}: unsupported or missing OCI mediaType")
    digest = _digest(descriptor.get("digest"), label)
    size = descriptor.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise OCIError(f"{label}: invalid descriptor size")
    path = "blobs/sha256/" + digest.split(":", 1)[1]
    item = members.get(path)
    if item is None or not item.isfile():
        raise OCIError(f"{label}: missing referenced blob")
    if item.size != size:
        raise OCIError(f"{label}: descriptor size mismatch")
    stream = tar.extractfile(item)
    if stream is None:
        raise OCIError(f"{label}: unreadable blob")
    try:
        actual, total = _stream_hash(stream)
    finally:
        stream.close()
    if actual != digest[7:] or total != size:
        raise OCIError(f"{label}: descriptor digest/size mismatch")
    return path, digest, total


def inspect_archive(
    path: Path,
    *,
    expected_archive_sha256: str | None = None,
    expected_manifest_digest: str | None = None,
    expected_platform: str | None = None,
) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise OCIError("archive is not a regular file")
    expected_sha = _hex(expected_archive_sha256, "expected archive sha256") if expected_archive_sha256 else None
    expected_manifest = _digest(expected_manifest_digest, "expected manifest digest") if expected_manifest_digest else None
    with path.open("rb") as f:
        archive_hash, archive_bytes = _stream_hash(f)
    if expected_sha is not None and archive_hash != expected_sha:
        raise OCIError("received archive SHA-256 differs from trusted expected bytes")

    try:
        with tarfile.open(path, "r:*") as tf:
            members = _members(tf)
            layout = _read_json(tf, members, "oci-layout")
            if layout.get("imageLayoutVersion") != "1.0.0":
                raise OCIError("unsupported OCI image-layout version")
            index = _read_json(tf, members, "index.json")
            manifests = index.get("manifests")
            if index.get("schemaVersion") != 2 or not isinstance(manifests, list) or len(manifests) != 1:
                raise OCIError("v0.1 requires a single-manifest OCI image index")
            index_descriptor = manifests[0]
            _, manifest_digest, verified_bytes = _descriptor(tf, members, index_descriptor, "image manifest", {MANIFEST_TYPE})
            if expected_manifest is not None and manifest_digest != expected_manifest:
                raise OCIError("image manifest digest differs from trusted expected digest")
            manifest = _read_json(tf, members, "blobs/sha256/" + manifest_digest[7:])
            if manifest.get("schemaVersion") != 2:
                raise OCIError("invalid OCI image manifest schemaVersion")
            _, config_digest, size = _descriptor(tf, members, manifest.get("config"), "config", {CONFIG_TYPE})
            verified_bytes += size
            config = _read_json(tf, members, "blobs/sha256/" + config_digest[7:])
            platform = f"{config.get('os')}/{config.get('architecture')}"
            if not isinstance(config.get("os"), str) or not isinstance(config.get("architecture"), str):
                raise OCIError("OCI config is missing platform identity")
            if expected_platform is not None and platform != expected_platform:
                raise OCIError("OCI platform differs from expected platform")
            index_platform = index_descriptor.get("platform")
            if isinstance(index_platform, dict) and (
                index_platform.get("os") != config.get("os")
                or index_platform.get("architecture") != config.get("architecture")
            ):
                raise OCIError("index and config platform disagree")
            layers = manifest.get("layers")
            rootfs = config.get("rootfs")
            if not isinstance(layers, list) or not isinstance(rootfs, dict) or rootfs.get("type") != "layers":
                raise OCIError("invalid OCI layer/rootfs metadata")
            diff_ids = rootfs.get("diff_ids")
            if not isinstance(diff_ids, list) or len(diff_ids) != len(layers):
                raise OCIError("config diff_ids do not match layer count")
            for i, diff in enumerate(diff_ids):
                _digest(diff, f"rootfs.diff_ids[{i}]")
            for i, layer in enumerate(layers):
                _, _, size = _descriptor(tf, members, layer, f"layer[{i}]", LAYER_TYPES)
                verified_bytes += size

            # Also reject damaged unreferenced blobs in the same layout.
            verified: set[str] = set()
            for name, item in members.items():
                if name.startswith("blobs/sha256/") and item.isfile():
                    suffix = name.split("/")[-1]
                    _hex(suffix, "blob filename")
                    if name in verified:
                        continue
                    stream = tf.extractfile(item)
                    if stream is None:
                        raise OCIError("unreadable additional blob")
                    try:
                        actual, total = _stream_hash(stream)
                    finally:
                        stream.close()
                    if actual != suffix or total != item.size:
                        raise OCIError("additional OCI blob digest mismatch")
                    verified.add(name)

            return {
                "schema": SCHEMA,
                "validation": "OCI_DESCRIPTOR_BYTES_VERIFIED",
                "archive": {"sha256": archive_hash, "bytes": archive_bytes},
                "image": {
                    "manifest_digest": manifest_digest,
                    "config_digest": config_digest,
                    "platform": platform,
                    "layers": len(layers),
                    "oci_blob_count": len(verified),
                    "referenced_bytes_verified": verified_bytes,
                    "uncompressed_layer_diff_ids_recomputed": False,
                },
                "expected": {
                    "archive_sha256": expected_sha,
                    "manifest_digest": expected_manifest,
                    "platform": expected_platform,
                },
                "not_proven": [
                    "SOURCE_AUTHENTICITY",
                    "UNCOMPRESSED_DIFF_ID_VERIFICATION",
                    "ACTUAL_IMAGE_RUNTIME",
                    "RECEIVER_IMPORT",
                    "PRODUCTION_ACCEPTANCE",
                ],
            }
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise OCIError("not a readable OCI image-layout tar archive") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["inspect", "verify"])
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-archive-sha256")
    parser.add_argument("--expected-manifest-digest")
    parser.add_argument("--expected-platform")
    parser.add_argument("--report", type=Path, help="Create a new machine-readable JSON receipt (will not overwrite)")
    args = parser.parse_args(argv)
    try:
        if args.action == "verify" and not (args.expected_archive_sha256 and args.expected_manifest_digest):
            raise OCIError("verify requires BOTH trusted expected archive SHA-256 and image manifest digest")
        receipt = inspect_archive(
            args.archive,
            expected_archive_sha256=args.expected_archive_sha256,
            expected_manifest_digest=args.expected_manifest_digest,
            expected_platform=args.expected_platform,
        )
        if args.report is not None:
            with args.report.open("x", encoding="utf-8") as f:
                json.dump(receipt, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write("\n")
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
        return 0
    except (OCIError, OSError) as exc:
        print(f"OCI_VERIFY_FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
