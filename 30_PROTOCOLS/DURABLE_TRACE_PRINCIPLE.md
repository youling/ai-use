# Durable Trace Principle

**Classification: L2 Targeted Reference.**

## 目的

任何**具有事实价值的 Agent 行为**必须留下 durable artifact，以便未来恢复、核验与交接。
聊天输出不是事实源；只有落盘到 durable source（Git / GitHub / durable docs / 当前 authority
issue）才算留下 trace。

本原则采用**阶段性 checkpoint**，不再把任务最终报告当成唯一 durable write 时点。AI provider
限流/冷却、网络中断、宿主机死机、会话强制截断都属于常态故障模型；目标是让 fresh/resume
Agent 从最近一次 durable checkpoint 恢复，最大返工不超过“当前尚未 checkpoint 的阶段”。

## 必须留下 trace 的行为

- **决策**（architecture / authority / scope 相关决策）
- **修改**（文件、配置、代码的改动）
- **验证**（tests / build / diff / exact-head 等验证结果）
- **状态变化**（task state transitions、release decisions）
- **风险判断**（blocking conditions、已知风险、未覆盖区域）

## Delegated execution attempt events

Delegated execution 的最小 durable lifecycle 为：

```text
DISPATCH -> AGENT_CLAIMED -> [PROGRESS_CHECKPOINT]* -> AGENT_TERMINAL_RESULT
```

