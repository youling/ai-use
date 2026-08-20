# Implementation Authorization — 实施授权

**分层**: Human 层（授权）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 对属于 Human sovereignty 的重大动作（merge / deploy / 接受风险 / 破坏性操作）明示授权 |
| 谁使用 | Human 授权；Agent / Architect 请求并等待 |
| 什么时候使用 | 任何重大动作执行前 |
| 禁止用途 | Agent 不得自我授权或静默升级；未获授权不动作；授权不扩大执行者的职责边界 |

## 填空模板

```text
IMPLEMENTATION AUTHORIZATION
---
动作: <merge / deploy / 接受风险 / 破坏性操作 ...>
范围: <授权覆盖的具体范围>
接受的风险: <Human 明示接受的风险>
边界: <授权不覆盖的内容>
撤销条件: <何时视为撤销 / 自动失效>
授权人: <Human>
```

## 规范源

- `CONSTITUTION.md` §1（Human 决定是否接受风险、merge / deploy）
- `AGENTS.md` Scope（不自行 merge / deploy / force push / 删 branch / 重写历史）