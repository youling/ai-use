# Agent Worksite Log — 本地施工现场日志

**Protocol Version: 0.1.0** · **Classification: L2 Targeted Reference**

本协议定义多 Agent、多节点、跨会话施工时的**现场 Markdown 工程日志**。它结合 Engineering Logbook（工程日志）、Site Diary（施工日志）和 Handover Log（交接日志）的可恢复信息，而不是新建一份全局 Work 状态机。

**核心原则：`LOCAL_FIRST_RECOVERY_EVIDENCE / GITHUB_FIRST_AUTHORITY`。** 在 GitHub 回执尚未写回时，节点本地尽可能留下足以恢复的事实；一旦能访问权威来源，必须按 current Work/authority/heads 对账并补写。现场日志不是 GitHub `AGENT_CLAIMED`、`PROGRESS_CHECKPOINT`、`AGENT_TERMINAL_RESULT`、正式交接、Review 或 merge 的替代品。

长期语义归属：
- [Durable Trace](DURABLE_TRACE_PRINCIPLE.md) 拥有 GitHub checkpoint/terminal 事件与非 GitHub 产物定位；
- [Recovery & Handoff](RECOVERY_HANDOFF.md) 拥有 cold/warm/crash 恢复和正式 ownership/角色交接；
- [Agent Interface](../docs/AGENT_INTERFACE.md) 拥有派单、执行边界与完成判断；
- 本文件**只拥有施工现场日志的选用、位置、字段、追加、对账和清理边界**。

## 1. 适用性：有现场才有日志

工头在任务启动/接续时判断是否需要现场日志。以下情况应创建或恢复本地 `WORKSITE_LOG.md`：

- 长期、复杂、多阶段、多会话或可能由不同 Agent/runtime 接手的 Work；
- 在某个真实节点上持续修改代码、环境或现场状态，尚有未推送的唯一证据；
- 研究产出包含不能合理进入 GitHub 的用户/业务原件、大文件、媒体、二进制、数据库快照或重要失败样本；
- 后续执行者若不读取现场记录，就无法安全地判断已做什么、哪里有未保存成果、什么不该重做。

一次性纯只读检查、短小且已从 GitHub 完整可恢复的代码/文档任务，不强制新建日志；**即使使用了本地日志，也不意味着 GitHub-only 成果还必须重复登记节点/路径**。不按固定时间或每条工具调用写入，以语义阶段、重要失败或风险步骤为触发。

## 2. 唯一现场与放置位置

**每个隔离 Work Context / attempt / 可变写域只有一个现场日志 writer；不同并行工头、子任务和节点不共享一个可写 MD。**

- 默认位置：隔离 worktree/工程目录根下的 `.worksite/WORKSITE_LOG.md`，便于启动器和接班者定点发现。
- 重要非 GitHub 原件在持久数据目录中时，可优先把 `WORKSITE_LOG.md` 放在该 owner 控制的数据目录根部、与原件/manifest 相邻；工程目录只保存指向它的**只读地址**，不再维护第二份可编辑日志。
- 若一个 Work 跨节点/不同物理工作区，各自有自己的现场日志，使用相同逻辑 `work`、不同 `worksite_id` 和 `node`；换节点时通过精确指针关联前一现场，不尝试同步编辑一份全网共享 MD。
- 日志应留在对应 owner 的私有/本地存储范围，**绝不默认提交到 Git**。位于 Git worktree 内时，先确认其目录实际被忽略（如受控本地 exclude）；不能保证不被误提交时，移至 owner 的非 Git 持久目录。不得为了日志而改写别的工头的 `.gitignore` 或占用共享写域。
- 临时容器文件系统、tmpfs、可自动清理的 worktree 不可充当非 GitHub 唯一原件的持久 home；外部 volume、owner-owned archive 或等价来源由实例 owner 决定。

工作坐标沿用 **`<owner>/<repo>#<issue>@<step>`**，例如评论内多 lane 仍属于同一个主题 Issue。`dispatch_ref` 必须指向精确有效派单评论；本地文件名/路径和工作区位置不授予 Work claim 或 mutation authority。

## 3. 人可速读的摘要 + 可追加事件

使用**一份 Markdown**，文件头为少量可解析的 YAML（`schema: ai-use.worksite-log/v0.1`），下面依次为：

1. **现场身份**：`work`、`worksite_id`、`attempt`、精确 `dispatch_ref`/`claim_ref`、`actor`（provider/runtime、逻辑 agent/session）、`node`（Fleet 稳定 UID；未知则 `UNKNOWN`）、`namespace`（宿主/WSL/容器）、`workspace_root` 和可选 `evidence_root`。
2. **当前速读快照**：`as_of_event`、最近核对的 GitHub Work/PR/HEAD、当前已观察事实、真实 blocker、未写回范围和下一具体动作。它是**可重建的派生摘要**，不是第二个有权威的 Work 状态。
3. **事件流水**：按 `E0001` 等顺序追加；每条包含 RFC3339 带时区时间、`event_id`、Agent/工作上下文、动作与证据、验证 `PASS|FAIL|NOT_RUN|UNKNOWN`、需要时的 artifact locator/hash、`next`，以及是否已同步到 GitHub。