本节拥有 CLAIM / TERMINAL 的 durable event shape；completion / terminal-return 语义由 [Agent Interface §1.8](../docs/AGENT_INTERFACE.md#18-completion-boundarydurable-acceptance--terminal-writeback) 拥有。

### `AGENT_CLAIMED`

```text
AGENT_CLAIMED
---
work: <owner/repo#issue@step>
dispatch: <exact durable dispatch pointer>
executor: <identity/session class>
startup_mode: <mode>
node: <only when materially relevant>
status: CLAIMED
```

规则：

- Bootstrap / execution gate 通过后、material execution 开始前立即写入 exact Work coordinate；
- 必须从 durable source readback 确认存在；
- 不复制 scope / acceptance / Work Order 正文；
- 不产生 authority，不迁移 Work 状态；
- 没有 CLAIM，只能说明缺少“该 attempt 已开始”的 durable evidence。

### `AGENT_TERMINAL_RESULT`

```text
AGENT_TERMINAL_RESULT
---
work: <owner/repo#issue@step>
result: SUCCESS | NEGATIVE_RESULT | PARTIAL | BLOCKED | HUMAN_REQUIRED | FAILED
remote_head: <sha | none>
durable_refs: <PR / commit / report / artifact pointers, or none>
verification: <summary>
remaining: <none | exact remaining>
blockers: <none | exact blocker>
next: <single next action>
```

规则：

- 每个已 CLAIM 的 delegated attempt 在正常可写回的终止路径上都必须产生 terminal result，成功与失败没有例外；
- 写回 exact Work coordinate 后必须 readback / 等价 durable read 确认，`WRITEBACK_ATTEMPTED != DURABLE_WRITEBACK_CONFIRMED`；
- terminal result 关闭 execution attempt，不自动关闭 Work Order，不替代 Architect Review / merge / deploy gate；
- terminal 详细事实留在 durable source，不依赖聊天 self-report；
- 没有 authorized durable write path 的 subagent 不得假装产生 terminal event，由 primary/orchestrator 承担最终 durable writeback。

## 阶段性 checkpoint

Checkpoint 是**语义阶段边界**，不是定时 heartbeat。至少在以下时点写回当前 durable source：

1. 研究 / 事实收集已经形成足以约束后续工作的可复用结论；
2. 架构 / 方案 / scope 边界已经冻结，后续开始不同性质的工作；
3. 一组有意义的 mutation 已形成可恢复成果；
4. 关键验证完成，结论会影响下一阶段；
5. 即将进入外部等待、provider 限流/冷却、长耗时或高失败概率步骤；
6. handoff、role switch、context reset、会话切换前；
7. 已知中断即将发生且仍有机会写回时。

短任务如果从启动到完成没有跨越独立恢复阶段，可以省略 `PROGRESS_CHECKPOINT`；但 delegated attempt
仍必须保留 `AGENT_CLAIMED` 与 `AGENT_TERMINAL_RESULT` 两端事件。长任务不得把所有事实价值积压到最后一次报告。

### Canonical event

统一使用低频事件：

```text
PROGRESS_CHECKPOINT
---
work: <owner/repo#issue@step>
phase: <semantic phase>
recoverability: REMOTE | LOCAL_ONLY
completed: <facts / conclusions completed>
durable_refs: <PR / branch / commit / exact head / report pointer, when available>
verification: <done / pending / not-run + evidence>
remaining: <what is still not done>
blockers: <none or current blocker/risk>
next: <single concrete next action>
```

字段可以按任务缩短，但必须足以让 fresh/resume Agent 判断“做到哪、证据在哪、下一步是什么”。
不要把 chain-of-thought、逐命令日志或大段临时探索塞进 checkpoint。

### Remote recoverability

有代码 / 文档 mutation 时，如果安全、在 scope 内且不会制造错误 authority，应优先在 checkpoint 前形成
remote-recoverable branch / commit / PR exact head。**未 push、仅存在于本机 workspace 的修改不是 durable
成果**；此时必须显式写 `recoverability: LOCAL_ONLY`，不得用自然语言把它描述成“已可恢复”。

Checkpoint 本身不授权 force push、merge、deploy、destructive cleanup，也不要求为了 checkpoint 提交明显
损坏或越界的中间状态；不能安全形成 remote ref 时，诚实记录 LOCAL_ONLY + 风险即可。

## Resume / Recovery 规则

恢复分支与旧 context 不可用的处理见 [Recovery & Handoff](RECOVERY_HANDOFF.md#1-恢复分类)。本节只拥有 checkpoint 的读取/验证 mechanics；没有旧 checkpoint 本身不新增 recovery gate。

恢复任务时：

1. 先按当前 Bootstrap / access route 读取 live Work Order、current durable ruling、Issue state 与 remote refs；
2. 存在时，读取同一 `work` 的最近有效 `AGENT_CLAIMED` / `PROGRESS_CHECKPOINT` / `AGENT_TERMINAL_RESULT` / HANDOFF / READY_FOR_REVIEW；若只有 CLAIM 而没有 matching TERMINAL，只能判定该 attempt 尚未 durable 闭合，是否 active / suspect / recoverable 需结合 current activity 与 deployment staleness 规则判断；不存在或旧 context 不可用时按 Recovery & Handoff 从 current durable state 重建，不把旧产物缺失单独视为 blocker；
3. 用 live GitHub state 校验 checkpoint 中的 branch / commit / exact head / PR 是否仍 current；
4. checkpoint 与 live state 冲突时，以 live durable state 为准并报告 drift；不得盲信旧 checkpoint；
5. 从最近仍成立的 checkpoint 继续，不要求重新研究已经有 durable evidence 的前序阶段。

Checkpoint 是 recovery evidence，不是 authority，也不迁移 task state。Issue label / exact remote refs / current
durable ruling 的优先级保持不变。

## 不 trace 的内容

- 临时推理过程（chain-of-thought）
- 已丢弃且没有后续事实价值的探索路径
- 非权威草稿
- 高频 heartbeat / “还活着”信号
- 循环日志、原始工具输出（应留在 artifact / execution node，只在 checkpoint 引用摘要）

## Pointer 规则

完成任何上述具有事实价值的行为或阶段后，**返回精确可恢复 pointer**（PR / commit / exact head /
durable report pointer）。durable trace 必须产生可恢复引用；只存在于聊天的结论不是 pointer，不算数。

对 delegated executor，最终 detailed result 必须进入 `AGENT_TERMINAL_RESULT` 或其精确引用的 durable report；terminal chat return 只返回该结果的 exact GitHub pointer，具体语义见 Agent Interface §1.8。Architect/orchestrator 的 Human Completion Card 不替代本事件。
