# 90_HISTORY

历史层：历史、案例、rationale、ADR。

默认不进入 Agent 上下文（L3）；如需了解长期裁决为什么形成，再按需读取。

当前 ADR：

- [`ADR-0001_DOCS_AS_CODE_CHANGE_LIFECYCLE.md`](ADR-0001_DOCS_AS_CODE_CHANGE_LIFECYCLE.md) — 关键文档采用 docs-as-code，低关键文档允许周期性维护。
- [`ADR-0002_CONTEXT_LIFECYCLE_V0_1.md`](ADR-0002_CONTEXT_LIFECYCLE_V0_1.md) — Context Lifecycle v0.1：Work Context 执行连续性（#60）。

- [ADR-0003](ADR-0003_STAGE_AWARE_REUSE.md) — Stage-aware Reuse。
- [ADR-0004](ADR-0004_RECOVERY_ROUTING_SINGLE_SOURCE.md) — 恢复语义与路由单一来源（已 exact-head Review 接受）。
- [ADR-0005](ADR-0005_OWNER_NATIVE_DERIVATION.md) — Owner / instance、GitHub Native First 与派生解释边界（已 exact-head Review 接受）。
- [ADR-0006](ADR-0006_GITHUB_CAPABILITY_LAB.md) — GitHub Capability Lab evidence、fixture safety、currentness 与 owner-local adoption delta（已 exact-head Review 接受）。
- [ADR-0007](ADR-0007_ACTIONS_RESOURCE_BUDGET.md) — GitHub Actions visibility / runner / budget-aware 使用策略（#89）。
- [ADR-0008](ADR-0008_EXECUTOR_ATTEMPT_LIFECYCLE.md) — Delegated executor 的 `DISPATCH → CLAIM → [CHECKPOINT]* → TERMINAL` 可观察 attempt lifecycle（#94）。
- [ADR-0009](ADR-0009_CONSTITUTIONAL_SEMANTIC_INTEGRITY.md) — Material governance L2 exact-head Review 的最小 semantic proof obligations（#96）。
- [ADR-0010](ADR-0010_HUMAN_HOST_ENVIRONMENT.md) — Human Host Environment：语义标准、现场解析与 **HOST_AGENT.md** 稳定发现（#107）。
- [ADR-0011](ADR-0011_ADAPTIVE_REASONING_EFFORT.md) — Adaptive Reasoning Effort：Fresh/takeover 深推理、稳态巡航、证据触发升级与 durable closure 后降档（#113）。
- [ADR-0012](ADR-0012_ARCHITECT_CONSTRAINT_CHALLENGE.md) — Architect Constraint Challenge：反盲从约束、owner-aware challenge/amend 与 currentness-before-wait（#106）。
- [ADR-0013](ADR-0013_ARCHITECT_WATCH_AND_DAILY_BRIEF.md) — Architect Watch / Daily Brief：周期唤醒只做 durable reconciliation；健康分类与日报是派生投影，不建立第二 lifecycle/authority（#91）。
- [ADR-0014](ADR-0014_HUMAN_SSOT_DEPOSITOR_INGRESS.md) — Human SSOT Depositor：post-hoc source-bound create-only capture，与 Curator 读取/维护 current Human state 分权（#38）。
- [ADR-0015](ADR-0015_HOST_AGENT_DURABLE_RELOCATION.md) — HOST_AGENT durable instance recovery copy + bounded autonomous relocation for explicit Host-managed relocatable roots（#122）。

退休入口的历史原文通过 [Session compatibility](../docs/SESSION_LIFECYCLE.md)、[provider guide forward](../docs/DeepSeekPP-github-mcp-usage.md) 的 frozen Git pointers 追溯；默认不读取历史全文。
