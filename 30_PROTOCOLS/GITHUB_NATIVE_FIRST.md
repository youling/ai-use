# GitHub Native First

**Classification: L2 Targeted Reference.**

**Protocol Version: 1.1.0**

语义 owner：[工作项 #67](https://github.com/youling/ai-use/issues/67)；长期裁决：[ADR-0005](../90_HISTORY/ADR-0005_OWNER_NATIVE_DERIVATION.md)。本协议是 architecture decision method，不是平台配置指令或 Capability Lab schema。

## 1. 触发范围

当 Architect 为 GitHub-hosted 项目提出自建 collaboration/control/work dashboard、release service、event plane、read/query/index、navigator 或 metadata subsystem，或 material architecture 明确依赖 GitHub platform behavior 时，MUST 做 targeted native-first 判断。

普通 bugfix、Hot Resume、确定性维护和已冻结方案下的窄实现不因项目托管在 GitHub 而触发 mandatory platform scan。已有同 scope、current 且适用的判断可按 [Architect Reconnaissance](../docs/ARCHITECT_RECONNAISSANCE.md) 复用；只复核受变化影响的 capability。

核心问题是：GitHub 已解决哪部分通用问题，项目还剩什么真正需要自建？native feature availability 不产生 authority；native convenience 不改变 semantic ownership。owner/storage/private boundary 由 [Owner / Instance Boundary](OWNER_INSTANCE_BOUNDARY.md) 定义。

## 2. 按语义选 surface

以下是候选映射，不要求每个 repo 部署全部层，也不承诺目标 account/plan 拥有每项能力。

| 语义层 | 可评估的 native / derived surface | 必须保留的边界 |
| --- | --- | --- |
| Canonical domain truth | owner-repo artifacts / exact Git revision；owner 明确指定的 native object/field | owner contract 定义真值；GitHub 托管不把业务事实强行迁入工程系统。 |
| Local intake / work | Issues、Forms、native relationships | 收集请求与本地 Work；关系含义以 current owner contract 为准。 |
| Transaction / acceptance | PR、reviews、checks、rulesets/protection | change、review、机械证据与 enforcement 分开；绿灯不自动等于治理验收。 |
| Operational projection | Projects、labels、milestones、saved views | 通常展示 active work；不得默认永久镜像每条 domain record 或另造 lifecycle。 |
| Validation / materialization | Actions、checks、deterministic generators | 产生验证结果和 derived artifact，不因执行成功取得语义 authority。 |
| Distribution / checkpoint | tags、Releases、Packages | 分发 envelope，可携带版本/source/provenance；不是写入真值本身。 |
| Event / integration | GitHub App、webhooks、REST/GraphQL | 事件提示与授权后的 reconciliation；不以 payload 代替 current source。 |
| Derived read / query | bounded index、snapshot、可选 DB、graph、navigator | 查询成本优化；保持 rebuildability、freshness 与 canonical pointer。 |
| DR / recovery | Git mirror/refs、desired config、native metadata export、external payload backup | 分层恢复；clone 不能证明整个 operational plane 可恢复。 |

Projects、labels、milestones、Discussions、Actions、Releases、App state 都**不是自动的 domain truth**。只有 explicit owner contract 指定某个 field/object 的 authority、合法 writer、mutation/lifecycle 与 reconciliation 规则时，该部分才可作为 canonical；不能把一个字段的授权扩成整个平台的 ownership。

## 3. Native-first 决策

Architect 对实际相关的 candidate 做最小比较，记录 current official capability evidence、目标环境可用性、semantic fit、剩余缺口与运维/恢复成本：

- Issues/Forms 能否表达 intake，native relationships 能否表达所需 dependency？
- Projects 能否承担 Human operational view，且保留现有 owner/lifecycle？
- Actions/Checks 能否承担 validation/materialization；rulesets/protection 是否能落实所需约束？
- Releases/Packages 能否承担所需版本分发/checkpoint，而不接管写 authority？
- GitHub App/webhooks 能否减少 polling；REST/GraphQL 能否提供所需 read/write seam？
- bounded derived index/snapshot 能否避免 full-repo ingestion；现有 Diagram/Navigator 能否提供 source drill-down？
- 哪部分仍是 project-specific，且 native adaptation 的总复杂度高于自建？

按能力或 seam 记录以下结论，不用一个全局标签掩盖不同缺口：

| Decision | 含义 |
| --- | --- |
| `REUSE_NATIVE` | current native primitive 已满足语义与必要约束，直接在授权范围使用。 |
| `ADAPT_NATIVE` | native 解决通用部分；用 bounded adapter/automation 接既有 contract，不创建平行语义轨道。 |
| `DERIVED_PROJECTION` | 需要新的 read/navigation/presentation 面；从 canonical source 生成并保留 currentness 与回源路径。 |
| `CUSTOM_REQUIRED` | 证据表明存在 native 无法满足的实质缺口；说明缺口、scope、owner seam 与 validation/recovery 成本后才进入自建。 |
| `DEFER` | 必要 evidence、能力、授权或优先级尚不足；记录 exact gap 与重开条件。 |
| `REJECT` | 方案违反 owner/authority/security 边界、形成第二 SSOT，或收益不足；记录理由。 |

native-first 不等于所有 native surface 必选，也不等于禁止 custom code。报告可以引用已有 ARCH-0 output 或 owner decision，不另造中央 registry。保存简洁决定、blocker、checkpoint 与 evidence pointers，不保存 chain-of-thought。

### 3.1 GitHub Actions resource-budget gate

选择 GitHub Actions 前，MUST 先判断：

```text
repository_visibility = PUBLIC | PRIVATE | INTERNAL | UNKNOWN
runner_class = STANDARD_GITHUB_HOSTED | LARGER_GITHUB_HOSTED | SELF_HOSTED | UNKNOWN
budget_state = AVAILABLE | CONSTRAINED | EXHAUSTED_OR_BLOCKED | UNKNOWN
platform_semantics_required = YES | NO
```

这些是执行环境/计费 current evidence，不产生 authority。deployment 的实际额度、账单、预算属于 owner-local private state，不进入 public ai-use。

**PRIVATE / INTERNAL 默认节制 GitHub-hosted Actions。** 若本地 deterministic validation 能证明同一性质，优先本地执行；generic GitHub 行为已有 current Capability Lab evidence 时优先复用；确实需要 GitHub event/runner/platform semantics 时，优先使用现有、已授权且适用的 self-hosted runner，最后才使用最小充分的 GitHub-hosted run。不得为了方便重复消耗 hosted-runner 额度去跑本地已等价覆盖的 unit test、format/lint、generator、schema/link check，或没有真实跨平台风险的宽 matrix。

若 `budget_state = EXHAUSTED_OR_BLOCKED`，GitHub-hosted Actions **不是默认 required verification path**。其它 evidence 能证明同一 claim 时使用其它 evidence；不能证明时保留该 property 为 `UNKNOWN / BLOCKED`，不得把“省额度”写成“CI PASS”。

**PUBLIC + standard GitHub-hosted runner** 可继续作为优先 native validation/canary surface，但免费不等于无节制：禁止重复 workflow、heartbeat CI、无必要矩阵、未变化 canary 的机械重跑和无必要的大 artifact/cache。larger runner 仍按其 current billing/plan 条件单独判断。

证据强度保持：

```text
CI unavailable due budget != CI passed
local PASS != GitHub platform/event semantics proved
public synthetic canary != private owner production proof
```

Generic GitHub uncertainty 应尽量“公共 Lab 测一次，下游私仓只测 unresolved local delta”。

官方 current billing/runner 条件入口：
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)

