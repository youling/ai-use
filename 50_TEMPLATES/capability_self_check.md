# Capability Self Check — Agent 节点能力盘点

**分层**: Agent 层（盘点当前节点具备哪些能力）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 盘点当前 Agent 节点具备哪些能力（runtime / tools / auth / access / environment / limits），作为节点切换、设备切换、派发前的标准入口 |
| 谁使用 | 执行 Agent（Human 可用触发文本发起） |
| 什么时候使用 | Agent 切换到新节点 / 新设备、首次接入 workspace、或派发前需确认节点能否胜任时 |
| 触发文本 | `CAPABILITY_SELF_CHECK` |
| 禁止用途 | 不执行任务；不修改文件；不把发现的能力当作授权；不打印 secret 值 |

## 与 Bootstrap Check 的分工

| 检查 | 回答的问题 |
| --- | --- |
| Bootstrap Check（`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`） | 当前 Agent 是否进入正确工作状态（身份 / 入口 / 权限 / 任务 / 边界 / 状态） |
| Capability Self Check（本文件） | 当前 Agent 节点具备哪些能力 |

两者互补，不互相替代；本检查不重复定义 Bootstrap Check 的固定检查项。

## 固定盘点项

按序盘点以下 6 项：

1. **Runtime** —— model / version / thinking 等运行时标识。
2. **Tools** —— 可用工具集（git / gh / shell / filesystem 等）及关键版本。
3. **Auth** —— 认证状态（如 `gh auth status` 只输出登录态，不输出 token 值）。
4. **Access** —— 目标仓库可达性与可见性（`github-private` / `github-public` / unreachable）。
5. **Environment** —— OS / 网络 / 本地 workspace 能力（worktree / clone / 容器）。
6. **Limits** —— 已知能力边界（缺工具、无网络、只读文件系统等）；不确定写 `unknown`，不编造。

## Capability != Authority

能力发现结果只说明"能做什么"，**不得自动提升**为组织权威 / 项目权威 / 人类决策权威；
授权始终以 Work Order / Dispatch 为准（见 `AGENTS.md` Authority）。

## 触发文本

```text
CAPABILITY_SELF_CHECK
```

## 填空模板

```text
CAPABILITY_SELF_CHECK
---
scope: <当前任务 pointer 或 node 身份>
depth: <targeted | full>
```

## 完成后

生成 `CAPABILITY_SELF_CHECK_REPORT`，并**回写 durable source**（当前 authority issue / dispatch comment）。仅存在于聊天的盘点不算数。

```text
CAPABILITY_SELF_CHECK_REPORT
---
identity: <node_id>/<agent_type>/<session_id>
runtime: <model/version>
tools: <git | gh | shell | ...>
auth: <authenticated | none>
access: <owner/repo: github-private | github-public | unreachable>
environment: <os / network / workspace>
limits: <已知能力边界 | unknown>
authority_note: capability != authority；授权以 Work Order / Dispatch 为准
status: READY | BLOCKED | WAITING_FOR_HUMAN
blockers:
  - <缺失的关键能力 | none>
```

缺失关键能力时报告 `BLOCKED` / `WAITING_FOR_HUMAN`，不靠猜继续。

## 规范源

- `AGENTS.md`（Authority：Capability != Authority）
- `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（启动状态验证；与本检查互补）
- `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`（只存在聊天的确认不算数）
