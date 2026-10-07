# ADR-0016 — Public Agent Runtime ownership and release lifecycle

- Status: Accepted implementation at PR #124 exact head `f8a4a873933e8b0e8e36d2c82cc7ecd480eeecfa`; merged as `45de55617f1921055aef660c13310650eb15625a`; first OCI publication remains separately gated
- Decision level: L2
- Canonical implementation: [agent-runtime](../agent-runtime/README.md)
- Does not supersede common HOST_AGENT schema or private instance ownership.

## Context and decision

Generic Foreman recipes and seams must be usable without private deployment access.
Keep one public owner for image/source, portable contract, conformance and OCI
distribution. Deployment systems consume immutable releases; exact Host instance
facts and credential references stay with their private owner. Original donor
history is preserved in the migration ledger; acceptance of donor heads does not
automatically accept adapted public artifacts.

Use separate images for separate runtimes. OpenCode is the first reference:
Linux-native workspace, non-root execution, bounded Host projections and direct
GitHub recovery. Host lifecycle/resource management remains platform native. A
production broker may be optional for exceptional privilege but is not baseline.

GitHub credential capability is separate from Work/governance authority. Missing,
expired, wrong-scope, partial context or unknown mutation outcome fails closed;
live durable reconciliation precedes retry. Session state is disposable.

## Lifecycle and tradeoff

An upstream observation creates a proposal, never automatic promotion. Exact source
and base digests plus signed package snapshot form candidate inputs. Public
conformance and optional privately owned real-consumer canary precede acceptance.
Separately authorized candidate publication returns an OCI manifest digest;
stable promotion binds that digest and reviewed source. Previous digest remains
available for rollback. Floating tags are convenience views, never Host truth.

Use standard public GitHub-hosted CI and GHCR as the first distribution surface.
Provider economics are current terms, not an invariant; recipe/tests are portable.
Initial amd64 only avoids unsupported multi-arch claims. Root key custody and
provider auth are not standardized into a new global credential store.

The publish workflow is disabled by default and requires a reviewed authorization
file on the current default branch, a matching exact revision, a successful
conformance run and an independently configured protected environment. Workflow
implementation does not confer release authority. Package visibility/linkage and
anonymous digest readback must be verified during separately authorized first
release; there is no claimed public package yet.

## Compatibility and failure closure

Public fixture success proves portable invariants, not authenticated private-host
success. Common HOST_AGENT V1 remains consumed, not redefined. Consumers can keep
their accepted donor digest until a new public release is accepted. Duplicate
generic donor source retires only through a reviewed consumer pointer transition
after migration acceptance. No donor head is rewritten or merged for convenience.

Counterexample: a token permits package/branch writes but Work grants only test
execution. Credential success creates no publish/merge authority; disabled release
workflow and required authorization/protection prevent automatic publication.
