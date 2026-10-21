# ADR-0020 — Foreman 研究产物分类与非 GitHub 证据定位

- Status: Human decision frozen in [#173](https://github.com/youling/ai-use/issues/173); normative adoption pending exact-head review and merge
- Decision level: L2 cross-project durable-evidence / recovery contract
- Canonical event and location semantics: [Durable Trace — 研究产物分类与位置](../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md#研究产物分类与位置)
- Canonical role responsibility: [Foreman §2.2](../20_ROLES/FOREMAN.md#22-研究产物分类与位置责任)

## Why

Research outputs do not all have the same storage shape. Code, documentation, reports, and tests often have a suitable durable GitHub pointer. Important source material may instead be user/business evidence, raw research files, media, binaries, or large files that should not or cannot reasonably be uploaded to GitHub. If the latter are left only on a researcher's machine without a durable location pointer, later Agents may repeat expensive work or mistake an old path for currently available evidence.

Requiring every artifact to carry node/path metadata is also wrong: it duplicates GitHub facts and burdens tasks that have no local artifacts. The contract must make the Foreman classify the actual artifact rather than apply one universal form.

## Decision

1. Classification is per meaningful artifact, not just per Work. A Work can contain GitHub deliverables, non-GitHub source evidence, working snapshots, and derived outputs.
2. Exact GitHub repository/commit/PR/Issue pointers suffice when GitHub is the appropriate durable home. No duplicate node/path inventory is required.
3. Important artifacts retained outside GitHub must be locatable from the appropriate owner-controlled durable source. Record a stable node/asset identity when node-local, the execution namespace, exact path or CAS/object reference, persistence/cleanup risk, provenance, and integrity/availability/access details as applicable.
4. Original source, working snapshot, and derived output remain distinct. Before ephemeral workspace cleanup, preserve important evidence in an authorized durable location or explicitly state `LOCAL_ONLY` and the recovery risk.
5. If no meaningful durable artifact was produced, do not create empty inventories and use `NO_ARTIFACTS`. If deliverables are preserved only in GitHub, use `GITHUB_ONLY`; the two states are distinct.
6. Private user/business data and location details stay in the appropriate authorized owner source, not public ai-use. A deployment control plane may coordinate authorized cross-node retrieval, but connectivity or a known path does not grant data-access or transfer authority.
7. This decision extends the existing Durable Trace and Foreman contracts. It does not create a parallel artifact database, a new Work state machine, a universal storage service, or a requirement to copy data through the control plane.

## Alternatives considered

- **Record every output's node and path:** rejected because it duplicates GitHub facts and creates empty/low-value metadata for tasks without local artifacts.
- **Store all research files in GitHub:** rejected because private business evidence and large/raw files may have a different owner-controlled source and retention model.
- **Create a separate global artifact database:** rejected because it adds a second source of truth; current owner records and exact pointers are sufficient for the initial contract.
- **Assume a recorded path is always current:** rejected because nodes, mounts, containers, and ephemeral workspaces change or disappear.

## Counterexamples and compatibility

- A code-only PR with tests in GitHub is complete with exact GitHub pointers; it does not need a Windows node UID or local path.
- A reverse-engineering run produces a large raw database snapshot on a Windows host and a parser in GitHub. The snapshot needs an owner-private location/provenance pointer; the parser needs only its GitHub ref.
- A container path is deleted with an ephemeral workspace. The receipt must not imply current availability; important evidence must have been preserved or the result must disclose `LOCAL_ONLY` and the recovery risk.
- An Agent can reach a node through a tailnet but lacks the source owner's permission. It must not read or transfer the data until authorized.
- A task produces no local artifact. It must not invent a directory or generate a path inventory solely to satisfy the contract.

Existing CLAIM / CHECKPOINT / TERMINAL events remain valid. The new classification and location fields are conditional extensions; historical receipts are not retroactively invalidated or rewritten. Current availability must be live-verified when a later Work attempts retrieval.
