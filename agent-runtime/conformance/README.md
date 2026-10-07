# Public conformance

`pytest` covers synthetic projection expiry/scope/atomic replacement, Git helper
target guards/no-store, Host context/mount guards, Work/write-set guards, fresh
recovery and release/update/rollback compatibility. Fixtures use owner/repo and
synthetic credentials; no private instance data or model inference.

The recovery fixture runs real Git against a local bare remote and a file-backed
fake Issue service. A writes an exact allowlisted artifact/checkpoint, refreshes
the synthetic credential generation and exits. Fresh B uses separate empty runtime
storage, reads durable checkpoint/ref and deletes only its owned branch after
readback. It tests the real recovery client with transport substitution; it is not
proof of authenticated private GitHub capability or model/native hierarchy.

Public Ubuntu CI also builds amd64 image, verifies non-root/version/tools, scans
exported layers/history/config and copied source, checks licenses/provenance,
exports package manifest and checks update/rollback semantics. No package push.
No-secret scans are bounded heuristic defenses plus explicit build-context allowlist;
they do not replace custody/semantic review. Exact-head CI and Architect review
remain distinct acceptance gates.
