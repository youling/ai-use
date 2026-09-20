# Recovery & Handoff — Canonical Protocol

**Classification: L2 Targeted Reference**
**Protocol Version: 1.0.0**

本文拥有 recovery/handoff、Work Context、正交 context 维度与 independence/delegation 的长期语义。模板只提供形态。启动顺序与执行门由 [Bootstrap](../10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md) 拥有；continuation、`PREMATURE_YIELD` 与完成边界由 [Agent Interface](../docs/AGENT_INTERFACE.md) §1.4、§1.6–§1.8 拥有；checkpoint 格式与频率由 [Durable Trace](DURABLE_TRACE_PRINCIPLE.md) 拥有。

## 1. 恢复分类

`recovery_kind` 恰有三种值。它描述恢复场景，不是 Work lifecycle，也不授予 authority：

| recovery_kind | 适用场景 | 当前路径 |
| --- | --- | --- |
| `PLANNED_TRANSFER` | 可联系的交出方按 current contract 计划交接角色/工作现场 | 交出方收敛可恢复状态，接收方完成 Bootstrap、接收检查与适用交接记录 |
| `CRASH_TAKEOVER_OR_OLD_CONTEXT_UNAVAILABLE` | 旧 session/context 丢失、失效、污染或无法联系；无法完成计划交接 | 用 current durable authority + 可恢复 Git/GitHub state 重建 fresh context |
| `HOT_OR_WARM_RESUME` | 同一 lineage 的 owned context 仍有效，继续既有任务 | 保留 context，只刷新受影响的 current rules、Work、refs、ownership 与 checkpoint |

不能联系旧方时选择 crash 路径，不伪造 REQUEST、旧 session、旧方已执行的操作或旧方 handoff artifact。warm context 无效时转为 crash 路径；计划交接过程中旧方不可用时也重新分类为 crash。换 context 不新增 authority，不取消 current independent verification 要求。

## 2. 共同恢复门与 currentness

先按 Bootstrap `BOOT-1 -> BOOT-2 -> BOOT-3` 建立当前 authority/access/live state，**之后**才可确认恢复足以执行；不得把 Bootstrap 放在 ACCEPTED 后补办。第一份 normative rules 仍是 current governance repo 的 L0。

只恢复 current target project/program/Work 的最小充分状态：current role/authority、Work Order/dispatch/latest ruling（适用时）、冻结 scope/acceptance、exact remote refs/PR、依赖/active graph、workspace ownership、真实 blocker 与 next action。没有 explicit work 的 Architect 使用 Bootstrap 的 role-bootstrap 规则；普通 delegated executor 的 required Dispatch 不因 crash 免除。

按 [Durable Trace](DURABLE_TRACE_PRINCIPLE.md) 找最近仍有效的 checkpoint/handoff/report，并以 live GitHub state 校验。current live durable state 高于陈旧 handoff/checkpoint/snapshot；记录 drift，保留仍有效的部分，不把旧文本回写成 current truth。不默认扫描整个 workspace 的 OPEN Work Orders、其它项目或全部历史。

检查 authority、冻结边界、相关 active graph、恢复证据与单一 primary。单一 primary 的 authority 来自 [Constitution](../CONSTITUTION.md) §4：用 current durable role/ownership evidence 确定本 scope 的唯一主责；旧会话不可读本身不等于存在双主，但发现仍在并行调度、有效 lease/ownership 冲突或无法确定主责时必须报告真实 gate，不猜旧方已停止。

Fresh/takeover Architect 的 Bootstrap Report 必须按 Bootstrap §3C 写入 current writable durable anchor，才能声称 durable `EXECUTION_ALLOWED`。恢复结果可复用该报告，包含恢复类别、authority/current-state/refs、checkpoint 可用性、drift、primary evidence、限制及下一步，避免强制制造多份重复报告。没有可写 anchor 仍按 Bootstrap 的 session-local 结论处理。

## 3. 三条恢复路径

### 3.1 Planned transfer

