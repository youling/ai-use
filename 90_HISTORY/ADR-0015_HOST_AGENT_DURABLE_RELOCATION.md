# ADR-0015 — HOST_AGENT durable instance copy and autonomous Host-root relocation

- **Status:** Accepted bounded direction / materialization in #122
- **Issue:** `youling/ai-use#122`
- **Decision level:** L2
- **Supersedes in part:** `ADR-0010_HUMAN_HOST_ENVIRONMENT.md` only where it denied relocation authority after material storage drift
- **Public semantic owner:** `30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md`
- **Private instance owner:** deployment-local resolved Host instance owner

## Context

[HOST_AGENT contract](../50_TEMPLATES/HOST_AGENT_CONTRACT.md) was introduced as the stable Agent discovery surface for a Human Host: semantic layout is standardized, physical placement is resolved from the current Host rather than copied from another machine.

Human has now clarified two missing long-term semantics:

1. The local Documents HOST_AGENT materialization is not the only durable copy. Private Human Host instances need a GitHub-native durable canonical copy so a lost/rebuilt local Host can restore its Agent collaboration context.
2. Storage placement is not static. When storage topology or capacity materially changes, an Agent should be able to re-resolve and relocate the Host-managed directories it owns instead of stopping for ceremonial approval.

Without these rules, a Host rebuild can lose its resolved projection, while storage drift can leave Agents bound to obsolete paths even though the system already has enough evidence to repair itself.

## Decision

### Durable copy

For Human Host private deployments:

```text
deployment-local private instance artifact
  = durable canonical resolved HOST_AGENT copy / recovery source

<OS-native Documents>/<HOST_AGENT materialization>
  = local materialized discovery copy
```

`ai-use` continues to own the portable semantics/template. The platform/profile owner owns desired profile/scanner/reconcile implementation; the asset owner owns stable physical asset facts; the deployment-local private instance owner owns per-Host resolved instance state/evidence and the durable canonical HOST_AGENT copy.

The canonical ai-hub artifact contains only Agent-facing resolved context and references allowed by the Human Host contract. Raw secret values remain outside it.

### Probe-driven placement

Physical paths remain Host-local decisions. An Agent should inspect current storage topology, filesystem, device class, free-space pressure, IO/locality, container/runtime storage and Host role before resolving roots.

Fixed drive letters or paths are never portable policy.

### Autonomous relocation authority

Human delegates autonomous relocation authority for directories explicitly classified as:

```text
owner = HOST_MANAGED
relocatable = true
```

Material relocation triggers include:

- new/removable/replaced storage that materially improves placement;
- current volume reaching material capacity pressure;
- filesystem/locality/runtime-storage constraints changing;
- a resolved root becoming missing, unwritable or materially unsuitable;
- another evidenced correctness/performance/failure-domain reason.

Within this class, the Agent does not need a ceremonial Human gate merely because bytes move between Host-owned locations.

### Relocation lifecycle

Autonomous relocation must be transactional and evidence-bound:

```text
PROBE current Host
 -> CLASSIFY trigger and ownership
 -> RESOLVE target
 -> PRESERVE/QUIESCE affected writer where required
 -> COPY/MOVE owned data
 -> VERIFY bytes/structure/consumer readiness
 -> SWITCH active mapping
 -> UPDATE deployment-local canonical HOST_AGENT
 -> RE-MATERIALIZE local Documents HOST_AGENT
 -> VERIFY fresh Agent discovery/currentness
 -> GC old location only after no-unique-state proof
```

At no point may the Agent leave the durable canonical projection pointing to an unverified target and then delete the only working copy.

### Default exclusions

Autonomous Host-root relocation does not, by default, include:

- raw Secrets or secret-store custody;
- device identity / machine trust roots;
- Human-unique files/data not explicitly classified Host-managed;
- vendor-owned state that has its own migration contract;
- UNKNOWN ownership;
- dirty/unpushed unique Work;
- externally destructive storage operations such as repartition/format/RAID change.

Such cases remain fail-closed or require the canonical owner/current Human authority.

## Compatibility

ADR-0010 remains valid for semantic standardization, probe-driven physical placement, seven-domain classification and HOST_AGENT discovery.

The older generic rule:

> hardware/storage change grants re-evaluation but not relocation authority

is superseded for explicit `HOST_MANAGED + relocatable=true` roots by this ADR. It remains valid for excluded/unknown classes.

Existing Host projections do not become relocatable merely because they have a path. The owner/classification must be explicit or safely derivable from the current canonical contract.

## Counterexample

A new NVMe is added while the existing Agent cache/workspace volume is nearly full. The Agent sees the new disk and immediately moves a vendor credential store and an unknown local database, then deletes the originals before updating HOST_AGENT.

Under this decision the action is rejected: cache/workspace may be eligible only if classified Host-managed/relocatable; credential/vendor/unknown state is excluded. Eligible roots follow copy/verify/switch/writeback/GC ordering.

## Consequences

Benefits:
- Human Hosts can reconstruct local Agent context from GitHub durable state;
- storage changes can self-heal without repeated Human path decisions;
- physical layout remains adaptive while semantic layout stays stable;
- fresh Agents read one current projection instead of rediscovering historical placement from chat.

Costs:
- deployment-local private instance artifacts must be kept current after migrations;
- relocation implementation needs ownership/currentness/verification/rollback checks;
- not every directory can be treated as movable just because it is listed in HOST_AGENT.