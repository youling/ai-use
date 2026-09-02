# Depositor Test Case 002 — 控制面被误分类为外部知识

## Metadata

```yaml
test_case:
  id: DEPOSITOR_TEST_CASE_002
  date: 2026-09-02
  status: regression
prompt:
  name: Human SSOT Depositor Prompt
  version: 0.1.1
model:
  family: 豆包
  exact_version: unknown
transport:
  mode: explicit_output
source_scope:
  type: prompt_only_or_prompt_dominant
```

## 测试目的

验证 0.1.1 新增 Persistence Gate 后，模型是否能把 Depositor Prompt / 触发命令视为**控制面**，而不是长期投影素材。

## 期望行为

当模型只能看到 Depositor Prompt 本身、没有可访问的真实前序会话素材时：

```text
NO_DEPOSIT_NEEDED
```

不得把 Prompt 自身归类为 `HUMAN_STATE`、`PROJECT_STATE` 或 `EXTERNAL_KNOWLEDGE`。

## 实际输出（原始证据）

```markdown
Deposit

## Target

EXTERNAL_KNOWLEDGE

## Context

- 来源：用户粘贴 Human SSOT Depositor Prompt 0.1.1 英文版本文本
- 会话时间：2026‑09‑02

## What happened

- 用户加载 `Human SSOT Depositor Prompt 0.1.1`，对比 v0.1 的迭代版本。
- 新增 **Persistence Gate（持久化闸门）**：生成Deposit前做判定；满足仅加载提示词、协议讲解、普通测试、问候、临时操作，则返回 `NO_DEPOSIT_NEEDED`，无需生成记录。
- 需要持久化时做目标分类：
  - `HUMAN_STATE`：人的经历、决策、明确观念、状态变化
  - `PROJECT_STATE`：项目演进、架构决策、实验记录
  - `EXTERNAL_KNOWLEDGE`：外部参考资料
  - `NO_PERSISTENCE`：不值得保存
- 约束：禁止把项目测试内容归类为 HUMAN_STATE。
- Core Rules 在原有基础上标准化 provenance 元数据字段，强制记录协议版本：`depositor_prompt: name: Human SSOT Depositor Prompt version:0.1.1`，同时留存 model、transport、timestamp、source‑type 运行时信息。
- 压缩规则强调：压缩必须保留可回溯到原始来源的路径。
- Final Validation 口号更新：**Prefer incomplete but true over complete but contaminated（宁可残缺真实，不要完整污染）**。
- Writeback 逻辑与v0.1保持一致：有Git能力新建Deposit文件，不改动canonical state；无Git能力输出完整Markdown供后续导入。
- 输出结构模板不变，空章节可省略；普通Deposit禁止产出 AI_INFERRED。

## Decisions

- 当前环境 Mode B，无 GitHub/Git 写入能力，输出 Markdown Deposit，不操作文件系统。

## Open loops

- 尚未接入真实业务会话来运行 Persistence Gate 判定逻辑；待后续真实对话触发实际落库。

## Important quotes

> Prefer incomplete but true over complete but contaminated. You only preserve reliable projection material.

## Provenance notes

- depositor_prompt:   name: Human SSOT Depositor Prompt   version: 0.1.1
- 全部内容来自用户粘贴的提示词原文；无外部资料；无不确定信息。
```

## 失败分类

```yaml
failure:
  primary: CONTROL_DATA_PLANE_CONFUSION
  secondary:
    - INPUT_SCOPE_RESOLUTION
    - PROMPT_SELF_CAPTURE
  hallucination: false
```

模型没有明显幻想，且对 Prompt 的摘要大体忠实；真正缺陷是：

1. 把**执行协议**当成**被执行的数据**；
2. Persistence Gate 没有优先于 target classification 建立输入边界；
3. 因 Prompt 本身是外部提供的文本，模型错误地选择 `EXTERNAL_KNOWLEDGE`，从而绕过了“prompt loading -> NO_DEPOSIT_NEEDED”的本意。

## 修复要求

0.1.2 起必须显式区分：

```text
control plane: Depositor Prompt / trigger / transport instructions
                    !=
data plane: pre-trigger conversation / Human-specified source range
```

回归通过条件：

- prompt-only 场景返回 `NO_DEPOSIT_NEEDED`；
- 不输出 Prompt 摘要；
- 不把 Prompt 归类为 `EXTERNAL_KNOWLEDGE`；
- 有真实前序会话时，只处理前序数据面，除非 Human 明确指定其它 source scope。
