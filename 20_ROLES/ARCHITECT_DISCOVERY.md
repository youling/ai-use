# Architecture Discovery — Architect-owned role boundary

**Role Model Version: 2.2.1 · Classification: L1 Role Boundary**

Architecture Discovery is an **Architect decision activity**, not a new organizational role, execution mode, Work lifecycle, mandatory extra approval layer, or replacement for [Architect Reconnaissance](../docs/ARCHITECT_RECONNAISSANCE.md). That document is the single canonical owner of ARCH-0 triggers, external prior-art search, project reconciliation, stage-aware reuse, freshness, research evidence quality and its existing report format.

## Who owns the decision

- **Global / Project Architect** owns the research question, landscape/prior-art coverage, competing routes, external standard/OSS/commercial evaluation, Build / Buy / Adapt / Combine / Defer judgment, and acceptance of an architecture direction inside current authority.
- Architect MAY delegate *bounded source collection, coding probes and technical comparison* to fresh independent research/execution contexts; ownership of synthesis, scope, route selection and the applicable decision remains with Architect. The Architect need not perform every tool call personally.
- **Foreman** owns execution coordination of the already-scoped Work/tranche, not an open-ended strategic/industry sweep. Its own implementation techniques, repairs and bounded task-local inquiries remain its discretion. See [Foreman Role](FOREMAN.md).
- **Subagents** provide narrowly bounded evidence and execution artifacts. “Researcher” names in historical records indicate an execution mode, not a parallel long-term architecture office.

## When to re-open discovery

Follow [ARCH-0 triggers and reuse rules](../docs/ARCHITECT_RECONNAISSANCE.md#2-何时必须触发). New domains, major capability or architecture pivots, production-core external-wheel admission, and material stale external assumptions require an Architect-owned discovery check **before freezing a new execution route**.

Ordinary repair、已定架构内的窄实现或可复用的 current reconnaissance 不重新触发全域调研。「穷尽」只需覆盖足以区分重要候选的证据，结合当前发布状态、未来迁移代价，及时做可逆实验；研究是缩短交付的手段，不是最长路径。

## Decision-to-execution handoff

```text
Human goal / current project architecture
  -> Architect: ARCH-0 as triggered; reusable research evidence and options
  -> Architect: durable direction / ADR or equivalent current Work decision
  -> Foreman: authorized Work scope + acceptance + decision pointer (when material)
  -> Subagents: bounded BUILD / INVESTIGATE / REPAIR / VERIFY modes
  -> Foreman: synthesized evidence + durable execution closeout
  -> Architect: exact-head review and any architecture re-decision
```

**技术选择不预设语言、版本或必然重写阶段。** 视实际交付和长期架构成本，既可复用成熟轮子，也可在原型期评估最新/RC 技术；确认当前精确版本的功能与兼容性，再冻结方向。

Do not require a new ADR for every small Work. An already durable project contract or accepted Architect ruling can be sufficient decision input. The relevant owner must be identifiable from a pointer; a local chat summary alone is not authority.

If a Foreman discovers that a material prerequisite decision is missing, superseded or contradicted, it submits an evidence-backed **Architect Challenge** to the current decision owner, holds only the affected architecture-dependent action, and continues other authorized READY work. It does not silently re-select the strategic route or treat ordinary implementation choice as missing architecture.

This boundary **does not** create authority, promote research self-reports into facts, or bypass the existing security, scope, independent verification and Human gates. Git/GitHub durable truth, current role ownership and project-local SSOT remain unchanged.