## 4. Projection、event 与 currentness

字段至少区分：

| 类别 | Writer / 消费方式 |
| --- | --- |
| `DERIVED` | 按 owner source 确定性生成；刷新不能覆盖 Human-owned 内容。 |
| `HUMAN_OWNED` | 由 Human 按 owner contract 管理；只有 contract 显式授权时才由 automation 修改。 |
| `SUGGESTED` | Agent/scheduler 建议，保持建议身份；未经 owner 指定的接纳步骤不能伪装为事实或指令。 |

UI drag/drop 或自动字段变化 MUST 映射到已有 owner transition/合法 mutation，或仅影响 presentation；不能默默引入第二套状态机。字段不明时先 reconcile。

```text
event / webhook = hint
 -> live-read current owner source
 -> reconcile observed state / desired effect
 -> authorized, currentness-guarded, idempotent mutation
```

重复、延迟、乱序或重放事件不得盲目重施 effect；owner-local adapter 明确去重、currentness guard 与失败后核对规则。必要权限不足、source 不可读或此前 effect 不明时停在 exact gap，不能用旧 payload 补作 current evidence。

事件接入不能假定无遗漏。若正确性依赖完整状态，owner-local contract 应提供按需或定期 reconciliation 作为补漏路径，并验证其覆盖范围；本协议不设统一 polling cadence 或强制 scheduler。

