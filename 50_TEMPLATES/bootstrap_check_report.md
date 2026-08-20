# Bootstrap Check Report — 启动核验报告

**分层**: Agent 层（启动后回写）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | fresh Agent 启动完成核验后，向 durable source 回写启动状态与缺口 |
| 谁使用 | 执行 Agent（Builder / Verifier / Research / Repair） |
| 什么时候使用 | Fresh Agent 冷启动完成 Bootstrap Check 时；**必须回写 durable source**，仅聊天确认不算数 |
| 禁止用途 | 不承载完整任务知识 / 执行计划（那是 dispatch 的职责）；不用自评替代证据；状态冲突不靠猜，报告 `BLOCKED` |

## 填空模板

```text
BOOTSTRAP CHECK REPORT
---
node: <node_id>/<agent_type>/<session_id>
work: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>

1. Identity      : <确认>
2. Entry Point   : <已定位 pointer / ref>
3. Authority     : <范围确认>
4. Access        : <与 live metadata 一致，或报告 drift>
5. Active Mission: <Work Order + 当前状态>
6. Boundary      : <owns / forbidden / acceptance>
7. State         : <durable / live 一致，或冲突>

结论: <READY_TO_EXECUTE | BLOCKED + 原因>
回写: <comment id / durable pointer>
```

## 规范源

- `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（输出与可回写要求）
- `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`（只存在聊天的确认不算数）