# Session & Context Lifecycle

ai-use v2.0.0

**Classification: L2 Reference / Playbook. Not default bootstrap reading.**

本文是 targeted reference：仅在 session / handoff / recovery 等场景触发后读取。
普通任务默认不读本文件；需要知道该读什么时先看 `READING_MAP.md`。

跨项目通用的 Agent 会话生命周期与上下文管理方法论。适用于 Codex、OpenCode 及其他兼容 Agent / Skill 与其控制平面。

本文档只定义通用原则与模板，不绑定任何具体项目、控制平面实现或历史任务。各系统在具体落地时，按自身协议实现（如状态 label、snapshot 文件等）。

## 1. Mental model

核心模型：

> **用户 + Architect 是长期控制角色；Builder / Verifier / Runner 默认是可替换、可丢弃的临时执行资源。长期知识上 Git / GitHub，本地任务现场默认可删除、可重建。**

> 说明：“长期”指角色职责跨阶段持续，不表示 chat / session 持久；Architect 的 session 同样可丢弃，按 §5 Architect Fast Restore 从 durable state 恢复。

三层边界：

- **Durable knowledge / state**：全局规则（ai-use）、控制平面、项目仓库及其远端 commit / PR / 文档。唯一可恢复事实来源。
- **Chat session = working memory / cache**。可随时丢弃，开新会话从 durable source 重建。
- **本地任务 workspace = ephemeral execution state**：任务级独立可变工作区（worktree / clone / container / 独立目录），远端可恢复后可整体删除；归属优先由 task / workspace / Git history 表达，不要求在业务文件内写 Agent 身份注释。

- 会话可以死，但任务必须能从持久状态恢复。
- 聊天 transcript、推理过程、临时结论不是任务合同，也不进入持久状态。

推论：

- 任何"下一步能继续"的必要信息，必须已存在于持久状态（Issue / branch / commit / PR / durable docs），不能只存在于旧聊天里。
- 事实源优先级（从高到低）：
  1. 实时任务状态（如 Issue status label）；
  2. 远端 branch / commit / PR；
  3. 长期项目文档；
  4. snapshot / cache / index（如 CURRENT_ARCHITECTURE_SNAPSHOT、Decision Index、Bootstrap Index）；
  5. 聊天记忆。

## 2. Bootstrap levels：L0 → L1 → L2 → L3

> 附：宪法规定四层阅读（L0/L1/L2/L3），见 `CONSTITUTION.md` §10 与 `READING_MAP.md`。
> 本文档历史使用了 L0→L1→L2 三层称呼，含义等价：本文的 "L0" 即宪法 L0（只指 slim `AGENTS.md`，**不指通读整个 ai-use 或控制面文档**）；本文未单列 L3（rationale/archive），该类内容默认不属于任何 Bootstrap 层。

### L0 — Rules / Identity

启动必读，成本固定且小。L0 只指 **slim `ai-use/AGENTS.md`（机器 L0）+ 精确任务指针**，不要求 Agent 通读整个 ai-use 代码库或完整控制面文档：

- 全局 L0 规则（`ai-use/AGENTS.md`，slim L0，不递归读其他 ai-use 文档）；
- 精确任务（Work Order Issue）及其当前状态；
- 自身身份 `<node_id>/<agent_type>/<session_id>`；
- 本机必要能力 / active-task 摘要：优先取控制平面、本地 runtime 或派发者已提供的当前任务相关摘要（只读，不读其他 Agent 的任务全文）；不存在摘要源时只做当前任务的 targeted preflight，禁止为生成摘要扫描整机、所有 worktree / 进程 / 仓库或其他任务全文。

需要更多上下文时，按 `READING_MAP.md` 决定 targeted 读取哪一层，不默认全量读。

控制平面核心协议（AGENTS.md / AGENT_PROTOCOL.md 等）**不属于所有 Agent 的默认 L0**；只有当精确 Dispatch / Work Order 或当前场景明确需要时才 targeted 读取。

### L1 — Task Context

只读取与当前任务直接相关的信息：

- 当前项目、branch、worktree、PR；
- Work Order 明确引用的 contracts / 文档 / registry 条目；
- owns 范围内的代码。

不读：无关项目、closed Issues、全部历史 PR、全部历史聊天、与任务无关的代码。

### L2 — Deep Dive

仅出现以下情况才扩大读取范围：

- Work Order 与代码事实冲突；
- contract 不明确；
- BLOCKED；
- Handoff / 恢复异常；
- 测试失败原因无法定位；
- Architect Review 要求；
- 安全 / 权限边界需要核查。