search/API 结果必须核对 pagination、可见范围、权限与截断。incomplete/truncated enumeration 不能证明全集或空集；forbidden/unknown 不能包装成“没有记录”。derived result 的 freshness 与 source drill-down 按 [Durable Data Doctrine](../docs/DURABLE_DATA_DOCTRINE.md)；多个派生面的含义一致性按 [Diagram-as-Code](DIAGRAM_AS_CODE.md#41-共享派生解释边界)。

Release/Package 是 distribution/checkpoint envelope：版本化甚至 immutable 的包装也不证明其中内容 current、canonical 或已获 production acceptance。分发 cadence 可独立于每次 commit，但消费者必须知道对应 source revision 和使用边界。private/source handling constraints 同样适用于 Projects、Releases、Pages、导出与 cache。

## 5. Capability evidence 与 admin / Human gates

平台判断使用 [ARCH-0 targeted platform pass](../docs/ARCHITECT_RECONNAISSANCE.md#31-targeted-github-platform-pass) 的 evidence classes，显式记录相关 plan、account/repo 类型、auth scopes、admin 能力、target/ref、配置与 evidence window。官方文档存在、一次 API 成功、别处 canary 或模型记忆，都不能证明当前目标已启用或有权变更。

`PROCESS_GUARDED != PLATFORM_ENFORCED`：review 约定、Agent 自律或脚本预检只能声明 process guard。只有 current target 上的实际 platform configuration、适用对象/refs、bypass 范围与相应验证 evidence 才支持限定范围内的 platform-enforced claim。无法读取设置时记 UNKNOWN；不得因已有 CI 绿灯声称分支已受平台强制保护。

只有方案确实依赖时才检查对应 gate；不存在能力或权限不授权自动升级 plan、迁移 Organization、创建 Projects、安装 App、扩 OAuth/PAT scopes、修改 rulesets/protection/bypass 或 merge settings。需要此类变更时，先确认 current explicit authority；缺失时以具体操作、目标、影响和 evidence 缺口停在 Human/admin gate。已授权的 ordinary repo action 不另加仪式性审批。

官方 lookup anchors（仅按命中 capability 读取，执行时重新确认适用条件）：

- [Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)：views/fields/automation 的 candidate。
- [Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)：rule、plan、管理权限及 bypass 边界。
- [Merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)：拟采用时检查 repo/plan/admin 与 `merge_group` CI 适配。
- [Repository webhooks](https://docs.github.com/en/rest/repos/webhooks)：delivery/read/redelivery 所需 API 与 permissions。
- [Immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)：拟采用时确认不可变边界，不从 immutable 推导 canonical authority。

Capability/audit/canary evidence 仅在 current、同 capability class 且环境适用时复用；synthetic benchmark 不作 production proof。Lab maturity、schema/index/promotion 属于其独立 owner decision，本协议不建立它们；现有 donor evidence 不构成自动 promotion。

## 6. Repo-class adaptation matrix

下表是 applicability/recommendation，不是 adoption 清单。每类都从 §2 的候选层选最小集合；Rulesets/protection 只在所需 transaction gate 且能力/授权满足时采用，App/webhooks 只在真实 integration 需求时采用，native metadata backup 只覆盖 owner 声明需恢复的对象。

| Repo class | Intake / operational view | Validation / distribution / integration | Derived read / navigation / recovery；避免 |
| --- | --- | --- | --- |
| Fact / archive | Issues/Forms 接入纠错与采集 Work；Projects 展示 active work。 | Actions/Checks 校验 provenance/schema；Releases/Packages 可分发有 revision 的 snapshot；事件触发 reconcile。 | bounded catalog/query → source；保留 lineage 与 payload recovery。避免把每条 fact 永久搬进 Projects。 |
| Infrastructure / platform | Issues/relationships 表达变更、依赖与 gate；Projects 展示 rollout。 | Checks 验证 config/adapter；保护规则按目标验证；版本分发可用 Release/Package，App 可接变更信号。 | topology/desired-state drill-down；分别恢复 Git/config/metadata。避免把连通、CI 或 webhook 当实际部署成功。 |
| Decision / runtime | Issues 记录机制/contract 工作；Projects 展示工程进展。 | Checks 验证决策/状态边界；Package/Release 分发版本；integration 适配现有 runtime seam。 | graph/query 回到 evidence 与 owner；runtime payload 单独恢复。避免拿 Issue/Project 状态替换 runtime domain state。 |
| Product | Forms/Issues 接入反馈、bug、feature；Projects/milestones 展示交付。 | Checks/review 支撑 acceptance；Release/Package 分发；App 仅接所需事件，deploy gate 独立。 | 按版本/交付导航，保留需恢复的反馈 metadata。避免把发版或板卡移动当 production acceptance。 |
| Horizontal library / design system | Issues 接 API/兼容性请求；Projects 按需要组织版本工作。 | Checks 校验 contract/兼容性；Package/Release 分发 reviewed artifact；integration 可通知消费者。 | API/依赖/示例索引回到 exact version；保留 release metadata。避免分发平台接管 consumer domain truth。 |
| Research / evidence | Issues 定义问题/实验；Projects 仅跟踪当前研究。 | Actions/Checks 支撑复现与机械验证；Release 可封装 evidence；App 按需接入采集事件。 | provenance/query/diagram 指回方法与原始 evidence，区分 metadata/payload recovery。避免把 synthetic PASS 或 Lab canary 变成 production/normative claim。 |

## 7. Recovery 与停止边界

采用 surface 前明确丢失后需恢复什么。按 [Durable Data recovery split](../docs/DURABLE_DATA_DOCTRINE.md#9-recovery-分层) 区分 Git truth/refs、desired platform configuration、non-Git metadata、external payload。metadata export 不等于原 GitHub IDs/authors/timestamps 和平台行为可原样恢复；owner 必须声明 reconstruction/mapping 的保真范围与验证证据。

遇到 authority/owner 冲突、必需平台能力 UNKNOWN/BLOCKED、枚举不完整却需全集判断、不可证明 query freshness、或无授权 admin/security 操作时，停止对应 dependent action 并报告 exact gate。不能通过自建 mirror、扩大 token 权限、相信旧 event 或把候选 surface 改称 canonical 来绕过。

本协议不要求 Projects/Releases/Apps 全量铺开，不建立新 control plane/runtime/DB，不复制私有 topology、schema 或 provider facts；落地只在项目自己的 authorized Work 中进行。
