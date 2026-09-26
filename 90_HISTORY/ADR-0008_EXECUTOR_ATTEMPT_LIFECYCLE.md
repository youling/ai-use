# ADR-0008：Observable Executor Attempt Lifecycle

**Artifact Version: 1.0.0**
状态：Decision materialization；acceptance/currentness 以 Git/GitHub exact-head Review + merge history 为准
裁决来源：[Governance #94](https://github.com/youling/ai-use/issues/94)
语义 owner：[Agent Interface](../docs/AGENT_INTERFACE.md) + [Durable Trace Principle](../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md)

## Context

ai-use 已经把 Git/GitHub 作为 durable truth，并要求具有事实价值的行为留下 durable trace；但 delegated executor 的“开始”和“结束”此前没有最小、对称、机器可观察的 attempt lifecycle。

结果是：executor 可能已经施工，却只在聊天中自述完成；也可能网络、provider、token、节点或会话中断后直接消失。Human / parent Architect 随后不得不人工搬运消息或凭记忆猜测施工状态。

这与 ai-use 的故障模型冲突：Human、AI/session、执行环境都被视为可能失败，系统必须能从 durable state 判断“是否接手、做到哪里、是否闭合”。

## Decision

Delegated execution attempt 固化为：

```text
DISPATCH
 -> AGENT_CLAIMED
 -> [PROGRESS_CHECKPOINT]*
 -> AGENT_TERMINAL_RESULT
```

1. **CLAIM 是 attempt-start evidence。** Bootstrap / execution gate 通过后、material execution 前写入 exact Work coordinate，并 readback 确认。
2. **CHECKPOINT 仍是语义阶段事件。** 短任务可以没有 checkpoint；禁止 heartbeat 化。
3. **TERMINAL 是 attempt-close evidence。** SUCCESS、NEGATIVE_RESULT、PARTIAL、BLOCKED、HUMAN_REQUIRED、FAILED、CANCELLED 都必须走同一 durable closeout；TERMINAL 必须精确引用它关闭的 CLAIM pointer，写入后必须 readback 确认。
4. **Attempt lifecycle 与 Work lifecycle 分离。** TERMINAL 关闭一次 executor attempt，不自动关闭 Work，不替代 Architect Review、merge 或 deploy gate。
5. **Completion 必须绑定 durable closeout。** `WRITEBACK_ATTEMPTED != DURABLE_WRITEBACK_CONFIRMED`；适用 delegated execution 在 terminal writeback 未确认前不能声称 `COMPLETION_REACHED`。
6. **Terminal transport 只返回 pointer。** durable terminal result 确认后，delegated executor 对 caller/Human 的最终返回只包含 exact GitHub pointer，不复制 summary。父 Architect live-read pointer/current Work 后再消费。
7. **没有 durable write path 的 subagent 不能关闭 Work。** 它只能返回有界 evidence 给 primary/orchestrator；后者负责验证、综合与 durable writeback。

## Why this shape

只要求 CLAIM + TERMINAL 两个端点，可以获得最小充分可观察性：

- 没有 CLAIM：没有 durable evidence 证明 executor 已开始；
- 有 CLAIM、无 TERMINAL：执行可能仍在进行，或已经进入 suspect/recovery candidate；
- 有 TERMINAL：本 attempt 已 durable 闭合，结果可由其它 Agent/Human 重新读取。

TERMINAL 直接引用 exact CLAIM pointer，不另造 attempt-ID registry；GitHub durable pointer 本身就是 attempt correlation key。中间 checkpoint 保持可选，避免把协议变成高频 heartbeat 或日志系统。

Pointer-only terminal return 同时把“有没有正确回写”变成可机械观察的 transport property：没有 pointer、pointer 无效或 pointer 指向不匹配 terminal event 都是显式 drift，而不是自然语言猜测。

## Alternatives and tradeoffs

### 只要求最终报告

无法区分“根本没开工”和“开工后异常消失”，也无法为 Architect Watch 提供 pickup/active/suspect 判别；不采用。

### 高频 heartbeat

能够提高在线感知，但制造噪声、状态重复和额外 GitHub 写入，且 heartbeat 不能证明有 meaningful progress；不采用。

### 把 executor 状态放进新的 scheduler/task DB

会制造第二 SSOT，并让恢复依赖 control-plane-local state；不采用。GitHub durable events 是 canonical evidence，scheduler 只能派生观察。

### terminal 聊天同时复制完整总结

人类可读性更高，但重新引入聊天作为事实搬运层，也让“是否完成 durable writeback”难以从 terminal transport 机械判断；不采用。详细结果留在 GitHub，Human/Architect 可按需读取。

## Compatibility

- 不修改 L0。
- 不改变 Work Order acceptance 的 semantic owner。
- 不改变 Architect Review / merge / deploy authority。
- `PROGRESS_CHECKPOINT` 继续有效，只从“唯一可恢复阶段事件”变成 CLAIM/TERMINAL 之间的可选阶段事件。
- 历史 executor report / completion artifact 保持 provenance 有效；新 delegated attempts 使用新 lifecycle。
- deployment 可以在此基础上派生 stale/suspect/recovery policy，但不能把 scheduler-local observation 升级为 durable truth。
