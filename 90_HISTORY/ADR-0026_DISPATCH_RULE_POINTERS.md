# ADR 0026 — 每轮派工附上可直达的适用章节

- 状态：Human 已裁决，随关联 PR 合并生效
- Work：[ai-use #197](https://github.com/youling/ai-use/issues/197)
- 规则归 [Agent Interface §1.1.1](../docs/AGENT_INTERFACE.md#111-rule-pointers-on-every-dispatch--每轮派工的规则援引)

实测中，同一对话返修仍会漏读规则，换建造者则容易丢失原验收。选择把本轮适用章节贴在任务动作旁，从 L0 按角色补齐，缺失时复用现有阅读索引。这样每轮只多传必要链接。历史派单按当时合同解释。 [现场证据](https://github.com/youling/ai-use/issues/98#issuecomment-7095680167)