事件类型是**现场观察分类**，不是新增 Work lifecycle：`START`、`OBSERVATION`、`CHECKPOINT_LOCAL`、`ARTIFACT`、`FAILURE`、`HANDOFF_NOTE`、`SYNC_ACK`、`RECOVERY_NOTE`。涉及终局时只写本地事实和 `TERMINAL_WRITEBACK_PENDING`；只有当前 GitHub `AGENT_TERMINAL_RESULT` readback 才能确认 remote terminal。

不记录逐命令刷屏、chain-of-thought、无事实价值的心跳、密码、token、Cookie、私钥、可直接鉴权的签名 URL 或完整敏感来源正文；对于重要源文件记录**定位/来源/哈希指针**，原始数据保留于有权的 owner 原件目录。记录的本地路径可能也是敏感信息，未经当前 owner/目的地授权不得复制到公共 GitHub 或其它项目。

### 最小事件边界

- **开工**：在现有 Bootstrap、GitHub durable dispatch/CLAIM 和执行授权满足后，写一次 `START`，确认本地节点/环境、实际工作区和基线来源。GitHub 暂时不可达时，可以定位/读取既有现场，但**不能用新建的本地 START 冒充 remote CLAIM 或新的权限**。
- **施工中**：完成有意义的研究、修改、验证、失败诊断或产生不可轻易重建的资料时写一条事实事件。高风险/长耗时步骤前可写 `CHECKPOINT_LOCAL`，记录可回退/可接续事实，不提高外部操作授权。
- **正常交接**：写 `HANDOFF_NOTE`，注明原执行者、候选接手者、已完成、未完成、冲突写域和原始证据。接手 Agent 先 live-revalidate GitHub claim/ownership；日志本身不使 takeover 生效。
- **突发中断**：下一 Agent 只信最后一条**完整事件**，并以现场文件、git status/diff、实际对象清单、GitHub live refs 验证；部分写入、未知变更和已失效归属应标 UNKNOWN/DRIFT，不补造历史。
- **回写与对账**：在有权访问 GitHub 后，比对 `last_synced_event` 之后的本地事实与 current Work/HEAD/ownership，授权范围内补充 `PROGRESS_CHECKPOINT` / terminal，并 readback。然后追加 `SYNC_ACK`，写精确远端评论或 commit pointer 及覆盖到的 event ID。不做“最后编辑者覆盖前者”，也不把 local report 自动晋升为 Architect acceptance。
- **清理**：普通 GitHub-only、已完成远端留档的临时日志可按 owner 清理合同处理；**唯一的非 Git 原件、未同步现场事件及其证据不得因删除工作树而丢失**。无法保全时在现有权责内报告 `LOCAL_ONLY`、剩余路径和数据丢失风险，阻止受影响的 destructive cleanup。

## 4. 追加一致性与恢复强度

- 单一 writer 负责当前文件；子 Agent 在各自隔离工作区写自己的日志，由 Foreman 引用/综合，不让多个进程直接编辑同一 Markdown。
- 每条事件以 `<!-- EVENT E0001 BEGIN -->` 和 `<!-- EVENT E0001 END -->` 成对界定。仅包含完整尾标记的条目进入有效事件链；中断的半条事件不算观察已完成，更不算远端已确认。
- 可以原子更新顶部派生摘要（标明 `as_of_event`），但不得静默重写、删改已确认的事件；勘误通过新事件引用旧 `event_id`。实际持久性依文件系统能力，写入重要事件时采用可用的 flush/fsync/原子替换手段，不声称对所有文件系统/掉电故障有强事务保证。
- `last_synced_event` 只能依据实际读回的 GitHub 回执前进；断网、工具失败或局部推送不得伪称 SYNCED。GitHub 与本地矛盾时保留两份证据并标记 `DRIFT`，不得默默覆盖当前事实。
- **本地日志与 GitHub 指针是互补恢复面，不是两个同等级的事实源。** 同机相邻文件也不是离机备份；真正不能丢失的大型原件按 owner 已授权的存储/备份/完整性规则保护，AI Hub 可按现有权限协调跨节点取回，不自动获得取数权限。

## 5. 接续验收样例

| 情况 | 正确解释 |
| --- | --- |
| 工头断网前写下文件 SHA，但还没 GitHub checkpoint | 本地 `CHECKPOINT_LOCAL` 可作恢复线索；`last_synced_event` 不前进；回网后 live reconcile |
| Codex 在 A 节点执行，OpenCode 在 B 节点接任 | 两份不同 `worksite_id` 的日志 + 同一 Work/派单指针，B 核实 GitHub authority/ownership 后接任 |
| 仅有已推送 GitHub 的代码/文档 | 精确 GitHub refs 足以恢复；不必为产物登记节点路径或强制保留本地日志 |
| 用户业务库留在持久来源目录 | 本地日志记原件 locator、hash/manifest、owner，GitHub 仅保存被授权的最小回链 |
| 工头删除临时工作区后仍指向其中大文件 | 禁止声称资料可恢复；必须先保全，或如实标为 `LOCAL_ONLY` 与缺口 |
| 某 Agent 看到日志写“我已接班” | 只是本地自述，不构成 GitHub claim 转移、lease 授权或新执行权 |
| 日志尾部只有 BEGIN 无 END | 视为不完整候选，不构成完整事件、PASS 或已执行的证据 |

可复制但不含真实账号/设备/客户信息的示例见 [Worksite Log Template](../50_TEMPLATES/WORKSITE_LOG.md)。