禁止以"可能有用"为由默认扫描全部历史。

**默认启动成本应与当前活跃任务范围相关，而不是与全部历史规模线性增长。**

## 3. Executor Cold Bootstrap template

用于新 Work Order、跨设备 Handoff、旧会话丢失或污染。占位符由派发者填好，执行 Agent 不改写。

> 说明：本模板是完整 protocol / reference。默认用户侧启动文案应使用 §9 的 pointer seed（只寻址，不复制本模板全文）。

```text
<CONTROL_PLANE> Executor Cold Bootstrap

SESSION
suggested_name: [<project>][#<issue>][<agent-node>] <short-task>
note: 会话名仅供人类导航，不是任务状态源。

RUNTIME
model: <model>
version: <model-version>
thinking: <enabled/disabled>
reasoning_effort: <level>
role: executor

TASK
control_plane: <control_plane_repo>
work_order: #<issue>
project: <project_repo>
branch: <branch>
worktree_hint: <path-or-none>

原则：
- Git / GitHub 是唯一持久状态源；旧聊天不是任务合同。
- 只执行明确派发的 #<issue>，禁止自行寻找其他 Work Order。

BOOTSTRAP（分层定义见本文档 §2，只做必要读取，禁止默认全量扫描）

L0 — Rules / Identity
1. 获取最新 <control_plane_repo> 与 <project_repo>。
2. 读全局 L0 规则（ai-use/AGENTS.md，slim L0，不递归读整个 ai-use 或完整控制面文档）。
3. 打开精确 Work Order：#<issue>。
4. 识别身份：<node_id>/<agent_type>/<session_id>。
不要读取其他无关 Issues。

控制平面 AGENTS.md / AGENT_PROTOCOL.md 仅在 #<issue> 的 Dispatch/Work Order 或当前场景明确引用时才 targeted 读取，不作为默认 L0。

L1 — Task Context
只读取与 #<issue> 直接相关的信息：
- Work Order 正文、引用的 contracts / runbook / 架构文档；
- <project_repo> 当前 README 与 Work Order 指向的文档；
- owns 范围内代码；
- 当前 branch / remote HEAD / 已有 PR（若存在）。
不要默认读取所有项目、closed Issues、全部历史 PR、长期历史聊天。

L2 — Deep Dive
仅当出现 §2 L2 所列情形（冲突 / BLOCKED / Review 要求 / 恢复异常等）才扩大读取。

EXECUTION
1. CLAIM #<issue>，记录完整身份；状态 label 按序更新 CLAIMED → WORKING。
2. 使用独立 branch / worktree。
3. 严格执行 owns / forbidden / acceptance 边界。
4. 共享接口冲突 → BLOCKED，不自行裁决。
5. 小 commits，及时 push；不自行 merge main。
6. 关键状态评论按控制平面协议写入（如 UTF-8 safe path），写入后 read-back 验证。

FINISH
- tests / verification → push → PR → READY_FOR_REVIEW
- 报告：commits / tests / changed files / unresolved / shared-interface impact
- 停止等待 Architect Review。
```

## 4. Executor Warm Resume template

同一 Work Order、旧会话仍健康时使用。不做全量冷启动。

> 说明：本模板是完整 protocol / reference。默认用户侧启动文案应使用 §9 的 pointer seed。

```text
<CONTROL_PLANE> Executor Warm Resume

继续当前 Work Order，不重新做全量冷启动。

当前任务：
project: <project_repo>
issue: #<issue>
branch: <branch>

只刷新：
1. fetch 最新全局 L0 规则（ai-use/AGENTS.md）与当前控制平面最小入口；
2. 若全局 L0 规则或控制平面协议自本会话启动后发生变化，只重读变化部分；
3. 读取 #<issue> 最新状态与 meaningful events：
   REVIEW / BLOCKED / ARCHITECT_DECISION / HANDOFF / READY_FOR_REVIEW 等；
4. fetch 当前 remote branch；检查 branch HEAD、worktree、PR；
5. 对比本地状态与远端状态。

若一致：
从最新 next_action 继续。

若不一致：
不猜测，按控制平面 HANDOFF_RECOVERY 规则恢复，无法安全恢复则 BLOCKED。

禁止：
- 重读所有历史 Issues；
- 扫描所有项目；
- 为恢复会话而重新设计已冻结 contract。
```

## 5. Architect Fast Restore template

新 Architect 不追求理解全部历史，只恢复"现在什么是真的、当前活跃图、冻结边界、风险与下一动作"。

