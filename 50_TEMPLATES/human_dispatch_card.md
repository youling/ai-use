# Human Dispatch Card — 人类调度卡片

**分层**: Human 层（决策卡片）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 给 Human 的派发决策提示，恰好五个字段 |
| 谁使用 | Architect 填写；Human 决策 |
| 什么时候使用 | 派发任务需要 Human 决策 / 知情时 |
| 禁止用途 | 调度建议**只给 Human**，不进 Agent seed；不是 Agent 指令或状态源；不承载第二份任务合同 |

## 填空模板

```text
任务: <一句话任务标题>
为什么做: <背景 / 理由>
你要做什么: <本轮工作内容>
调度建议: <难度 / 上下文规模 / 模型建议 / 词元·时间粗估 / 并行策略 / 本轮重点>
本轮终点: <完成边界 / stop condition>
```

## 规范源

- `docs/AGENT_INTERFACE.md` §2（Human Dispatch Card 五字段顺序）