交出方在当前 scope 内收敛 active/blocked/deferred work、有效决策、风险与 next actions，建立 [Durable Trace](DURABLE_TRACE_PRINCIPLE.md) 要求的 checkpoint。清理/关闭 Work、workspace 操作仍须 current authority；交接不授权额外 mutation。

当 current planned-transfer contract 要求时，交出方提供 `READY_FOR_ARCHITECT_HANDOFF` artifact 与 exact pointer，Human 或交出方写 `ARCHITECT_HANDOFF_REQUEST`，接收方核对其依据、交接 scope、接收身份与生效条件。REQUEST 只请求 AI 工作角色协调职责交接，不转移 ownership、GitHub permission、人类组织权或商业决策权。

接收方完成 §2、适用能力检查和 handoff check 后，按 current contract 将 `ARCHITECT_HANDOFF_ACCEPTED` 写回 authority anchor；使用 REQUEST/ACCEPTED 事务对的 planned contract 只有 REQUEST 不算已完成转移。报告引用 Bootstrap/handoff/capability evidence；适用验证缺失不能宣称 ACCEPTED。Human confirmation 仅在 current authority/contract 明确要求时为 gate，不因模板存在自动新增。

### 3.2 Crash takeover or old context unavailable

若 current durable authority、可恢复 Git/GitHub state 与 §2 的门足够，**MUST NOT 仅因旧 session/context、旧方 REQUEST、READY_FOR_ARCHITECT_HANDOFF 或 handoff artifact 不可用而阻塞**。记录 unavailable 与实际恢复来源，直接从 current durable state 建立 `FRESH_CONTEXT`，不要求 Human 补旧聊天或为替换崩溃 context 再发一次 prompt。

这里免除的是“必须取得旧方产物”的假前提，不免除 current authority/access、相关工作事实、独立性、primary ownership、durable writeback 或真实安全 gate。无法从 current source 恢复执行必需事实时，精确报告缺口。通过后按 Agent Interface 与 current Work acceptance 继续；material Architect action 仍遵守 [Reconnaissance](../docs/ARCHITECT_RECONNAISSANCE.md)。

### 3.3 Hot or warm resume

复用 current owned warm context，live refresh 当前规则变化、Work meaningful events、remote refs/PR 和 workspace ownership；状态一致时从仍有效的 next action 继续。只重读受变化影响的 context，不重新扫描项目/历史，不为恢复重新设计冻结 contract。health/currentness 失效时改走 §3.2；不是为了切换 mode 就创建新 session。

## 4. Work Context 与正交维度

Work Context = Work Coordinate + session binding + isolated workspace/worktree + current exact head + current mode + context health/checkpoint。Project Architect Context 保存跨工单架构与方向，保持低工具噪声；Work Context 保存一条 Issue/PR/implementation lineage，完成后归档或 compact。长期角色不等于永久 session。会话名仅作 Human 导航，不是状态源。

下列字段和值是长期 machine seam；convenience label 不是新增枚举：

| 字段 | 值 |
| --- | --- |
| `context_policy` | `WARM_RESUME`, `FRESH_CONTEXT`, `COMPACT_SAME_CONTEXT`, `SIDE_CONTEXT`, `FORK_CONTEXT` |
| `mode` | `PLAN`, `BUILD`, `REPAIR`, `SELF_REVIEW`, `VERIFY`, `INVESTIGATE` |
| `continuation` | `TO_DURABLE_BOUNDARY`, `ONE_SHOT` |
| `independence` | `REQUIRED`, `NOT_REQUIRED` |
| `delegation` | `INLINE_PRIMARY`, `SUBAGENT` |
| `parallelism` | `NONE`, `READ_ONLY`, `ISOLATED_WRITE` |

`FRESH_VERIFY = FRESH_CONTEXT + VERIFY + independence:REQUIRED`；普通修复是 `WARM_RESUME + REPAIR + continuation:TO_DURABLE_BOUNDARY`；side research 是 `SIDE_CONTEXT + INVESTIGATE`。字段正交，mode/context/affinity 不产生 authority/currentness；`ONE_SHOT` 不覆盖 current Work 的 completion/stop predicate。

