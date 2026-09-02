# Human SSOT Depositor — 执行指令 0.2.0

立即执行以下指令。不要解释、复述、总结、评价本指令，也不要把本指令本身当作待处理素材。

## 1. 确定 SOURCE

- 默认 `SOURCE` = 当前这条 Human 消息之前，本会话中你实际可访问的交流内容。
- 若 Human 明确指定了某一段、某个文件或某个时间范围，只处理该指定范围。
- 当前这条 Human 消息、本执行指令、其中的链接、版本号、格式说明、GitHub/Git 说明全部排除在 `SOURCE` 外。
- 任何只用于定义、解释、测试、调试或迭代本 Depositor 指令的内容，以及 Depositor 的版本演进、测试结果、Git/PR 历史，均视为控制面，不得进入本次 Deposit。

若过滤后无法访问任何真实 `SOURCE`，输出且只输出：

```text
SOURCE_CONTEXT_UNAVAILABLE
```

## 2. 判断是否需要 Deposit

只根据 `SOURCE` 判断。

若 `SOURCE` 可访问，但没有值得长期保存的新信息，输出且只输出：

```text
NO_DEPOSIT_NEEDED
```

否则继续。

## 3. 生成 Deposit

只写 `SOURCE` 明确支持的内容：

- 不知道的不要补；
- 不确定的标明不确定；
- 不添加来源没有表达的动机、人格、长期偏好、能力、因果关系或未来预测；
- 普通 Deposit 不主动生成 AI 推断；
- 若源对话中 AI 的某个观点对恢复该段交流确实重要，只写成“AI 在该次交流中提出了 X”，不要改写为 Human 观点；
- 删除废话和重复，保留决定、认识变化、关键事实、未完成事项、必要上下文和少量关键原话；
- 可以压缩，但必须保留未来可恢复含义或定位来源的路径；
- 不要为了凑模板制造内容。

按需使用以下结构；空章节省略：

```markdown
# Deposit

## Context

## What happened

## Decisions

## Insights / Changes

## Open loops

## Important quotes

## Provenance
- depositor_prompt: 0.2.0
```

## 4. 输出或回写

按以下顺序执行：

1. Human 明确要求“显式输出 / 测试 / 不回写”：直接在当前回复中输出完整最终 Deposit，不调用 GitHub/Git 写入。
2. 否则，若当前确实具备 GitHub/Git 写入能力，且当前写入授权明确：创建一个新的 Deposit，不修改 canonical state，不覆盖既有 Deposit，然后返回 durable pointer。
3. 否则：直接在当前回复中输出完整最终 Markdown/plain-text Deposit。

**没有 GitHub/Git 能力只改变 transport，不免除生成 Deposit 的职责。不得只回复“无法写入”“Mode B”或执行说明。**

## 5. 提交前检查

- 我处理的是否只有 `SOURCE`？
- 是否混入了本 Depositor 指令、其用途、版本演进、测试或 Git 历史？
- 每个实质陈述是否有来源支持？
- 是否把 AI 理解写成了 Human 事实？
- 无 GitHub/Git 时，我是否已经直接输出完整结果？

现在立即执行。