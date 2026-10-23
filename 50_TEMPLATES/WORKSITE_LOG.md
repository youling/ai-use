---
schema: ai-use.worksite-log/v0.1
work: "<owner>/<repo>#<issue>@<step>"
dispatch_ref: "<exact durable dispatch comment pointer>"
claim_ref: "<exact GitHub AGENT_CLAIMED pointer | NONE>"
attempt: "<attempt id / generation>"
worksite_id: "<unique local worksite ID>"
node_uid: "<stable Fleet UID | UNKNOWN>"
node_label: "<local human-readable alias, optional>"
namespace: "<host | WSL distro | container | volume>"
workspace_root: "<exact local workspace path>"
evidence_root: "<owner-controlled raw evidence root | NONE>"
actor: "<Codex | OpenCode | Antigravity | other + logical agent/session>"
last_observed_remote_ref: "<GitHub Work / PR / commit pointer, as observed>"
last_synced_event: "NONE"
snapshot_as_of_event: "E0000"
---

# WORKSITE_LOG — 施工现场日志

> 本文件是现场恢复证据，不是 GitHub 的 Work authority / CLAIM / Review / terminal。
> 先读 current ai-use L0，再核验精确派单、现行 GitHub Work 与 owner；不可仅凭本文件接管或扩权。
> 具体字段和同步规则见 current ai-use `30_PROTOCOLS/LOCAL_WORKSITE_LOG.md`；本文件复制到节点后不依赖相对文档链接。

## 当前现场摘要（派生，只表示 snapshot_as_of_event）

- **当前观察**：<已做什么；证据是什么，观察时点是什么>
- **最近完成的检查**：<PASS/FAIL/NOT_RUN 与证据>
- **重要非 GitHub 证据**：<源文件类别、owner 来源、local locator/hash 清单；如无则 NONE>
- **尚未同步 GitHub**：<从哪一个 E 事件开始；没有则 NONE>
- **有效阻断／未知**：<没有则 NONE；不要把历史结论当现役事实>
- **下一具体动作**：<谁在什么授权条件下做什么>
- **上一个现场**：<若跨节点接续，前一 worksite pointer；否则 NONE>

## 事件流水（仅追加，完整 BEGIN/END 为一个事件）

<!-- EVENT E0001 BEGIN -->

### E0001 · START · <RFC3339 timestamp with UTC offset>

- **event_id**: <unique immutable event id>
- **actor**: <runtime / logical session / execution context>
- **action**: <开工或接任时实际完成的事实、源/目标及当前节点>
- **observed**: <现行 GitHub dispatch/claim/remote head 已核对的内容；未核对明确 UNKNOWN>
- **verification**: <PASS | FAIL | NOT_RUN | UNKNOWN + pointer>
- **artifacts**: <如果已有重要非 GitHub 产物，指向本地 owner 原件 manifest；否则 NONE>
- **sync**: PENDING_SYNC
- **next**: <下一具体动作>

<!-- EVENT E0001 END -->

<!-- EVENT E0002 BEGIN -->

### E0002 · CHECKPOINT_LOCAL · <RFC3339 timestamp with UTC offset>

- **event_id**: <unique immutable event id>
- **actor**: <runtime / logical session>
- **action**: <本阶段确实修改/调查/验证了什么>
- **observed**: <准确结果；FAIL、UNKNOWN、未运行分别说明>
- **verification**: <PASS | FAIL | NOT_RUN | UNKNOWN + 本地 evidence pointer>
- **artifacts**: <原件 / 工作快照 / 派生文件；需要时记 exact locator 和 SHA256/manifest>
- **sync**: PENDING_SYNC
- **remaining**: <真正未完成的部分和真实 blocker>
- **next**: <单个可执行下一步>

<!-- EVENT E0002 END -->

<!-- EVENT E0003 BEGIN -->

### E0003 · SYNC_ACK · <RFC3339 timestamp with UTC offset>

- **event_id**: <unique immutable event id>
- **actor**: <执行 GitHub 写回并 readback 的 Agent>
- **action**: <将 E0001–E0002 中的有效可公开/可进入 owner GitHub 的内容写回>
- **remote_ref**: <已回读的准确 GitHub comment/commit/head pointer>
- **covers_through**: E0002
- **verification**: <写回回读结果；只有实际确认才填写 PASS>
- **next**: <交给谁继续；无继续则按当前 Work terminal 合同>

<!-- EVENT E0003 END -->

<!-- EVENT E0004 BEGIN -->

### E0004 · HANDOFF_NOTE · <RFC3339 timestamp with UTC offset>

- **event_id**: <unique immutable event id>
- **from_actor**: <实际交出方>
- **candidate_to_actor**: <目标接手方；未获授权时不能写成 owner>
- **observed**: <已完成的事实、当前 worksite 和 active write-set / lease>
- **unsynced**: <尚未回写的事件列表或 NONE>
- **limitations**: <明确 UNKNOWN、LOCAL_ONLY 或其他不能重做/越界的事项>
- **next**: <新 Agent 先核验 GitHub 现行 authority、CLAIM、HEAD 和 workspace，再读取现场>

<!-- EVENT E0004 END -->

> **模板备注（实际使用时删除）**：本文件应在每个隔离 Work Context 或持久证据根部实例化，事件只在真实发生后追加。不得把示例事件、占位符或无回读的 GitHub pointer 当作发生过的证据。多 Agent 不并发编辑同一文件；本地重要事件尽可能刷盘，文件残缺尾部不构成完成证明。
