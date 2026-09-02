# Human SSOT Depositor 协议说明

## 定位

`human/DEPOSITOR_PROMPT.md` 是给 Chat / Agent 直接派发的**执行指令**，不是项目说明书。

本文件才承载 Depositor 的项目用途、设计理由、演进记录和调试结论。

## 核心分层

```text
项目文档 / 治理说明
  -> 解释为什么这样设计
  -> 面向 Architect / Maintainer / Reviewer

DEPOSITOR_PROMPT.md
  -> 只包含立即执行所需指令
  -> 面向被临时调用的 Chat / Agent
```

派发 Prompt 不应包含：

- 项目愿景；
- 设计背景；
- 版本演进叙述；
- 调试历史；
- 口号或解释性段落；
- 为 Architect 准备的 rationale。

原因不是这些内容无价值，而是它们会扩大模型的候选语义空间，使某些模型把“关于 Depositor 的知识”误当成“待 Depositor 处理的数据”。

## Depositor 职责

Depositor 只负责：

1. 确定当前允许处理的 source scope；
2. 排除控制面；
3. 判断是否值得保存；
4. 对来源支持的内容做凝练；
5. 按当前 transport 能力回写或显式输出；
6. 记录 Prompt 版本 provenance。

Depositor 不负责：

- 项目状态归档；
- Prompt 测试结果归档；
- Prompt 版本演进总结；
- 人格推断；
- 长期模式发现；
- 多条 Deposit 的去重、融合和 Current 更新。

这些工作由 Architect / Processor / Maintenance Agent 等后续角色完成。

## 为什么 0.2.0 改为 command-only

0.1.x 的真实测试连续暴露同一类问题：

- 模型能复述“协议属于控制面”，但仍会总结协议；
- 模型会把版本演进归类为 `PROJECT_STATE`；
- 越多解释性内容，越容易触发“总结当前文本”的默认行为。

因此 0.2.0 不再继续给 Prompt 增加更多解释和禁止条款，而是直接减少输入：

> 给执行模型的 Prompt 只保留完成任务所必需的命令。

这属于接口层收缩，不代表项目文档减少。

## Transport 规则

- 有 GitHub/Git 能力且当前写入授权明确：新建 Deposit，返回 durable pointer；
- Human 明确要求显式输出 / 测试 / 不回写：直接输出完整 Deposit；
- 无 GitHub/Git 能力或写入授权不明确：直接输出完整 Deposit。

因此 transport 与语义处理分离：没有 GitHub 只影响结果送到哪里，不影响 Depositor 是否完成总结。

## 测试证据

回归样本保存在 `human/tests/`。

已知失败序列：

- `DEPOSITOR_TEST_CASE_001`：prompt-only scope confusion；
- `DEPOSITOR_TEST_CASE_002`：0.1.1 将协议自身归类为外部知识；
- `DEPOSITOR_TEST_CASE_003`：0.1.2 已识别控制面规则但仍总结协议；
- `DEPOSITOR_TEST_CASE_004`：0.1.3 将协议迭代历史沉淀为 `PROJECT_STATE`，暴露“项目说明与执行指令混装”问题。

Prompt 版本治理见 `human/PROMPT_VERSIONING.md`。