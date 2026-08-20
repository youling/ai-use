# Durable Dispatch — 持久派发评论

**分层**: Architect 层（durable 源）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 在 Work Order 上发布 `ARCHITECT_*_DISPATCH` 评论，携带任务知识（角色 / 启动元数据） |
| 谁使用 | Project Architect |
| 什么时候使用 | 每次 Agent-facing 执行派发；位于 Human seed 之前 |
| 禁止用途 | 不复制进 seed；不替代 Work Order（scope / acceptance 已在 Work Order，不重复）；不承担调度建议（调度建议只进 Human Dispatch Card） |

## 填空模板

```text
ARCHITECT_<ROLE>_DISPATCH
---
work_coordinate: <owner/repo>#<issue>@<step>
role: <Builder | Verifier | Research | Repair | Release>
startup_mode: <Fresh Builder | Warm Resume | Fresh Verifier | ...>
<按任务需要补充字段，非强制全集>
```

> 派发前确认 durable source 足以让 fresh Agent 执行；seed 不替代本评论。

## 规范源

- `docs/AGENT_INTERFACE.md` §1 / §1.1（Durable Dispatch Comment）