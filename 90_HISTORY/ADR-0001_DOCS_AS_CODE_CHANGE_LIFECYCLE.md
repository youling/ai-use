# ADR-0001：关键文档采用 docs-as-code，低关键文档允许周期性维护

状态：Accepted  
来源 Issue：#49  
相关预研：#40

## Context

ai-use 与多个项目已经把 Markdown 用作 Agent 冷启动、规则、架构、SSOT、模板与长期协作的 durable input。此前代码天然走 branch / PR / Review，但文档经常被当成“说明附件”，导致几个问题：

- 当前文本能看到，但为什么这样改不容易恢复；
- 不同 Architect 会自行发明文档更新方式；
- 规则/Prompt/Template 的行为变化可能绕过与代码同级的审查；
- 如果把所有文档都强制重治理，又会产生明显维护税。

Assets 仓真实使用表明，关键规则文档与代码一样做 Issue / PR / Review / CI 留痕可显著降低漂移；而低关键 derived/navigation 文档更适合按周期批量更新。

## Decision

1. 代码与文档统一视为 Git Artifact；Markdown 不因是文档而免除历史、diff、Review 与回滚。
2. 文档分两种治理模式：
   - `STRICT_DOCS_AS_CODE`：规则、Prompt、Protocol、Template、Architecture、Contract、SSOT 等关键文档；
   - `PERIODIC_DOCS`：低关键、derived、navigation、presentation 类文档，可周期性批量维护。
3. 所有变更按影响分级：
   - L0：无语义变化，branch -> PR -> Review -> merge；
   - L1：实质语义/行为/事实变化，Issue -> branch -> checks -> PR -> exact-head Review -> merge；
   - L2：authority / stable ID / schema / SSOT ownership / lifecycle / 长期 contract 等架构变化，在 L1 流程上增加 ADR。
4. 周期性文档一旦触及 canonical / normative / authority / schema / ownership / compatibility 语义，必须升级到 STRICT 的 L1/L2。
5. Issue 保存本轮 rationale / acceptance；ADR 保存长期裁决与取舍；PR 保存 exact diff 与验证；Git 保存演化历史。不要在多处复制完整正文。
6. `ai-use` 自身治理文档默认采用 `STRICT_DOCS_AS_CODE`。

## Alternatives

### A. 所有 Markdown 一律重治理

未采用。优点是统一，缺点是 README、derived view、状态摘要等低价值刷新也产生大量 Issue/ADR 仪式，Human/Agent 维护成本过高。

### B. 文档继续按普通附件维护，只有代码严格 PR

未采用。对 AI-native 项目不成立：Prompt、Protocol、Architecture、Template 本身就会改变 Agent 行为，风险不低于代码。

### C. 每个项目自己定义完全不同的文档流程

未采用。局部可调整强度，但没有共同分级会让跨项目 Architect 反复重新学习，并产生格式漂移。

## Consequences

正向：

- 关键文档获得可审查、可回滚、可追因的生命周期；
- 文档/代码共享一套变更语言；
- Project Architect 可以按重要性控制治理成本；
- 未来 Agent 可以从 Issue -> ADR -> PR -> Git history 恢复“为什么变成现在这样”。

代价：

- L1/L2 关键文档会增加 Issue/Review 开销；
- Project Architect 需要判断 STRICT/PERIODIC 与 L0/L1/L2；
- 错误降级仍可能发生，因此模糊情况默认不降级。

## Supersedes / Superseded by

无。
