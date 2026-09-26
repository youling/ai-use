# ADR-0009：Constitutional Semantic Integrity Gate

**Artifact Version: 1.0.0**  
状态：Decision materialization；acceptance/currentness 以 Git/GitHub exact-head Review + merge history 为准  
裁决来源：[Governance #96](https://github.com/youling/ai-use/issues/96)  
语义 owner：[Change Lifecycle](../30_PROTOCOLS/CHANGE_LIFECYCLE.md)

## Context

ai-use 把 Human、AI/session 与执行环境都视为可能失败，因此治理文本本身具有高 blast radius：一个重复 owner、混淆状态或隐含 authority 可以被多个 Agent / project 复制。已有 Issue → ADR → branch → checks → PR → exact-head Review 流程能保证 provenance，却没有要求 material normative governance Review 明确证明“语义没有漂移”。

需要增强的是 **Review 质量**，不是增加第二套审批链或把更多内容塞进 L0。

## Decision

对 material normative governance L2 change，在既有 exact-head semantic Review 中增加最小 proof obligations：

1. single semantic owner；
2. term/state separation；
3. authority conservation；
4. failure-closed meaning；
5. lifecycle closure（适用时）；
6. compatibility / supersession；
7. 至少一个 counterexample test；
8. minimum semantics / lowest stable canonical layer；
9. decidable where possible，优先 machine-observable evidence。

每项由 Review 记录 `PASS | FAIL | N/A`，其中 `N/A` 简述理由。FAIL 阻止把该 exact head 称为 semantic-review complete；修复后在新 exact head 重新 Review。

Canonical mechanics 只进入 `30_PROTOCOLS/CHANGE_LIFECYCLE.md`。本 ADR 保存长期 rationale，不复制完整执行模板；PR Review 保存本次 exact-head proof。

## Why this shape

- **不新增角色**：仍由 current contract 已要求的 Architect/Reviewer 做 exact-head semantic Review。
- **不扩大 L0**：proof obligations 只在 material governance L2 变更时触发。
- **不替代机器 checks**：schema/test/link/generated checks 继续证明机械性质，semantic Review 证明不能可靠机械化的 governance meaning。
- **不造第二 SSOT**：proof 绑定 PR exact head，并通过 pointer 连接 Issue/ADR/canonical Artifact。
- **counterexample 优先**：要求至少一个 plausible misuse，避免只证明 happy path。

## Alternatives and tradeoffs

### 把九项全部加入 L0

拒绝。它们是治理变更 Review mechanics，不是所有 Agent 在 lower layer 失效时都必须常驻的 identity/authority/truth invariant。

### 新增独立 Governance Approval Role

拒绝。会增加审批链和长期 coordination cost，而问题可在现有 exact-head Review 内解决。

### 只依赖 prose Review “看起来合理”

拒绝。缺乏可重复 proof boundary，容易漏掉 owner duplication、authority leakage 与 lifecycle gap。

### 全部要求 machine proof

拒绝。部分治理语义可以机械观测，但 canonical ownership、术语分离与 counterexample correctness 仍需要 semantic Review。

## Compatibility

- 不修改 Human sovereignty、现有 authority hierarchy 或 merge/deploy/destructive authority。
- 不改变 L0 Kernel。
- 不影响 L0 typo/format 等非语义维护。
- 不要求普通项目 L2 机械套用 governance-specific proof gate；只针对 material normative governance change。
- 既有 ADR / historical artifact 保持 provenance，不回写历史。
- 后续若 proof obligations 本身需要改变，走新的 L2 Issue/ADR/PR，而不是静默扩表。
