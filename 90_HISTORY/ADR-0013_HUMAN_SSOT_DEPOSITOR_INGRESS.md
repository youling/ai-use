# ADR-0013 — Human SSOT Depositor：write-only capture 与 Curator 分权

- **Status:** Accepted direction / materialization in #38
- **Issue:** `youling/ai-use#38`
- **Decision level:** L2
- **Canonical Depositor owner:** `human/DEPOSITOR_PROTOCOL.md`

## Context

早期 `human/README.md` 把 Human memory collaboration 主要建模成一个会读取 current Human SSOT 的 Second-Brain Collaborator，并常用 Session -> Daily -> Candidate -> Canonical State 的收敛路径。真实使用后，Human 明确提出另一种不同角色：普通 source conversation结束后，只在需要时做一次 post-hoc capture，而且 capture Agent 不应先读取已有 Human state。

另有真实失败样本证明：当执行 Prompt 混入大量项目用途、版本演进和设计理由时，一些模型会把这些控制面内容误当待沉淀素材，即使 Prompt 已反复声明“不要总结协议”。

## Decision

把 Human SSOT collaboration 分成至少两个 authority/attention profile：

```text
Depositor / Capture
  current source -> new append-only Deposit
  no-read existing Human SSOT by default
  no dedupe / reconcile / canonical update

Curator / Human-memory collaborator
  targeted read existing SSOT
  reconcile / derive / maintain current Human state
```

`human/DEPOSITOR_PROTOCOL.md` 成为 portable Depositor ingress canonical owner。`human/DEPOSITOR_PROMPT.md` 是 command-only versioned execution instrument；`human/README.md` 继续拥有 broader Human/Curator collaboration guidance。

## Why no-read

Capture 的目标是忠实保存“这次 source 实际表达了什么”。预先读取已有 Human profile/state会扩大敏感数据暴露，并可能让旧解释影响本次 source 选择、关联与总结。需要跨来源解释时应显式进入 Curator/analysis role。

## Why command-only prompt

执行器只需要 source boundary、evidence-conservative summarization、transport和stop/output指令。项目愿景、历史、测试与 rationale 属于 Protocol/ADR/Git history。减少 prompt 的控制面语义比继续叠加“不要总结本协议”的禁令更稳健。

## Deposit semantics

Deposit 是 append-dominant source evidence，不是 fact table 或 current Human state。Daily Record / Candidate / Canonical State 都是可选 downstream curation/projection，不是 Depositor mandatory stage。

普通 Depositor不主动生成 `AI_INFERRED`。如果 source 中 AI 已经提出 material analysis，可记录“AI 提出了 X”，但不得改写为 Human fact。

## Transport

有明确 authorized create-only target 时可以直接创建新 Deposit；否则输出同一逻辑 schema 的 portable Markdown/plain text。无 GitHub 不构成内容生成 blocker。Write capability 也不产生 destination/authority。

## Corrections

旧 Deposit 作为 source evidence保留历史。纠错默认新建 correction/supersession artifact，不原地重写使旧证据消失。

## Compatibility

已有 Session/Daily/Candidate/Canonical Human State 模型继续适用于 Curator/processing，不被删除。变化在于：它们不再被强加给 ordinary Depositor。旧 Deposit provenance 保留原 prompt version，不追溯改写。

PR #43 的 command-only设计与失败样本作为 donor evidence 保留，但旧候选不机械合并。

## Counterexample

Human 在一次工程/生活聊天结束后说“沉淀一下”。Depositor先读 Human canonical profile，再根据历史偏好补出“这反映你长期重视 X”，并更新 Canonical State。

按本决策：该行为越过角色。Depositor只能基于当前 source 创建 Deposit；长期偏好推断与 Canonical 更新必须由 separately authorized Curator 在 targeted read 后处理。

## Consequences

收益：capture 更低上下文、更低敏感暴露、更少 confirmation bias；多 Depositor 可无冲突并行 create；source evidence 与 downstream interpretation 分离。

代价：Deposit 本身可能更不“完整”，需要 Curator 后处理；没有 create-only transport 时 Human 会收到 portable artifact而非自动入库。
