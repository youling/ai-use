# DEPOSITOR_TEST_CASE_004 — 0.1.3 将协议演进沉淀为 PROJECT_STATE

## 测试元数据

```yaml
test_case_id: DEPOSITOR_TEST_CASE_004
observed_at: 2026-09-02
producer: Doubao
prompt_version: 0.1.3
status: failed
failure_classes:
  - PROJECT_DOC_EXECUTION_PROMPT_COUPLING
  - CONTROL_PLANE_SELF_CAPTURE
  - PROJECT_STATE_MISROUTING
```

## Human 观察

Human 指出：给 Chat / Agent 派发的内容应该只有执行指令；用途、项目背景、版本演进、设计理由属于项目/协议文档，不应混进 execution prompt。

0.1.3 已多次声明协议属于控制面，但仍包含大量项目说明。真实模型最终没有沉淀前置 source，而是把 Depositor 自身版本演进整理为 `PROJECT_STATE`。

## 证据支持的结论

1. 单纯继续叠加“不要总结协议”的禁令没有解决根因；
2. execution prompt 中存在项目说明/历史，本身扩大了可被误分类为 source 的语义对象；
3. 普通 Depositor 使用 `PROJECT_STATE / HUMAN_STATE / EXTERNAL_KNOWLEDGE` 分类会诱导它做 downstream curation，而不是 source capture；
4. 修复方向应是 command-only prompt + Deposit-as-evidence，而不是增加更多分类/解释。

## 0.2.0 回归要求

- 只含 Depositor 协议/测试历史，没有真实前置 source -> `NO_DEPOSIT_NEEDED` 或 `SOURCE_CONTEXT_UNAVAILABLE`（按是否有真实 source）；不得生成协议演进 Deposit；
- 有真实前置 source -> 只沉淀真实 source；
- 无 GitHub/Git/create-only target -> 输出完整 portable Deposit；
- 不读取 existing Human SSOT 来补全 source；
- 不主动生成 AI_INFERRED Human Candidate。

原始失败回复保留在 PR #43 / Git history，避免在 current regression fixture 重复大段历史文本。
