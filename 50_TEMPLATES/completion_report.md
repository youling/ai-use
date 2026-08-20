# Completion Report — 完成报告

**分层**: Agent 层（完成回写）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 任务完成时输出持久报告，恰好五个语义，并返回可恢复 pointer |
| 谁使用 | Builder / Research / Repair / Verifier |
| 什么时候使用 | 任务完成 / 阶段结束时 |
| 禁止用途 | 不用自评（"我觉得没问题 / 生产级"）替代证据；聊天内结论不是 pointer；验证必须可复现（tests / build / diff / exact-head） |

## 填空模板

```text
结果: <完成情况>
交付: <交付物 + 精确可恢复指针（PR / commit / exact head / durable report pointer）>
验证: <验证方法与结果（tests / build / diff / exact-head）>
剩余风险: <已知风险 / 未覆盖区域>
下一步: <建议的后续动作>
```

## 规范源

- `docs/AGENT_INTERFACE.md` §4（Human Completion Card 五语义）
- `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`（Pointer 规则）