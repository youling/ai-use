# Durable Data Doctrine v0.1

> **L2 Targeted Reference** — not default reading. Trigger: durable business data / data model / schema migration / state lifecycle questions.
> This document defines general principles for durable data handling across projects. It does not规定具体数据库产品或平台。
> Source issue: `youling/ai-hub#58`

---

## 1. Identity

**Stable identity is the foundation of deduplication, merge, and cross-system correlation.**

- Every entity that may be referenced across time, systems, or sessions must have a **stable identity key** — not a display name, not a generated UUID that changes on re-creation.
- Identity keys must be **opaque, versioned, and scoped** to their merge boundary (e.g. project-scope, system-scope, cross-system-scope).
- Display names, labels, and human-readable descriptions are **presentation-layer** concerns and must never serve as the canonical identity key for deduplication or merge decisions.
- When two systems each assign identity to the same real-world entity, the merge boundary and conflict resolution strategy must be declared explicitly — not assumed.

**Anti-pattern:** Using user-chosen display names as primary keys; re-generating identity on each import; treating "same name" as "same entity."

---

## 2. Semantics

**Every field, record, and state must have a precise, documented meaning.**

- Field definitions must specify: type, unit, allowed values, null semantics, and default behavior.
- `unknown` ≠ `absent` ≠ `not-applicable` ≠ `null` ≠ `""` — each represents a different semantic state and must not be collapsed into a single sentinel value.
- State machines must have declared states, transitions, and terminal conditions. Implicit states ("we don't call it anything but it exists") are forbidden.
- When a field's meaning evolves across versions, the old meaning must be preserved in historical records — do not retroactively reinterpret old data under new definitions.

**Anti-pattern:** Using `null` to mean both "not yet set" and "explicitly not applicable"; treating empty string as missing data; undocumented enum values.

---

## 3. Provenance

**Every piece of durable data must carry evidence of where it came from and when it was observed.**

- Key metadata: source system, observation time (or version/evidence snapshot time), transformation steps if derived.
- Provenance is **append-only** — once recorded, the observation fact cannot be changed, only supplemented with corrections or newer observations.
- Critical derivations (computed fields, aggregated metrics, imported records) must be traceable to their source records through a declared derivation chain.
- "I don't know where this came from" is a data quality incident, not an acceptable steady state.

**Anti-pattern:** Backfilling observation timestamps; losing source references after ETL; storing derived values without recording the derivation.

---

## 4. Immutability

**Distinguish between what can be overwritten and what must be preserved.**

- **Append-only / versioned history**: audit logs, event streams, evidence records, signed facts. These are never overwritten — corrections are new entries that reference the originals.
- **Current state**: the latest snapshot of mutable state (e.g. "user's current address", "project's current status"). These are overwritten by design, but each overwrite should produce a new history entry.
- **Ephemeral state**: caches, indexes, materialized views, embeddings, temporary computation results. These can be rebuilt from durable sources and are explicitly not authoritative.

The boundary between "current state" and "history" must be declared per entity type, not left implicit.

**Anti-pattern:** Storing only the latest value with no history; treating a materialized view as the source of truth; silently deleting audit records.

---

## 5. Derivation

**Canonical/source data and derived/rebuildable data must be explicitly separated.**

- **Canonical source**: the authoritative record for a fact. One fact, one canonical source (within its merge boundary).
- **Derived data**: any value computed from canonical sources — caches, search indexes, embeddings, aggregated reports, materialized views, denormalized projections.
- Derived data must be **labeled as such** and must never be silently promoted to canonical status. If a derived view becomes the only way to access a fact, that fact needs a canonical source.
- Rebuildability must be declared: can this derived data be fully reconstructed from canonical sources? If not, it has implicitly become canonical.

**Anti-pattern:** Treating a search index as the only source of truth; promoting a cache to canonical without declaring the change; "we can't rebuild it so we keep it" without reclassifying.

---

## 6. Retention

**Retention must be a deliberate policy, not a side effect of "afraid to delete."**

- Every data category should declare its retention class:
  - **Permanent**: regulatory, legal, or architectural requirement to preserve indefinitely (e.g. signed contracts, audit trails).
  - **Long-term compressible**: valuable for historical analysis but can be summarized or compressed after a retention period.
  - **Short-term**: operational need only (e.g. debug logs, temporary processing state); auto-expire after declared TTL.
  - **Rebuildable**: can be fully reconstructed from canonical sources; no independent retention needed (e.g. search indexes, caches).
- "We might need it someday" is not a retention policy. If the cost of retention exceeds the expected value of eventual access, the default is short-term or rebuildable.
- Retention policies must be declared per data category, not globally applied.

**Anti-pattern:** "Keep everything forever just in case"; mixing retention classes in the same store without distinction; no TTL on operational logs.

---

## 7. Migration

**Schema, version, and storage changes must be explainable, testable, and reversible where possible.**

- Every schema change must declare: what changed, backward/forward compatibility guarantees, required conversion steps, and rollback path.
- Storage engine changes (e.g. switching from one database to another) do **not** change data semantics — semantics are defined by the doctrine, not by the storage implementation.
- Migration scripts must be:
  - **Testable**: verifiable against a representative dataset before production execution.
  - **Idempotent**: safe to re-run without side effects.
  - **Auditable**: logged with timestamp, executor, before/after state summary.
- When a migration changes semantics (not just storage), it must be versioned as a semantic migration with explicit conversion/rollback and stakeholder notification.

**Anti-pattern:** Schema changes without rollback path; "we migrated but didn't test the old query paths"; storage engine migration that silently changes query semantics.

---

## Scope boundaries

### What this document covers

General principles for handling durable data across any project in the system. Applies to: business databases, object storage, durable business stores, and any data that must survive beyond a single session or workspace.

### What this document does not cover (v0.1)

- Specific database product selection or configuration.
- Complete data governance platform design.
- Privacy & secrets management (future extension).
- Data deletion / right-to-erasure policies (future extension).
- Cross-system data synchronization protocols.
- Real-time streaming or event sourcing patterns.

### Relationship to other documents

- This document is an **L2 targeted reference** — not default reading for all agents.
- For session/context lifecycle, see `docs/SESSION_LIFECYCLE.md`.
- For governance authority hierarchy, see `CONSTITUTION.md`.
- For agent bootstrap rules, see `AGENTS.md`.
- Project-specific data contracts remain in project-local repositories; this document does not override them.
