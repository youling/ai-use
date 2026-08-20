# Bootstrap Check Request — 初始化状态检查请求（Human 触发）

**分层**: Human 层（请求 Agent 执行初始化状态检查）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | Human 请求 Agent 执行一次初始化状态检查，确认当前启动状态是否就绪 |
| 谁使用 | Human（向 Agent 发起）；执行 Agent 接收并执行 Bootstrap Check |
| 什么时候使用 | 首次进入、跨设备/会话恢复、或怀疑当前状态与 durable source 不一致时 |
| 触发文本 | `BOOTSTRAP_CHECK` |
| 禁止用途 | 不补充历史上下文；不执行任务；不修改文件；只验证当前初始化状态 |

## 要求

- 不补充历史上下文；
- 不执行任务；
- 不修改文件；
- 只验证当前初始化状态。

## 触发文本

```text
BOOTSTRAP_CHECK
```

## 完成后

生成 `BOOTSTRAP_CHECK_REPORT`，并**回写 durable source**（当前 authority issue / dispatch comment）。

## 填空模板

```text
BOOTSTRAP_CHECK
---
source: <durable source pointer>
startup_mode: <Fresh Role / Warm Resume>
```

## 规范源

- `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（固定检查项、可回写要求）
- `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`（只存在聊天的确认不算数）