> 说明：本模板是完整 protocol / reference。默认用户侧启动文案应使用 §9 的 pointer seed。

```text
<CONTROL_PLANE> Architect Fast Restore

你是 <system> 的新任架构 Agent。旧 Architect 会话不可用。
禁止要求用户复制旧聊天记录；旧聊天不是持久状态源。
GitHub / Git 是唯一持久状态源。

目标不是理解全部历史。
目标是用最少读取恢复：现在什么是真的、正在发生什么、哪些边界不能碰。

PHASE A — FAST RESTORE
只读取：
1. 全局 L0 规则（ai-use/AGENTS.md，slim L0，不递归读整个 ai-use）；
2. 控制平面 README / AGENTS.md / AGENT_PROTOCOL.md / 架构与运行模型文档（如存在）；不默认扫描整个控制平面全文，只读恢复当前状态所需的最小入口；
3. compact snapshot / index（如 CURRENT_ARCHITECTURE_SNAPSHOT、Decision Index、Bootstrap Index）——仅作 cache / index，不是实时状态事实源；
4. registry 中当前活跃任务涉及的条目；
5. 当前所有 OPEN Work Orders（实时状态以 Issue status label 为准）。
禁止：扫描所有 closed Issues、全部历史 PR、所有项目全部文档、全部代码、追溯历史讨论原因。

PHASE B — ACTIVE GRAPH
根据 OPEN Work Orders 建立当前活跃任务图：
issue / project / status / executor / branch / PR / dependencies /
shared contracts / resource ownership / blocked_by / next architect action。

只对 active / blocked / ready_for_review 涉及的项目做 L1 读取。
每个活跃项目默认只读 README + 架构文档；
ROADMAP / HANDOFF / contracts / 代码 / 历史 PR 仅当 Work Order 引用或当前决策需要时读取。

PHASE C — VALIDATE SNAPSHOT
若 snapshot 存在：将其中的 active references 与实时状态对照。
冲突规则：
实时状态 > 远端 branch / commit / PR > durable docs > snapshot / cache > 聊天记忆。
snapshot 过期 → 指出过期项，不因 snapshot 写了某状态就覆盖实时状态。

PHASE D — OUTPUT
输出 CURRENT_ARCHITECTURE_SNAPSHOT，只包含：
system_goal / current_phase / frozen_boundaries / active_work_orders /
blocked_items / deferred_items / recent_effective_decisions / shared_contracts /
critical_resources / top_risks / next_actions / uncertainties。
每项尽量引用持久状态来源。

不要：重述全部历史、保存模型推理过程、罗列已 superseded 的旧方案、为完整而完整。
需要历史才能确定的项 → 标记 NEEDS_DEEP_DIVE，不立即自动扫描全部历史。

STOP
不施工。不改仓库。不派新 Work Order。
先把恢复结果给用户确认，确认后再接任调度。
```

## 6. Architect Convergence template

大阶段结束、关闭当前 Architect 会话前执行。目的：让下一任 Architect 不需要重新经历本阶段的探索过程。

```text
ARCHITECT CONVERGENCE

目的：
让下一任 Architect 不需要重新经历本阶段的探索过程。

执行：
1. 清点所有 OPEN Work Orders；
2. 关闭 / 取消已失效或已完成的 Issue；
3. 检查 BLOCKED / deferred 项是否仍有效；
4. 收敛本阶段重大架构决策：
   decision / reason（最短充分理由）/ supersedes / source（Issue / PR）；
5. 删除或标记已被推翻的架构假设；
6. durable docs 只保留长期知识；活任务状态不复制进项目长期文档；
7. 刷新 compact snapshot / index（若系统使用）；
   snapshot 中只引用 active Issue，实时状态仍由 Issue label 决定；
8. 不保存聊天 transcript；
9. 不保存 chain-of-thought；
10. 输出 READY_FOR_ARCHITECT_HANDOFF。

完成后当前 Architect 会话即可安全废弃。
```

## 7. Session naming

- Executor：`[<project>][#<issue>][<agent-node>] <short-task>`
- Architect：`[ARCH][<scope>] <phase-name>`

状态（WORKING / BLOCKED 等）不进入会话名。

会话名仅用于人类导航，不作为任何状态源。

## 8. Keep old session vs start new session

| 情形 | 选择 |
| --- | --- |
| 同 WO + 同 branch + 连续施工 | 优先旧会话（Warm Resume） |
| 同 WO + 跨设备 / 强制 Handoff / 旧会话丢失或污染 | 新会话（Cold Bootstrap） |
| 新 WO / 新职责 | 新会话（Cold Bootstrap） |
| Architect 换阶段 | 新会话；按阶段切换，不按每张单切换 |

