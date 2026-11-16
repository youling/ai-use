# Durable Trace Principle

**Protocol Version: 1.2.0** · **Classification: L2 Targeted Reference.**

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
execution_context: <observed execution surface or current evidence pointer, when material>
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
claim: <exact AGENT_CLAIMED pointer>
result: SUCCESS | NEGATIVE_RESULT | PARTIAL | BLOCKED | HUMAN_REQUIRED | FAILED | CANCELLED
remote_head: <sha | none>
execution_context_ref: <exact evidence for environment-bound execution, when material>
durable_refs: <PR / commit / report / artifact pointers, or none>
artifact_disposition: GITHUB_ONLY | NON_GITHUB_ARTIFACTS | MIXED | NO_ARTIFACTS
artifact_locations: <only for important non-GitHub artifacts; otherwise omit>
verification: <summary>
remaining: <none | exact remaining>
blockers: <none | exact blocker>
next: <single next action>
```

规则：

- 每个已 CLAIM 的 delegated attempt 在正常可写回的终止路径上都必须产生 terminal result，成功与失败没有例外；
- 写回 exact Work coordinate 后必须 readback / 等价 durable read 确认，`WRITEBACK_ATTEMPTED != DURABLE_WRITEBACK_CONFIRMED`；
- `claim` 必须精确引用本 terminal 所关闭的 `AGENT_CLAIMED`，以区分同一 Work coordinate 的多次 retry / recovery attempt；
- terminal result 关闭 execution attempt，不自动关闭 Work Order，不替代 Architect Review / merge / deploy gate；
- terminal 详细事实留在 durable source，不依赖聊天 self-report；
- 没有 authorized durable write path 的 subagent 不得假装产生 terminal event，由 primary/orchestrator 承担最终 durable writeback。

## Execution Context Provenance — 执行上下文来源

**既有回执已有 `executor`、`node`、`remote_head` 与本地 Worksite Log 的 `actor/namespace/workspace`，但未要求实际执行环境与具体测试结果绑定。** 本节在现有 CLAIM / CHECKPOINT / TERMINAL 事件中条件式补齐；不新建环境注册表、第二种事件或必须填满的机器 schema。

当本次事实/测试/构建/异常解释**依赖具体执行面**时，Executor（包含末端 child）应在执行前或首次观察时自报并保存最小 `execution_context`，随后把每个有意义的验证证据绑定到该 context 的 `as_of` 与 `ref`。没有本地执行面、仅修改 GitHub 文档的简单任务，可写 `execution_context: GITHUB_ONLY / N/A` 或不填。可引用仍适用的 current Capability Self Check / Worksite Log / CI job URL，**不必复制一份主机清单**。

```yaml
execution_context:
  agent:                    # Agent 逻辑身份，不等于 OS 账号
    provider: <observed product/provider | UNKNOWN>
    model: <observed model/version | UNKNOWN>
    harness: <observed ZCode/Antigravity/OpenCode/Workbuddy/etc or other | UNKNOWN>
    session: <provider run/session pointer if available; otherwise UNKNOWN>
  surface: <LOCAL | WSL | SSH_REMOTE | CONTAINER | VM | CI | BROWSER | DEVICE | CLOUD | MIXED>
  host: <owner-approved alias/node identity; no unauthorised private topology>
  guest_or_container: <OS/distro/kernel/arch + runtime/namespace when relevant | N/A>
  principal: <actual OS account or UID/GID/class when relevant | UNKNOWN>
  toolchain: <actual command/runtime/tool versions used; not full package list>
  workspace: <authorized repo/worktree/ref/exact HEAD/dirty state when relevant>
  profile: <material config/profile ID or digest; never credential values>
  as_of: <ISO-8601 timestamp with timezone or exact CI job evidence URL>
  evidence: <command/test/job/source receipt proving these fields>
  confidence: <OBSERVED | INHERITED_REVALIDATED | UNKNOWN>
```

最小填写原则：

1. **分层，不混淆**：Agent provider/model/session、实际执行主体（Host 用户/UID）、工作负载容器 UID、Fleet node identity、可调用能力、当次授权/lease 是不同事实。Host OS 与 WSL/guest/container 的 OS、运行时、工具版本分开；远端运行不能用本机环境替代。未知身份/版本写 `UNKNOWN/NOT_OBSERVED`，不能凭提示词或旧记忆自报为 observed。
2. **结果随环境走**：对测试/构建/动态观察至少绑定执行命令或测试集、返回状态、目标 exact HEAD/制品 digest、适用 OS/arch/runtime、时间或 CI run/job 指针。若 `PATH`、版本、容器 profile、node、principal、source HEAD、权限或网络路径变化会改变结论，新写一条 context delta 或引用新快照；**不能覆盖原测试的环境**。
3. **最小而安全**：不采集完整 `env` dump、Cookie/token、密钥、完整私有配置或无关本地路径；公共 GitHub 只放非敏感别名与证据摘要，敏感拓扑/locator 留给 owner 私有来源。Tool access/SSH/目录存在不等于真实执行成功、持久工作叶授权或 Host mutation authority；缺授权只停止受影响操作。
4. **多 Agent 与失败也要标来源**：子对话可在自己的 evidence/局部回执中记录该 context，由 Foreman 核验后引用；不同 Agent 或多台节点的结果不得拼成一个“同环境全通过”。Job 若 `runner_id=0` / `steps=[]`，只能报告未分配执行者或步骤未执行，不能虚构 Runner 环境或测试 PASS。
5. **按需压缩**：已经通过同一 context 当前核验且没有实质 delta 时，后续 CHECKPOINT/TERMINAL 使用 `execution_context_ref: <exact prior evidence>` 即可；简单、短小、确定性的工作只保留对复现/解释有影响的字段。字段可以缩短，**不能把未知伪装已测**。

在 `AGENT_CLAIMED` 可记预定执行面及已实测身份；`PROGRESS_CHECKPOINT` 引用本阶段真正使用的环境与 delta；`AGENT_TERMINAL_RESULT` 引用支持最终结论的 context，或列明影响复现的 UNKNOWN。`execution_context` / `execution_context_ref` 是对既有事件的附注，不改变 CLAIM/TERMINAL、Work acceptance 或权限语义。

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
artifact_disposition: GITHUB_ONLY | NON_GITHUB_ARTIFACTS | MIXED | NO_ARTIFACTS (when artifacts have been produced)
artifact_locations: <only for important non-GitHub artifacts; otherwise omit>
verification: <done / pending / not-run + evidence>
execution_context_ref: <stage execution context or delta, when material>
remaining: <what is still not done>
blockers: <none or current blocker/risk>
next: <single concrete next action>
```

