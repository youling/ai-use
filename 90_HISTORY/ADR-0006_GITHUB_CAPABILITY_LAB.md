# ADR-0006：GitHub Capability Lab

**Artifact Version: 1.0.0**
状态：Accepted / exact-head reviewed
裁决：[Global Architect R4 freeze](https://github.com/youling/ai-use/issues/73#issuecomment-5750977205)
语义 owner：[#68](https://github.com/youling/ai-use/issues/68#issuecomment-5750977380)
实施：[R4 Work #82](https://github.com/youling/ai-use/issues/82)
验收：[PR #86 Global Architect review 5261164668](https://github.com/youling/ai-use/pull/86#pullrequestreview-5261164668)

## Context

#69/#70 审计原型包含有用 GitHub canary，但旧 evidence index 缺少统一 claim/currentness/cleanup/adoption contract。一次 API/Actions 成功容易被扩大成通用能力、规范规则或生产验收。R4 需要可审阅、可复用、保留限制的证据通道；历史 donor 本身不直接升级。

## Decision

1. [Lab](../docs/research/github-capability-lab/README.md) 只拥有公开安全的能力证据。`claims/*.json` 是 canonical evidence，`index.json` 只从 claims 生成；fixtures 拥有实验定义，receipts 保留精确来源与摘要。规范规则仍在 owner protocol/ADR/PR lifecycle 中。
2. versioned schema 区分可组合 evidence descriptors 与 Lab-local promotion：`UNREVIEWED → REVIEWED_EVIDENCE → REUSABLE_DONOR` 需要明确语义 Review，退役/失效分别为 `SUPERSEDED`/`INVALIDATED`。箭头是可选流程，不是能力阶梯；无 NORMATIVE/PRODUCTION 状态，无自动采用。
3. 每条记录保留 source snapshot、fixture digest、verified_at、environment、proves/does_not_prove、limits、invalidated_by 与 event/condition-based revalidate_before。没有统一 TTL；历史观测不自动变假，也不证明变化后的环境。index 不把 stale/invalid/unknown 解释成缺失或当前可用。
4. [fixture policy](../docs/research/github-capability-lab/schema/fixture-policy.md) 只允许已有权限中的 bounded public synthetic/reversible 资源。mutating fixture 在执行前记录创建资源、cleanup/replay、UNKNOWN live reconciliation 与 retry receipt。失败证据不清除，Git 历史不重写，短期 artifacts 不承担唯一 custody。
5. 下游采用先确认语义、target environment/permissions/currentness，再证明未覆盖 delta，由 owner 决策。public Lab 不承载 private topology 或 production acceptance，不自动扩权。
6. 最小 stdlib validator/generator 与 exact-head offline CI 负责结构和派生一致性；semantic evidence review 与 Global Architect establishment acceptance 分开。仅新增 Architect/Research targeted discovery route，普通执行不读取 Lab。

## Alternatives and tradeoffs

直接升级 audit 原型会继承未审阅成熟度与 cleanup/currentness 缺口；因此保留历史、只迁移 pagination、Actions least-permission/matrix artifact、reversible Issue relationship 三个代表维度。已有精确 donor 足够时复用，不为新 schema 无谓扩大远端 mutation。

完整 JSON Schema framework、数据库、服务或 runtime 会增加依赖与第二控制面；采用 Git JSON source、有限已声明 schema 子集和离线工具。代价是新增 schema keyword 需要实现与测试，公开可见性和语义真实性仍要人工/Agent review，不能由 regex 或 CI 保证。

## Validation, compatibility and rollback

负例覆盖非法枚举、自我规范/生产提升、缺必要字段、重复/删除稳定 ID、index stale/invalid/unknown、digest/pointer drift、明显秘密或 private coordinate。PR 检查 exact head、event base、index reproduction、routing、AGENTS unchanged 与历史 donor unchanged。claim Review 绑定 exact semantic digest；不能据此自行声明 establishment。

本次不修改 L0、不做 R5/admin/Projects/App/auth/plan/private-access/production/downstream 变更。失败用后续 PR revert/supersede；无运行态数据迁移或中央服务需要回滚，保留 old donor 与失败 provenance。
