# Bootstrap Check Request — 初始化状态检查请求（Human 触发）

**分层**: Human 层（请求 Agent 执行初始化状态检查）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | Human 请求 Agent 执行一次初始化状态检查，确认 current bootstrap 是否就绪 |
| 谁使用 | Human（发起）；执行 Agent / Architect 接收并执行 Bootstrap Check |
| 什么时候使用 | 首次进入、跨设备/会话恢复、takeover，或怀疑 current state 与 durable source 不一致时 |
| 触发文本 | `BOOTSTRAP_CHECK` |
| 禁止用途 | 不补充历史上下文；不执行当前业务任务；不把聊天/provider memory 当 durable completion；不因没有既存 Issue 就猜一个 authority source |

## 要求

- 按 current `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` 完成 `BOOT-1 -> BOOT-2 -> BOOT-3`；
- 只读取 current target/role 所需上下文，不为恢复默认扫描整个 workspace；
- 检查过程本身不施工业务代码/功能；
- Fresh/takeover Architect 只有在 required report 已进入 current writable durable anchor 后，才可声称 durable cold-start complete / `EXECUTION_ALLOWED`。

## 触发文本

```text
BOOTSTRAP_CHECK
```

## 完成后

生成 `BOOTSTRAP_CHECK_REPORT` / `ARCHITECT_BOOTSTRAP_REPORT`，写回**当前 deployment 可写且具 current 语义的 durable anchor**，例如：

- current authority/bootstrap Issue 或 dispatch source；
- workspace 初始化阶段的 current governance repo durable bootstrap/registry anchor；
- deployment-local control-plane 中已存在的 current authority anchor。

不要把上游维护者 private repo 当默认 writeback target，也不要求“必须已经有 dispatch comment”才能完成第一次 workspace bootstrap。若确实没有任何可写 durable anchor，则按协议报告 `BOOTSTRAP_VALID_SESSION_LOCAL`，不得用聊天声明替代。

## 填空模板

```text
BOOTSTRAP_CHECK
---
source: <current durable source pointer | workspace-bootstrap>
startup_mode: <Fresh Role | Warm Resume | Takeover>
governance_repo: <owner/repo>
control_plane_repo: <workspace_registry.control_plane.repo | none-if-not-yet-registered>
```

## 规范源

- `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（Ordered Bootstrap、durable writeback、continuation）
- `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`（首次 workspace role registration）
- `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`（只存在聊天的确认不算数）
