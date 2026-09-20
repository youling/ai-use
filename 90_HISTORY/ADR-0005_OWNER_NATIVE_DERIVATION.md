# ADR-0005：Owner / Native Capability / Derived Interpretation

**Artifact Version: 1.0.0**
状态：Accepted / exact-head reviewed
裁决：[Global Architect R3 freeze](https://github.com/youling/ai-use/issues/73#issuecomment-5750762655)
语义 owner：[#66](https://github.com/youling/ai-use/issues/66) / [#67](https://github.com/youling/ai-use/issues/67)
实施：[R3 Work Order #80](https://github.com/youling/ai-use/issues/80)
验收：[PR #81 Global Architect review 5261019854](https://github.com/youling/ai-use/pull/81#pullrequestreview-5261019854)

## Context

存储位置、native UI 与查询便利容易被误当 semantic ownership；派生 index/snapshot/diagram 若分别解释同一 domain，会产生多份互相冲突的“当前事实”。已有 L0、stage-aware reuse、七项 durable-data 问题与 Diagram doctrine 已提供基础，R3 只补足这些 seam；#73 负责实施协调，不吸收 #66/#67 的语义 ownership。

## Decision

1. [Owner / Instance Boundary](../30_PROTOCOLS/OWNER_INSTANCE_BOUNDARY.md) 区分 semantic owner、storage、pointer、derived projection、private instance 与 secret reference/value。允许有明确 owner/currentness/purpose 且不藏唯一外域事实的 private overlay；拆分依据真实 lifecycle/access/retention 证据。复制与移动不自动转移 ownership。
2. [GitHub Native First](../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md) 是 targeted architecture method：提出 custom GitHub-hosted subsystem 或依赖 material platform behavior 时，先判断 native fit 与剩余缺口。native capability 和便利性都不授予 authority；ordinary task 不增加全平台扫描。
3. [Durable Data Doctrine](../docs/DURABLE_DATA_DOCTRINE.md) 保留七项基础问题，兼容增加 optional Current Read Plane。canonical/history cost 与 current-read cost 分开；旧 snapshot 回答新 target 必须有版本、完整 delta 与相关 query 正确性的 evidence。优化读取不创造第二 SSOT。
4. [Diagram-as-Code](../30_PROTOCOLS/DIAGRAM_AS_CODE.md) 扩展为同 domain 的 index/snapshot/graph/navigation/diagram SHOULD 共用 reviewed normalized interpretation boundary，或证明 semantic equivalence。renderer schema 不拥有 domain ontology；表面渲染成功不能裁决派生冲突。
5. [Routing Catalog](../ROUTING_CATALOG.yaml) 仅增加两个 targeted routes，继续生成现有四个 projections。协议拥有语义，routing 拥有 applicability；不添加第二导航源或 L0 mechanics。

## Alternatives and tradeoffs

把全部内容加到 L0 会扩大每次启动成本，也不通过 Kernel residency test；使用 targeted L2。把每种 repo 固定成同一 GitHub stack 虽易复制，却会掩盖 plan/admin 条件并引入第二状态机；采用分层 candidate 与 repo-class guidance，保留 owner-local 决策。

统一数据库或集中 query runtime 可减少实现差异，却不是治理所需的必要条件；不规定 SQLite/DB 或新中央 runtime。共享解释边界降低 drift，代价是维护 version/provenance；独立实现仍可存在，但需要其声明 query/domain 范围的 equivalence evidence。incremental current-read 可能节约读取，也增加 delta completeness 与 full-rebuild 对照的举证成本。

## Compatibility and scope

不替换七项 data 问题、不改 Diagram renderer/readability/scale doctrine、不移除旧路径、不修改 `AGENTS.md`。公共规范不承载私有部署/项目事实，不实施 downstream adoption、平台 admin 或项目 migration。

audit/canary 只是可复用 evidence。历史 [#67 maturity statement](https://github.com/youling/ai-use/issues/67#issuecomment-5749193138) 已由 [#68 ruling](https://github.com/youling/ai-use/issues/68#issuecomment-5749572259) 与 R3 freeze 的 R4 HOLD supersede；本 ADR 不建立 Capability Lab schema/index/promotion。R5 platform enforcement 也不在本次范围。

## Validation and rollback

结构 checks 验证 routing/schema、generated projections、links 和 L0 未改；bounded semantic scenarios 检查 custom control、private overlay、旧 snapshot/new target 与 derived-surface drift。机械或 synthetic reader evidence 不替代 exact-head Global Architect Review，也不是 production proof。

回滚使用后续 PR revert/supersede，保留 Git provenance；本次无运行态迁移。若实现与 frozen decision 冲突，停在 Review 边界回报 owner，不在实现中重设计。
