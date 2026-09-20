# ADR-0004：Recovery / Routing Single Source

**Artifact Version: 1.0.0**
状态：Accepted / exact-head reviewed
裁决：[Global Architect #73 freeze](https://github.com/youling/ai-use/issues/73#issuecomment-5749622582)
实施：[R1/R2 Work Order #74](https://github.com/youling/ai-use/issues/74)
验收：[PR #75 Global Architect review 5260926445](https://github.com/youling/ai-use/pull/75#pullrequestreview-5260926445)

## Context

旧公开入口同时路由到 current Bootstrap 与要求旧方 artifact、人工确认的 Fast Restore/handoff 流程；一个健康的 crash takeover 需要先读旧流程再隔离冲突。context 的稳定枚举与 delegation 边界实际驻留模板，导致“协议拥有语义”与真实消费者不一致。三份导航重复解释同一套 applicability，扩大 cold-start 成本与 drift 风险。[#69 审计](https://github.com/youling/ai-use/issues/69#issuecomment-5749535827) 提供问题证据，审计本身不授予规范 authority。

## Decision

1. [Routing Catalog](../ROUTING_CATALOG.yaml) 是 scene/applicability、reading level/role trigger、canonical pointer 和 compatibility/derived-view metadata 的单一解释边界。它不拥有 authority、scope/acceptance、private topology、live work facts 或 protocol mechanics。
2. `START_HERE.md`、`READING_MAP.md`、`NAMESPACE.md` 和小型 route index 是该目录的投影；生成器负责形态，canonical 协议保留 semantic ownership。L0 的入口指针与 `00→90` 链保持兼容，可 targeted/short-circuit，不能变成 mandatory full-read。
3. [Recovery & Handoff](../30_PROTOCOLS/RECOVERY_HANDOFF.md) 区分 `PLANNED_TRANSFER`、`CRASH_TAKEOVER_OR_OLD_CONTEXT_UNAVAILABLE`、`HOT_OR_WARM_RESUME`。计划交接保留适用合同的 handoff 要求；crash 在 current authority 和可恢复 durable state 足够时，不以缺失旧 context/handoff 作为 blocker；warm 复用有效 owned context。current live state 高于旧 checkpoint，不以新的 Human prompt 作为替换崩溃 context 的仪式门。
4. `protocol = semantics`，`template = copyable shape`。稳定 context 枚举、recovery/independence/delegation 等 accepted semantics 搬入协议，模板与消费者指向其 home；continuation/repair/completion 仍归 Agent Interface。
5. current public copyable surfaces 使用 inert coordinates。实例 registration/topology 留在 private owner/control plane；更完整 storage/ownership doctrine 属于 [#66](https://github.com/youling/ai-use/issues/66)，本次不重复建立。
6. evidence/canary 必须经 reviewed interpretation、explicit governance decision 才能进入 normative artifact。Capability Lab schema/promotion 属于 [#68](https://github.com/youling/ai-use/issues/68)，本次不建立 Lab。
7. 旧路径保留 thin forward、compatibility projection 或明确 retired/historical 身份；旧正文通过 frozen Git provenance 保留。旧 provider guide 失去 live instruction 地位，不重写 Git history。

## Alternatives and tradeoffs

继续在三个入口和模板各补一个“current rules 优先”说明，编辑量较小，但读者仍需先摄入冲突规则；不采用。删除全部旧路径能消除文本，但会断开既存 anchors 与历史来源；采用 forward compatibility。

选用 YAML 1.2 的 JSON 子集可直接用 Python 标准库解析，无需为文档引入依赖框架。代价是目录源较长；Human/Agent 使用短投影，无需再通读源。生成检查能证明路径/投影一致，不能证明 scene 语义合理或模型阅读正确，所以仍需五类 isolated fresh-reader evidence 与 exact-head Global Review。

## Compatibility, staging and rollback

此次仅 R1 recovery/current-entry 与 R2 catalog/projections。R3（#66/#67、Durable Data、Diagram refinement）、R4（#68 Lab）、R5（platform-enforcement canary）继续 HOLD。`AGENTS.md` 字节与语义不变，不改 main/admin/rulesets，不新增 L0 mechanics。

结构改动留在 feature branch，以 [migration map](../docs/migrations/R74_RECOVERY_ROUTING.md) 记录 relocation/compatibility。若读成本/正确性回归，或无法 single-source 而保持 current consumers，停止在 Review 边界并报告冲突；不得扩大 scope。回滚使用后续 revert/supersede，保留旧路径与历史 provenance；不重写旧 ADR。
