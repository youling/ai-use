# GitHub Capability Lab

**Contract version: 1.0.0** · **LAB_ESTABLISHED = PENDING**

这是公开、安全、可复用的 GitHub 能力证据入口。建立范围来自 [R4 Work #82](https://github.com/youling/ai-use/issues/82)、[架构冻结](https://github.com/youling/ai-use/issues/73#issuecomment-5750977205) 与 [owner 裁决](https://github.com/youling/ai-use/issues/68#issuecomment-5750977380)。只有 Global Architect 的 exact-head Review 才能接受 establishment；机械 PASS、claim promotion 或本目录存在均不能代替验收。

`EXPERIMENT != NORMATIVE_AUTHORITY`。Lab 不拥有项目事实、生产验收、治理规则、权限或平台配置，也没有数据库、服务、定时刷新器或 control plane。`R5 = HOLD`，downstream adoption 留给各 owner。

## 从最小证据开始

Architect / Research 需要可复用 GitHub 能力证据或计划当前 canary 时，先读 [派生索引](index.json)，再按 `claim_path` 读具体 claim、fixture 与 receipt。普通项目执行不默认读取 Lab。

| 路径 | 所有权 / 用途 |
| --- | --- |
| `claims/<capability_id>.json` | canonical Lab evidence：问题、观察、环境、边界、当前适用性与采用缺口 |
| `fixtures/<capability_id>/` | 可复现实验定义，包含执行前的资源与恢复计划 |
| `receipts/<capability_id>/` | 紧凑收据、精确来源、摘要与持久证据；不是第二 claim owner |
| [index.json](index.json) | 仅从 claims 生成的 discoverability projection；可完全重建 |
| [schema/claim.schema.json](schema/claim.schema.json) | versioned claim 与 compact receipt 结构 |
| [schema/fixture-policy.md](schema/fixture-policy.md) | public-safe allowlist、清理、UNKNOWN/replay 合约 |

治理采用必须另外走 owner Issue / [ADR-0006](../../../90_HISTORY/ADR-0006_GITHUB_CAPABILITY_LAB.md) / protocol / PR lifecycle；index 不产生规则。

## 三个相互独立的维度

`evidence_classes` 是可组合的描述：`DOCUMENTED_CAPABILITY`、`OBSERVED_AVAILABLE`、`OBSERVED_BLOCKED`、`SYNTHETIC_CANARY`、`MEASURED`、`REAL_REPO_CANARY`、`OWNER_LOCAL_PRODUCTION_EVIDENCE`、`UNKNOWN`。它们不是成熟度阶梯。有限正面观察可以与未解决维度的 `UNKNOWN` 共存；owner-local production 只能引用经过脱敏的 owner 提供证据，不能由 Lab 制造。

`promotion_status` 只取 `UNREVIEWED`、`REVIEWED_EVIDENCE`、`REUSABLE_DONOR`、`SUPERSEDED`、`INVALIDATED`。前两次提升需要针对具体 claim 范围的语义 Review；不存在 NORMATIVE / PRODUCTION promotion。`--write` 只生成 index，绝不修改 claim 或提升状态。Review 引用必须绑定 `semantic_digest`（UTF-8、排序 JSON、排除 `promotion_status` 和 `review` 字段）；内容、receipt 摘要或 fixture 摘要变化都会使绑定失效。schema 的 `review_receipt` 要求 `SEMANTIC_EVIDENCE_REVIEW` / `ACCEPT`、reviewed_by、review_scope、reviewed_head、content_sha256 与 limits；工具还从该 head 读取 claim 核对相同内容。这个机械绑定防止误用旧 Review，不能验证 reviewer 独立性或接受权限，后者留给 exact-head review。

`status` 描述已有证据的适用性，不回答功能是否存在：

| status | 含义 |
| --- | --- |
| `CURRENT` | 最近明确核对的环境与问题范围仍适用；采用前仍核对触发条件 |
| `HISTORICAL` | 冻结的旧观察，未重新主张当前环境 |
| `STALE` | 已知相关环境 / fixture / source 发生变化，需要重验 |
| `INVALID` | 已观察到失效条件，promotion 同时为 `INVALIDATED` |
| `UNKNOWN` | 当前适用性不能确定；不是不存在或不可用 |

index 保留全部这些记录。除 `CURRENT` + reviewed promotion + 无 `UNKNOWN` evidence 外，`use` 都是 `NOT_CURRENT_EVIDENCE`；满足条件也只显示 `REQUIRES_CLAIM_AND_TARGET_REVALIDATION`，不显示通用 available / absent / production-ready。消费者不能用过滤后的空集推断能力不存在。

## Revision、时间与证据保管

没有固定 TTL。`verified_at` 是该记录所依据的观测时刻，迁移、文件编辑、离线测试或 URL readback 不自动刷新它。`source_revision.kind=GIT` 时 commit 与 meaning 指定被观察的 source snapshot，不能机械填当前 HEAD；`LIVE_API` 时 commit 必须为空，由 `receipt_path` 指向 exact IDs、摘要与时间窗口，施工用 main 不能充当非 Git 元数据 revision。`fixture_revision` 用路径与 SHA-256 绑定定义字节；`execution` 明确 `EXECUTED` 或 `RECIPE_ONLY`，新 recipe 不冒充已经执行，EXECUTED 必须匹配 observation 中的 fixture_sha256。执行旧版本时，receipt 保留精确旧 fixture/source revision。

Lab 文本通过 scoped `.gitattributes` 保持 UTF-8/LF；SHA-256 对其实际字节计算。历史 donor artifact 的 `git_revision` 非空时，SHA-256 对该 commit 的 Git blob bytes 计算，避免 Windows checkout 换行转换造成伪差异；为空时对 local artifact bytes 计算。Git commit 负责 custody/provenance，不是生产当前性。旧 [#69/#70 donor](../astra-audit-69/README.md) 保持原样；只选三个代表维度，不全量复制八项原型结论。

每条记录列出 `invalidated_by`、事件/条件式 `revalidate_before` 与 `adoption_delta`。行为或权限、plan、visibility、API、runner、配置、fixture/source 改变，或采用依赖未覆盖维度时，先重验相关缺口。冻结的历史观察仍可解释当时结果，却不能证明变化后的环境。

外部 URL 不由离线工具联网检查；发布前由 executor/Reviewer 针对 exact receipt 完成 readback，并报告失败/未知。短期 Actions artifact/cache 不能作为唯一长期 custody，保留 compact receipt 与必要小型 payload/digest。cleanup failure 与 UNKNOWN 结果同样保留。

## 验证与维护

前提：Git、Python 3.10+；无第三方 Python 包、网络或凭据。

```sh
python tools/capability_lab.py --write --base-ref <exact-base-commit>
python tools/capability_lab.py --check --base-ref <exact-base-commit> --r4-acceptance
python tools/test_capability_lab.py
python tools/routing.py --check
```

`--base-ref` 在发布/CI 中必须传入当前 PR/event base；本地默认 `HEAD` 只比较未提交状态，不是整个 PR 的证明。`--r4-acceptance` 额外证明本次 R4 未改 AGENTS 与历史 donor；普通 `--check` 不永久禁止未来获授权的 L0/历史修正。CI 在 Ubuntu/Windows checkout exact PR head，校验预期 SHA，比较 event base，R82 分支额外启用 R4 proof，执行纯离线检查，不运行 live canary。

验证器实现 schema 中实际使用的标准 JSON Schema 子集：`$ref/$defs`、object/array/string/boolean/null、required、additionalProperties、items/minItems/uniqueItems、minLength/pattern、enum/const、anyOf、HTTPS uri 与含时区 date-time。它不是通用 JSON Schema engine，新增关键词需同步实现与负例，未知关键词 fail closed。

检查覆盖稳定唯一 ID（保留已存在记录，退役用 supersede）、schema、receipt/fixture 本地指针与摘要、index 精确重建、必要限制/采用/清理字段、AGENTS 与旧 donor 未改，以及 obvious public/private/secret tripwire。当前 coordinate allowlist 仅含公开的 `youling/ai-use`；扩大需要显式公开来源核对与 Review。模式检查不能证明无秘密、真实性、完备性、权限或语义正确。

证据更新在 claim owner 中进行，追加/保留失败 provenance，重建 index，再做 exact-content semantic Review 与 exact-head PR Review。回滚用后续 PR revert/supersede，不重写历史，不删除解释失败所必需的证据。
