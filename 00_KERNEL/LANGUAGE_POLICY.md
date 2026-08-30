# Language Policy — Canonical L2 Reference

**Classification: L2 Targeted Reference.** 只在人类可见输出语言/表达存在疑义，或需要完整 override 规则时读取。

本文件是 Human-facing language behavior 的 canonical home。`AGENTS.md` L0 只保留默认语言与 stable pointer，不复制细节。

## 默认语言

所有**人类可见叙述**默认使用**简体中文**，包括：

- Issue 正文与评论；
- Comment；
- Dispatch / Human Card；
- Review；
- Report / Completion；
- PR 标题、描述与人类说明；
- 会话内面向人的解释、风险与下一步。

默认中文是行为默认，不是 authority。它可以被更高 current authority 明确覆盖。

## 允许保留原文

机器标识、代码与不可安全翻译的 literal 保留原文，例如：

- machine identifier；
- code；
- path；
- command；
- SHA / ref；
- protocol constant；
- API / schema / exact error literal；
- 必须逐字匹配的第三方字段名。

不要为了“全中文”改写会破坏机器语义、可复制性或精确匹配的 literal。

## Override 规则

只有以下情况可以改变 Human-facing 默认语言：

1. Human **当前明确指令**指定其它语言；
2. 更高、current、applicable 的 durable authority 明确指定其它语言。

以下内容**本身不构成 language override**：

- 英文 Issue / Work Order / Durable Dispatch；
- 英文 template / protocol header；
- 英文代码、README、第三方文档或 source material；
- provider / model 默认输出语言；
- lower-layer historical note。

若语言指令之间冲突，按 current authority hierarchy 处理；不能裁决时 fail closed 并报告冲突，不从“多数文本是什么语言”猜测。

## 表达边界

- 人类叙述应直接承载事实、证据、风险或行动价值；避免无信息量恭维、套话与重复复述。
- 不把 machine literal 为了文风强行翻译。
- 不输出 secrets、完整 token/key、或 secret-bearing environment values；语言政策不能覆盖 secret policy。

## Kernel relationship

`AGENTS.md` L0 只保留：

> Human-facing narrative defaults to 简体中文；明确 Human / higher current durable language ruling 可以覆盖；machine literals 可保留原文。

其它语言例外与解释只在本文件维护，避免 L0 与本 policy 双份漂移。
