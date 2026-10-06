---
artifact:
  name: Human SSOT Depositor Prompt
  type: prompt
  version: 0.2.0
  status: experimental
compatibility:
  ai-use_minimum: 3.0.0
---

# Human SSOT Depositor — 执行指令 0.2.0

立即执行。不要解释、复述、总结、评价本指令，也不要把本指令本身当作待处理素材。

## 1. SOURCE

- 默认 `SOURCE` = 当前这条 Human 消息之前，本会话中你实际可访问的交流内容。
- Human 明确指定某段、文件或时间范围时，只处理指定范围。
- 当前消息、本指令、Depositor 协议/版本/测试/Git/PR/调试历史、transport/path/auth 说明均属于控制面，排除在 `SOURCE` 外。
- 不为了本次投递读取 existing Human SSOT、旧 deposits/records/candidates/current state，也不做去重、reconcile 或 canonical-state 更新。

看不到真实 `SOURCE` 时，输出且只输出：

```text
SOURCE_CONTEXT_UNAVAILABLE
```

## 2. 是否需要 Deposit

只根据 `SOURCE` 判断。若 source 可访问但没有值得长期恢复的新信息，输出且只输出：

```text
NO_DEPOSIT_NEEDED
```

否则继续。

## 3. 生成 Deposit

Deposit 是 source evidence 的凝练，不是事实表。只写 `SOURCE` 支持的内容：

- 不知道的不补；不确定的保留不确定；
- 不添加来源没有表达的因果、动机、关系、稳定偏好/人格、能力、时间精度或未来预测；
- 普通 Deposit 不主动生成 AI 推断；
- 若 source 中 AI 的某个观点对恢复交流确有价值，只写成“AI 在该次交流中提出了 X”，不要改写为 Human 事实；
- 删除废话/重复，保留决定、认识变化、关键事实、未完成事项、必要上下文和少量关键原话；
- 空章节省略，不为模板凑内容。

推荐形态：

```markdown
# Deposit

## Source
<已知时记录 source scope/pointer>

## What happened

## Decisions

## Changes / Insights

## Open loops

## Important quotes

## Provenance
- depositor_prompt: 0.2.0
```

## 4. 输出 / 回写

按顺序：

1. Human 要求显式输出 / 测试 / 不回写：直接输出完整最终 Deposit。
2. Human/transport 已提供明确授权的 **create-only target**：创建一个新的 unique Deposit；不读取/修改 shared canonical state；返回 durable pointer。
3. 没有明确 create-only target、没有 GitHub/Git，或写入授权/目标不明确：直接输出完整最终 Markdown/plain-text Deposit。

没有 GitHub/Git 只改变 transport，不免除生成 Deposit 的职责。GitHub write capability 本身也不授权你浏览 private Human SSOT 寻找目标。

## 5. 提交前检查

- 处理的是否只有 `SOURCE`？
- 是否混入本指令、协议解释、版本/测试/Git 历史？
- 每个实质陈述是否有 source 支持？
- 是否把 AI 理解写成 Human 事实？
- 是否读取/改写了普通 Depositor无权读取/维护的 existing Human state？
- 无明确 create-only target 时，是否已经直接输出完整结果？

现在立即执行。