判断依据是持久状态能否安全恢复当前任务，而不是"聊天里还有多少内容"。

## 9. Seed / Dispatch Minimality

原则：**Seed 负责寻址，不负责承载知识。**

Git / GitHub / durable docs 保存任务合同、约束、验收标准、协议和可恢复状态；聊天 seed 默认只提供启动所需的最小指针，避免复制 durable context、制造协议副本和上下文膨胀。

### 9.1 最小必要项

seed 默认只包含：

- identity / role（必要时）；
- task 或 control-plane pointer（Work Order Issue 或控制平面引用）；
- startup mode（Cold Bootstrap / Warm Resume / Review 等）；
- 必要的 exact ref（branch / commit / PR / label，如需要）；
- stop condition。

凡能由 durable dispatch / Work Order 无歧义推导者，seed 不必重复；只有无法无歧义推导时才补字段。

不复制：requirements、acceptance、review/recovery protocol、长期架构边界等已存在于 durable source 的内容。

### 9.2 规则

- durable knowledge（Work Order、requirements、constraints、acceptance、review/recovery protocol、长期架构边界）必须保存在 durable source，不靠聊天 seed 保存；
- 只有"尚未持久化且当前执行必需"的临时事实才允许补充进 seed；应尽快转存 durable source，不允许 seed 演化成第二份合同；
- §3–§5 的完整模板继续作为 protocol / reference；默认用户侧启动文案使用 pointer seed，不机械复制整份模板；
- durable source / live state 与 seed 冲突时，以 durable source / live state 为准，seed 不成为第二 SSOT；
- 访问路径属于寻址元数据：当 pointer 指向 GitHub 且 public / private 会影响启动路由时，seed / dispatch 应显式给最小 access hint（如 `access: github-private | github-public`），不得要求 Agent 先试错探测；该 hint 不承载任务合同，不成为第二 SSOT；机制保持通用，不绑定 ai-hub；
- 原则适用于 Builder / Reviewer / Verifier / Architect / Runner 等，不绑定 ai-hub；ai-hub 只做自身映射；
- 不引入 Bot、自动调度器、数据库、session recorder、prompt registry 或新的状态源。

### 9.3 Pointer seed 示例

用户 → Builder 的默认 seed 应能压缩到最小，例如：

```text
领取架构师任务 <Issue URL>
```

与 §9.1 不冲突：startup mode / stop condition 等若能由 durable dispatch / Work Order 无歧义推导（例如 Issue label 与 WO 已明确启动方式与停止条件），seed 不必重复；只有无法无歧义推导时才补最小字段。requirements / base / scope / acceptance 已持久化在 Work Order 中，不在聊天 seed 重复。

> **Reference / protocol template only — 不是 Human Agent Seed 的规范格式。**
> Human Agent Seed 的规范格式见 `docs/AGENT_INTERFACE.md` §3（Default Minimal Agent Seed）。
> 本节的完整参考格式仅供控制平面协议设计参考；日常派发不机械复制整份模板。

完整参考格式（派发者填好，执行 Agent 不改写）：

```text
<CONTROL_PLANE> <startup_mode> pointer seed

TASK
control_plane: <control_plane_repo>
work_order: #<issue>
project: <project_repo>
access: github-private | github-public（public / private 会影响启动路由时给）
branch: <branch>
startup_mode: Cold Bootstrap / Warm Resume / Review / Architect Fast Restore
exact_ref: <branch/commit/PR，如需要>
stop: <PR 到 READY_FOR_REVIEW 后停止>

原则：Git / GitHub 是唯一持久状态源；seed 只寻址，不承载知识。
完整协议见 <control_plane>/AGENT_PROTOCOL.md 与 ai-use §3–§5 模板。
```

## 10. Project Reproducibility Contract

每个项目必须把自身可复现所需的知识放回项目仓库，而不是复制进 ai-use / ai-hub。

项目仓库至少应保存：

- 依赖与 lockfile；
- setup / run / test / lint 入口；
- 必要 runtime 版本；
- 必要 env var 的**名称与语义**（不包含 secret 值）；
- fixture / migration / local service 要求；
- 项目 AGENTS / README / RUNBOOK 等长期约束。

不强制所有项目使用同一种文件名或工具；优先使用项目原生机制。ai-use 不复制 Python / Node / Docker 等项目专属安装清单。
