# ADR-0022 — Domain-neutral OCI Artifact Supply belongs to ai-use

- **Status:** Human decision recorded in [#181](https://github.com/youling/ai-use/issues/181); normative contract/implementation pending exact-head review and merge
- **Decision class:** L2 public cross-domain capability ownership / delivery-contract seam
- **Current canonical home (candidate):** [capabilities/oci/CONTRACT.md](../capabilities/oci/CONTRACT.md)
- **Prior accepted related ADR:** [ADR-0016 public Agent Runtime](ADR-0016_PUBLIC_AGENT_RUNTIME.md)
- **Decision date:** 2026-11-06

## Problem

An internal Host/Fleet experiment with Windows/WSL2 OCI building, immutable archive verification, authorized offline transfer, Linux rootless receipt, snapshot-aware recovery and mount-UID testing produced methods applicable to ordinary business container images as well as AI Agent images. Treating all of this as a Fleet-only feature forces new businesses and non-Fleet consumers to borrow private node APIs or duplicate implementation.

However, the existing public `agent-runtime/` is already the canonical owner of *Agent-specific* reference images, image conformance and separately controlled release. Moving all instance-specific Fleet code or introducing another release authority would instead create an overlapping owner and a large runtime dependency.

## Decision

1. Establish a **public, consumer-neutral OCI artifact supply capability** in `ai-use/capabilities/oci/`. It owns the generic stages, exact source/digest/receipt contracts, read-only archive validation tools, reusable examples and optional transport/build adapter interfaces.
2. Keep `agent-runtime/` as an optional *consumer*, owning its OpenCode (and future Agent) Dockerfile, model/tool conformance, scoped credentials and publish/rollback gate. Its existing ADR-0016 and publication workflow remain authoritative.
3. Keep actual business image recipes, integration/rollback acceptance, artifact storage, host/runtime credentials, disk paths, identity mapping, network transport configuration and remote effects with their project/instance owners. Fleet is one possible adapter, not the default prerequisite.
4. Use OCI image-spec descriptors, image layout and established build/container/transport tools. Do not reinvent image layers, crypto, containerd, authenticated SSH or an artifact registry.
5. Begin with a public read-only, stdlib single-image OCI archive verification subset and executable Windows/Linux CI. Expand build/export/transfer/import/resume adapters only with separate real non-Fleet canaries and behavior parity; retain donor evidence until review. Public synthetic CI does **not** make another Host production-ready.
6. Keep Build, real image smoke, export, archive integrity, trusted expected digests, receiver import, unpack, runtime acceptance and production promotion as distinct proofs. Unknown/timed-out side effects require reconciliation, not unconditional replay; image manifest digest differs from archive SHA-256/config ID/layer diffID.
7. Do not imply real secret custody from image no-secret scans. Private data cannot be copied into public source merely because it inspired the generic capability.

## Alternatives rejected

- **Leave the method only in private ai-hub/Fleet:** consumers outside Fleet must recreate common code/docs or gain a private control-plane dependency; rejected by explicit Human ruling.
- **Move all private FOK donor sources unmodified into ai-use:** imports node UID/SSH policy, private identity, specific OpenCode image/pins and source-specific constraints; exceeds generic contract and could violate source handling.
- **Put all new capability under agent-runtime:** this incorrectly makes business/services a subcategory of Agent-specific images; instead provide a sibling generic toolkit with a precise consumer pointer.
- **Require GHCR or Fleet to transfer OCI artifacts:** clashes with offline/intranet/air-gapped/no-registry needs. Existing release workflow remains an optional, separately controlled consumer.
- **Brand a shell tutorial as a mature product without executable checks:** documentation alone cannot demonstrate tamper detection or portability.

## Compatibility, falsifiers and rollout

This additive namespace does not rewrite accepted Agent Runtime source, old Fleet Host Work/receipts or existing image IDs. An ordinary user with a Dockerfile and OCI-compatible build engine should be able to follow the process without Fleet access. A synthetic malformed OCI tar must fail; a correct OCI tar with wrong expected SHA must fail; pure Docker legacy archive cannot be treated as validated OCI layout. A different tar packaging with the same image manifest must still have its own outer-file hash. An image that passes archive validation but has never started must not be labeled runtime PASS.

**Rollout path:** publish reviewed v0.1 generic verifier and docs → validate on independent non-Fleet business canary → extract generic build/distribution code from donor behind portable adapters as required → bind consumer versions → retire private duplicate code only after owner parity/rollback acceptance.

No authority to auto-deploy, move business data, copy credentials, mutate another project's state or merge a PR is created by this ADR.
