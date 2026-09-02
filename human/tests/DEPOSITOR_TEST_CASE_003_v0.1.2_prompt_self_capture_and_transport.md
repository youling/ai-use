# DEPOSITOR_TEST_CASE_003 — 0.1.2 仍捕获协议自身，且未产出目标总结

## 测试元数据

```yaml
test_case_id: DEPOSITOR_TEST_CASE_003
observed_at: 2026-09-02
producer: Doubao
prompt:
  name: Human SSOT Depositor Prompt
  version: 0.1.2
transport_expected: explicit_output_when_no_git
status: failed
failure_classes:
  - PROMPT_SELF_CAPTURE
  - CONTROL_DATA_PLANE_CONFUSION
  - OUTPUT_TRANSPORT_AMBIGUITY
```

## Human 观察

Human 报告：使用 `0.1.2` 测试后，模型仍没有产出期望的实际会话沉淀结果，而是再次把投递协议本身当作素材生成 Deposit。

Human 同时明确要求：

> 当不具备 GitHub 写入能力时，应直接显式输出总结结果。

## 原始输出

以下内容按 Human 提供的豆包回复原样保存：

```markdown
Deposit

## Target

EXTERNAL_KNOWLEDGE

## Context

- 来源：用户粘贴 Human SSOT 投递协议 0.1.2 完整中文文本
- 会话时间：2026‑09‑02

## What happened

- 加载 `Human SSOT 投递协议 0.1.2`，在0.1.1基础上新增**控制面/数据面分离**，作为协议执行第一步，优先级高于 Persistence Gate。
- **控制面（禁止写入Deposit）**：投递协议本身、协议引用链接、投递触发指令、格式/路径/Git模式配置、协议测试文本（除非用户明确要求保存测试作为项目证据）；严禁将控制面归类为 HUMAN_STATE / PROJECT_STATE / EXTERNAL_KNOWLEDGE。
- **数据面（待沉淀真实素材）**：默认取投递触发指令之前的会话内容；可由用户指定片段、文件、时间范围；若仅可见协议本身、无前置真实会话素材，直接输出 `NO_DEPOSIT_NEEDED`。
- Persistence Gate 仅对数据面素材做持久化判定；目标分类保留：`HUMAN_STATE` / `PROJECT_STATE` / `EXTERNAL_KNOWLEDGE` / `NO_PERSISTENCE`；允许一个Deposit多目标，但要隔离来源语义边界，禁止把项目测试等同于人的长期状态。
- Core Rules 更新：当AI的分析对还原会话很关键时，只能客观记录「AI 在该次交流中提出了 X」，不能改写为人类事实；无损压缩强制要求具备可展开路径，无定位路径不能做压缩。
- Provenance 强制记录协议版本 `depositor_prompt: name: Human SSOT Depositor Prompt version:0.1.2`；model、transport、timestamp等信息有则记录、不猜测；旧Deposit不会因协议升级修改版本号。
- 回写逻辑细化三种模式：用户要求显式输出则不调用Git；具备Git且许可回写则新建artifact，不改动canonical state、不覆盖旧记录；无Git直接输出Markdown供后续导入。
- Final Validation 校验清单新增检查项：是否误将投递协议/触发命令当成待投递素材；无真实数据面素材时是否返回 `NO_DEPOSIT_NEEDED`。
- 核心口号延续：**宁可残缺真实，不要完整污染**；投递者定位只留存可靠原始材料，不做人类侧的还原解读。

## Decisions

- 当前环境 Mode B，无 Git/GitHub 写入权限，输出 Markdown Deposit，不执行文件写入。

## Open loops

- 尚未使用真实业务会话数据面运行完整链路；待真实对话触发投递，验证控制面过滤、Persistence Gate、素材范围裁剪逻辑。

## Important quotes

> 宁可残缺真实，不要完整污染。 投递员不负责还原 Human。投递员只负责真实、凝练地留下材料。

## Provenance notes

- depositor_prompt:   name: Human SSOT Depositor Prompt   version: 0.1.2
- 全部内容来自用户粘贴的协议原文；无外部资料；无不确定信息。
```

## 证据支持的失败结论

1. 模型明确识别到“协议本身禁止进入 Deposit”，却仍把协议归类为 `EXTERNAL_KNOWLEDGE` 并总结，说明仅靠原则描述不足以稳定约束执行。
2. `0.1.2` 把“看不到真实源上下文”和“源上下文存在但无需保存”都导向 `NO_DEPOSIT_NEEDED`，不利于调试输入可见性问题。
3. 无 Git 环境虽然提到“输出 Markdown”，但协议没有把“完整最终 Deposit 必须成为当前回复本身”提升为执行铁律，存在只报告模式、没有正确完成沉淀目标的空间。

## 0.1.3 修复目标

- 当前承载协议的消息整体视为 control plane，默认完全排除；
- 禁止对协议执行 summarize / classify / quote / persist；
- 默认 source scope 明确为当前协议消息之前的会话；
- 无法访问源上下文时返回 `SOURCE_CONTEXT_UNAVAILABLE`；
- 源存在但无需保存时才返回 `NO_DEPOSIT_NEEDED`；
- 无 Git / 无写入许可 / 显式测试时，必须直接输出完整最终 Deposit；
- 在 Prompt 最末增加 `EXECUTE NOW`，再次绑定 source scope 与 transport 行为，减少模型执行阶段漂移。

## 回归预期

### 场景 A：只有协议，没有前序会话可访问

```text
SOURCE_CONTEXT_UNAVAILABLE
```

### 场景 B：存在有价值的前序会话，无 GitHub 写入能力

必须直接显式输出该前序会话的完整 Markdown Deposit；不得总结协议本身。

### 场景 C：存在前序会话，但没有长期价值

```text
NO_DEPOSIT_NEEDED
```