字段可以按任务缩短，但必须足以让 fresh/resume Agent 判断“做到哪、证据在哪、下一步是什么”。
不要把 chain-of-thought、逐命令日志或大段临时探索塞进 checkpoint。

### 研究产物分类与位置

工头应按**每一项有事实价值的产物**分类，而不是只给整个 Work 贴一个标签。在阶段 checkpoint 中，只有产物新生成或其可恢复性发生变化时才需要补充；terminal 必须明确本轮产物归类。

- `GITHUB_ONLY`：代码、文档、报告、测试等已合理保存在 GitHub。`durable_refs` 中的精确仓库/提交/PR/Issue 指针足够，不重复登记节点和路径。
- `NON_GITHUB_ARTIFACTS`：重要原始来源、用户/业务资料、大文件、媒体、二进制或其他不适合存入 GitHub 的产物，保存在其他位置。
- `MIXED`：同时有 GitHub 交付物和重要的非 GitHub 产物；逐项定位后者。
- `NO_ARTIFACTS`：本次没有形成有事实价值的持久产物。不要为满足格式要求虚构空目录或路径清单。只有 GitHub 产物时应使用 `GITHUB_ONLY`，不能归入 `NO_ARTIFACTS`。

对重要的非 GitHub 产物，在对应 owner 控制的持久来源中记录可用指针。只填写定位、理解和核验该产物所需的字段：

```yaml
artifact_locations:
  - artifact: <逻辑名称；不嵌入私有数据内容>
    kind: ORIGINAL_SOURCE | WORKING_SNAPSHOT | DERIVED_OUTPUT | OTHER
    node: <稳定 Fleet UID 或持久资产/主机标识；仅节点本地文件需要>
    namespace: <host | WSL distro | container | volume | external object/CAS>
    locator: <精确路径或持久对象/CAS 引用>
    persistence: OWNER_DURABLE | NODE_LOCAL_PERSISTENT | EPHEMERAL | EXTERNAL_OBJECT | UNKNOWN
    provenance: <来源指针，以及与原件/快照/派生结果的关系>
    integrity: <适用时的哈希/manifest 指针；否则 N/A>
    availability: PRESENT_AT_CHECKPOINT | LAST_VERIFIED | UNKNOWN
    verified_at: <核验时间或证据指针，适用时填写>
    access: <必要时填写 owner 授权的读取/传输指针>
```

规则：

1. 原始来源、工作快照和派生结果必须区分。路径只是定位符，不证明文件当前仍存在或字节未变化。
2. 清理临时工作区前，必须把重要证据保存到获授权的持久位置；若做不到，应明确记录 `recoverability: LOCAL_ONLY`、已知位置和恢复风险。仅剩临时路径时，不得宣称已经持久化。
3. 私有路径、客户/用户资料指针及来源细节只写入相应的授权 owner 来源。公共 `ai-use` 只保存可复用规则，不保存私有运行态证据。
4. 无法确认当前可用性时，标记 `LAST_VERIFIED` 或 `UNKNOWN`；不能从旧回执推断文件现在仍可访问。
5. 部署侧控制面（例如 AI Hub）可在获得授权后协调跨节点取回数据。网络可达、节点已纳管或知道文件路径，都不等于获得读取、披露或传输权限。
6. 阶段尚未产生产物时，可省略分类。terminal 应明确选择适用类别，让后续 Agent 知道该追踪 GitHub 指针、非 GitHub 位置，还是本轮没有持久产物。

这些字段是对现有事件结构的条件式扩展，不新建 Work 状态机、产物数据库或通用存储服务。

**本地断点补充：** 长期、多 Agent、多节点或持有重要非 GitHub 原件的施工，可在实际工作区/原件目录中留下 [Agent Worksite Log](LOCAL_WORKSITE_LOG.md)。它记录尚未写回 GitHub 的完整现场事件与接续线索；工头必须在恢复连接后按 current GitHub authority/refs 对账，不能将本地日志等同远端 CLAIM、terminal 或第二份 Work SSOT。短小的 GitHub-only 任务不因此增加本地日志门槛。

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