同 lineage 默认 warm 的执行循环与 repair/stop 判定只在 Agent Interface §1.6–§1.8。`FRESH_CONTEXT` 用于 independent verification、安全/权限边界、高风险最终验收、adversarial review、context contamination/无关新工作、真正并行及 `CONTEXT_UNAVAILABLE` 恢复。`FORK_CONTEXT != FRESH_CONTEXT`，`SELF_REVIEW != FRESH_VERIFY`；不能因 warm 方便取消 fresh independence。

## 5. Durable before fragile 与 delegation

在 compaction、provider/backend handoff、session termination/replacement、workspace ownership transition、long-running crash 风险前，先建立 current durable checkpoint；不可预测的 crash 发生后按 §3.2 恢复，不能倒推“旧方未写 checkpoint，所以永远不可接任”。压缩摘要与 provider memory 仍是 cache。

Subagent 是隔离/并行机制，不是 authority 来源或默认 mode 切换方式：

- `MAIN_CONTEXT_OWNS_WORK = YES`；`SUBAGENT_OWNS_WORK = NO`，除非显式委托 isolated child Work Coordinate/workspace。
- `SUBAGENT_RESULT = evidence/summary/pointer`，不是 canonical acceptance truth；`SUBAGENT_IS_FRESH_VERIFY_BY_DEFAULT = NO`。
- `MODE_CHANGE != SPAWN_SUBAGENT`；`SAME_LINEAGE_REPAIR = WARM_PRIMARY_BY_DEFAULT`；`NESTED_SUBAGENT_DEFAULT = DENY`；`PRIMARY_CONTEXT_REMAINS_ORCHESTRATOR = YES`。
- 优先委托独立 exploration、upstream research、test/log triage、有界安全/质量审计、大证据分区与并行只读验证；不因 mode 切换、已知 finding、可合法修复的红测或 Human 说“继续”就 spawn。
- 父保持 orchestrator/final synthesizer。子 contract 只带 work pointer、narrow question、allowed tools/write scope、expected return shape、stop condition；返回有界 evidence/pointer，不倾倒 transcript/log。子失败不自动成为 Human gate。
- 子写需 isolated branch/worktree/generation ownership 与 exact-head handoff；两个子不能共享 mutable workspace，除非显式冲突安全机制。`READ_ONLY` 优先；`PARALLEL_WRITES = ISOLATED_WORKSPACE_OR_DENY`。
- side/fork/subagent 结果不转移 Work ownership/authority。provider action/命令名不能产生 authority 或证明 capability；不支持时 fail closed，仅用可证明等价的 adapter 行为。

机器边界保持 `PROVIDER_COMMAND_IS_AUTHORITY = NO`、`SEED_SECOND_SSOT = NO`、`FORK_COUNTS_AS_FRESH_VERIFY = NO`。provider 适配由 deployment/control-plane adapter 持有，不建立 scheduler、task DB、marketplace、Bot、session recorder 或新状态源。

## 6. 形态与兼容

- [Context mode shape](../50_TEMPLATES/CONTEXT_MODE_SEED.md)
- [Handoff check shape](../50_TEMPLATES/architect_handoff_check.md)
- [Handoff transaction shapes](../50_TEMPLATES/architect_handoff_transaction.md)
- [Capability evidence shape](../50_TEMPLATES/capability_self_check.md)：所需 preflight 语义在 Bootstrap §4，不是所有恢复路径的额外 mandatory hop。
- [旧 Session 入口](../docs/SESSION_LIFECYCLE.md)：只保留 forward anchors；旧 Fast Restore/Convergence 不再是 current instructions。

## 7. Project Reproducibility Contract

每个项目必须把自身可复现所需知识放回项目仓库，不复制进公共治理或控制面。至少保存依赖与 lockfile、setup/run/test/lint 入口、必要 runtime 版本、env var 的名称与语义（不含 secret 值）、fixture/migration/local service 要求，以及项目 AGENTS/README/RUNBOOK 等长期约束。

不强制统一文件名或工具，优先项目原生机制；ai-use 不复制项目专属安装清单。此节保全原 Session §11 的既有要求，不新增 ownership/storage doctrine。
