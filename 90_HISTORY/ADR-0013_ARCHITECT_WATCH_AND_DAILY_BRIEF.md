# ADR-0013 — Architect Watch / Daily Brief 是 durable reconciliation 的派生能力

- **Status:** Accepted
- **Issue:** `youling/ai-use#91`
- **Decision level:** L2
- **Canonical behavior owner:** `docs/AGENT_INTERFACE.md §1.4.3`
- **Guidance:** `40_GUIDES/ARCHITECT_WATCH_AND_BRIEF.md`

## Context

Human、AI 会话与执行环境都可能中断。已有 durable Work、Dispatch、CLAIM/CHECKPOINT/TERMINAL 与 recovery 语义足以恢复工作，但如果 Architect 只在 Human 发消息时才重新观察，Human 会退化成 scheduling clock 和状态搬运者。

同时，新增一个“Watch 状态机/数据库/常驻 Architect”会复制 Work truth 并制造新的失效面。

## Decision

Watch 被定义为可选的周期/条件 wake：

```text
WAKE -> live durable reconciliation -> derived health -> authorized action or exit
```

scheduler/event 只提供 wake capability，不提供 authority。每轮从 current Git/GitHub durable source 重建，不依赖 scheduler-local memory。

Health labels 是 derived read model，不是 Work state。deployment 可配置 stale/pickup threshold；超时只产生 SUSPECT/UNKNOWN，不自动 failure、takeover 或取消 ownership。

Daily Brief 是同一 durable facts 的 Human-facing derived memory projection；可用于恢复注意力，但不能驱动 mutation，除非 exact Work 已重新 live validate。

## Existing semantic owners

- Work / execution / continuation：Agent Interface；
- CLAIM/CHECKPOINT/TERMINAL event shape：Durable Trace；
- recovery/takeover：Recovery & Handoff；
- scheduler/cadence/notifications/task IDs：deployment control plane。

不修改 Durable Trace event schema，不新增 public scheduler、liveness registry、task DB 或 mandatory always-on session。

## Consequences

收益：Human 不再承担例行轮询；Architect 可在 provider/session中断后从 durable state 重建；日报帮助多日中断后快速恢复。

代价：deployment 必须管理自己的 wake 机制和阈值；brief/health 都可能 stale，因此每次 effectful action 前仍需 currentness gate。

```text
WATCH = RECONCILIATION_LOOP
BRIEF = DERIVED
CAPABILITY != AUTHORITY
```
