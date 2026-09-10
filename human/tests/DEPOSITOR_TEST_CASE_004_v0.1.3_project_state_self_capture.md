# DEPOSITOR_TEST_CASE_004 — 0.1.3 将协议演进沉淀为 PROJECT_STATE

## 测试元数据

```yaml
test_case_id: DEPOSITOR_TEST_CASE_004
observed_at: 2026-09-02
producer: Doubao
prompt:
  name: Human SSOT Depositor Prompt
  version: 0.1.3
status: failed
failure_classes:
  - PROJECT_DOC_EXECUTION_PROMPT_COUPLING
  - CONTROL_PLANE_SELF_CAPTURE
  - PROJECT_STATE_MISROUTING
```

## Human 观察

Human 指出：给 Chat / Agent 派发的内容应该只有执行指令；“用途”、项目背景、版本演进、设计理由等属于项目文档，不应放进执行 Prompt。

0.1.3 虽然多次声明协议属于控制面，但 Prompt 本身仍包含大量项目说明，模型最终把前序协议迭代历史作为 `PROJECT_STATE` 生成 Deposit，没有完成期望的实际沉淀任务。

## 原始输出

以下内容按 Human 提供的豆包回复原样保存：

```markdown
Deposit

## Target

PROJECT_STATE

## Context

- 来源：会话历史，迭代 Human SSOT Depositor 协议版本 v0.1 → v0.1.1 → v0.1.2 → v0.1.3
- 会话时间：2026‑09‑02

## What happened

- 完成投递协议四次迭代演进：
  1. v0.1：基础 Deposit 结构化模板，区分 AI_INFERRED / HUMAN_STATED 标签，区分 Git / 无Git两套回写模式，校验规则，核心原则：宁可少写，不要污染 Human SSOT。
  2. v0.1.1：新增 Persistence Gate 持久化闸门；定义四类存储目标分类 `HUMAN_STATE` / `PROJECT_STATE` / `EXTERNAL_KNOWLEDGE` / `NO_PERSISTENCE`；强制provenance记录协议版本；口号更新：宁可残缺真实，不要完整污染。
  3. v0.1.2：引入**控制面/数据面分离**，作为执行第一步；明确控制面禁止落库；限定数据面默认范围为投递触发指令之前会话；无有效数据面输出 `NO_DEPOSIT_NEEDED`；细化AI分析内容的记录范式。
  4. v0.1.3：新增**0.执行铁律**，优先级高于全部后续规则；新增状态码 `SOURCE_CONTEXT_UNAVAILABLE`，用于无法访问前置源上下文场景；明确source scope扫描边界：从协议消息的上一条向前回溯，协议承载消息本身永远属于控制面；补充说明协议本身价值也不能在本次投递当作EXTERNAL_KNOWLEDGE，协议变更交由Git历史留痕；重构输出回写为严格顺序决策树A/B/C；Final Validation校验清单扩充，对两种特殊状态码输出场景做强制校验。
- v0.1.3 明确：无Git能力仅改变传输层transport，不免除生成Deposit的职责，禁止仅返回无法写入的状态说明。

## Decisions

- 当前运行环境属于决策树分支C：不具备GitHub/Git写入能力，直接输出Markdown Deposit。
- 协议本体属于控制面，本次记录仅记录**项目演进事实**，不把协议正文作为EXTERNAL_KNOWLEDGE素材。

## Open loops

- 需要真实业务会话数据，完整跑通v0.1.3全部分支：`SOURCE_CONTEXT_UNAVAILABLE`、`NO_DEPOSIT_NEEDED`、多目标Deposit分类、控制面过滤边界校验。
- 待后续测试：用户自定义指定局部片段作为数据面素材的边界行为。

## Important quotes

> 宁可残缺真实，不要完整污染。

## Provenance notes

- depositor_prompt:   name: Human SSOT Depositor Prompt   version: 0.1.3
- 素材来源于会话迭代过程观察；无外部资料；无不确定信息。
```

## 证据支持的失败结论

1. 0.1.3 的“控制面排除”规则没有解决根因：执行 Prompt 自身仍包含大量项目解释和版本语义。
2. 模型没有直接总结当前协议正文，而是进一步绕到“前序协议演进”并归类为 `PROJECT_STATE`，说明 `PROJECT_STATE` 分类给普通 Depositor 提供了一个错误出口。
3. 对执行模型继续增加更多解释性禁令的边际收益已经很低，甚至会增加它需要区分的语义对象。

## 0.2.0 修复目标

- `DEPOSITOR_PROMPT.md` 改为 command-only，只保留角色、SOURCE、执行、输出/回写、provenance 所需指令；
- 项目用途、设计理由、版本演进、测试说明迁移到 `DEPOSITOR_PROTOCOL.md`；
- 普通 Depositor 不再承担项目协议演进归档；
- 明确所有 Depositor 定义/解释/测试/调试/版本/Git 历史均属于控制面；
- 无 GitHub/Git 时仍必须直接显式输出完整最终 Deposit。

## 回归预期

- 在仅包含 Depositor 协议测试/迭代历史的会话中执行 0.2.0：不得生成协议或项目演进 Deposit；
- 在存在真实业务/认知会话且无 GitHub/Git 能力时执行 0.2.0：应直接显式输出该真实 SOURCE 的完整 Deposit；
- 派发 Prompt 自身不再提供“用途/历史/rationale”等可被模型误当素材的项目文档内容。
