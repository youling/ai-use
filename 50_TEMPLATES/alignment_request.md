# Alignment Request — 对齐确认请求

**分层**: 双方协作（请求方 = Agent / Architect；确认方 = Human）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 在执行重大 / 不确定 / 边界模糊动作前，请求 Human 对齐目标、scope、优先级或风险 |
| 谁使用 | Agent / Architect 作为请求方；Human 作为确认方 |
| 什么时候使用 | scope 边界模糊、优先级冲突、跨职责边界、动作超出已授权范围、或建议可能被误读为要求时 |
| 禁止用途 | 不为小事 / 已授权动作打断（minimum sufficient）；不把建议静默升级为要求；确认后仍不得越权执行未授权动作 |

## 填空模板

```text
ALIGNMENT REQUEST
---
当前理解: <对目标 / scope / 优先级的陈述>
决策点: <需要 Human 拍板的具体项>
备选: <选项 + 各自风险>
请求确认: <确认项>
待确认期间: <不动作 / 只做只读探索>
```

## 规范源

- `CONSTITUTION.md` §1（Human sovereignty；建议不得静默升级）
- `AGENTS.md` Authority（区分"用户要求 / 项目约束 / 你的建议"）