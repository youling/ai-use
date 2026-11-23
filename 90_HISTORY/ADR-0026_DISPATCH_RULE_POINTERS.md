# ADR 0026 — 每轮派工附上可直达的适用章节

- 状态：待审查
- Work：[ai-use #197](https://github.com/youling/ai-use/issues/197)
- 现行规则拟归入 [Agent Interface §1.1.1](../docs/AGENT_INTERFACE.md#111-rule-pointers-on-every-dispatch--每轮派工的规则援引)

## 背景

工作站实测中，原对话继续施工仍会遗漏规则或改写验收边界，换建造者进一步失去原会话线索。文件主页能帮助发现资料，却不能证明派发者选中了正确条款。 [实测回执](https://github.com/youling/ai-use/issues/98#issuecomment-7095680167)

## 裁决

把适用规则的直达链接放在执行者实际收到的本轮行动或验收旁。派发者负责核对治理仓、版本、锚点和适用性。后续可以从既有 dispatch 或 checkpoint 恢复该引用。派发模板示范首次、原对话返修及接任，Routing Catalog 指向规范章节。

## 取舍与验证

每轮复用少量章节链接，降低查找与错误继承的成本。整本规则只需在其本身就是必要读取时使用，例如换人先读取 L0。原 Seed 的寻址职责及 Work 的授权、归属、写域和验收沿用现行规则。已完成历史派单按当时合同解释。用[派工验收](../40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md#fixture-f1--每轮派工的章节援引)复测实际消息、章节落点和回读。
