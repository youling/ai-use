# ASTRA_AI_USE_R1_R2_BUILD_REPORT

Artifact Version: 1.0.0
Work: [#74](https://github.com/youling/ai-use/issues/74)
Decision: [#73 freeze](https://github.com/youling/ai-use/issues/73#issuecomment-5749622582)

本文件记录 R1/R2 实现和证据。最终交付状态、exact final head、最后一次 Actions 收据由 #74 的同名报告评论绑定；文件本身不自证 Global acceptance。Global Architect 的 exact-head semantic Review 仍是后续边界。

## 1. Base

`e6de9acdafbc3b9d12802ecf8de25f444074553b`。施工前 native current L0/Work/ruling 读取、live-fetch、隔离 clone 和迁移计划已记入[修改前 checkpoint](https://github.com/youling/ai-use/issues/74#issuecomment-5749653022)。最终报告前再核对 main 与 ruling，未发生源语义漂移。

## 2. Exact-head binding

核心候选 commit：`d38cb8aa6c74cc6a5b5f4a49ea39c3f51cf9674d`，tree：`5d811690041acf9c5d2aa652ddcce1cccfad174b`。

五类 candidate readers 使用该冻结源码。最后的 evidence commit 只增加本实验目录和读取器；[source manifest](candidate-source-manifest.json) 列出候选全部 73 个文件的 SHA-256。最终验证逐文件确认这些 Git blobs 与交付 head 相同。readers 没有重读后来加入的报告，不把这些新增文件伪称 reader-tested governance。最终完整 SHA 及 CI 绑定在 #74 评论，避免 Git 文件自引用 commit hash。

## 3. Branch / PR / execution lineage

Published branch：`codex/r74-recovery-routing`；唯一交付 PR：[#75](https://github.com/youling/ai-use/pull/75)。

Fresh Builder 使用无父对话继承的独立上下文，源文件在 task-private clone 中批量实现。协调上下文保留 #69 历史，负责实验、对账和发布，不伪称 Fresh Builder 或 Global Reviewer。Builder 的本地核心 tree 与 native GitHub 发布的核心 tree 一致；没有强推或重写历史。已有 native GitHub 能力完成含 workflow 的提交，无 credential scope、App、组织或平台设置扩张。

## 4. ADR

[ADR-0004](../../../90_HISTORY/ADR-0004_RECOVERY_ROUTING_SINGLE_SOURCE.md) 在编号复核后文件化 #73 的长期语义、取舍、阶段与回滚边界。状态明确为 frozen decision materialized / exact-head semantic Review pending。

## 5. Changed-file map

核心改动共 31 个文件，逐文件列表在 [changed-files.json](changed-files.json)；最后只追加实验观察、计量、报告和标准库读取器。

| 分组 | 改动 |
| --- | --- |
| R1 语义 | 新 Recovery protocol；Bootstrap、Agent Interface、Durable Trace 的必要 relocation / current-state fallback |
| R1 形态与兼容 | Context Mode Seed、Dispatch Pair、handoff check/transaction、capability self check；Session、旧 provider guide 和旧 Human 入口 forward |
| R2 单源 | Routing Catalog；完整生成的 START_HERE、READING_MAP、NAMESPACE、ROUTING_INDEX |
| 消费者入口 | README、00/10/40/50/90 indices、Progressive Context、public cold-start checklist、human README |
| 迁移与验证 | ADR、migration map、routing generator/validator、15 项结构测试、只读 Linux / Windows CI |
| 实验证据 | 本目录、10 份原始 reader 结果及对应 read logs、source manifest、计量/人工评分；[读取器](../../../tools/fresh_reader_io.py) |

## 6. Recovery semantic migration

完整表见 [migration map](../../migrations/R74_RECOVERY_ROUTING.md#semantic-relocation-map)。

- Recovery §1–3 是唯一 current recovery/handoff 语义 owner，恰分 planned transfer、crash/old-context-unavailable、hot/warm resume。当前 durable authority/state 足够时，旧方产物或新 Human prompt 不作为 crash 的额外门；真实 authority/access/currentness/primary/independence/writeback gate 保留。
- Session / Context Mode Seed 的 Work Context、六个正交维度全部既有枚举、fresh independence、delegation 和 durable-before-fragile 迁入 Recovery §4–5。Session §11 的项目可复现要求迁入 §7；无新增 storage doctrine。
- continuation、ordinary repair、PREMATURE_YIELD 和 acceptance-derived completion 留在 Agent Interface；Dispatch 的最小 seed / fallback 语义归其 §3。
- capability preflight 语义归 Bootstrap §4，模板只给形态；没有建立 Capability Lab。Durable Trace 仍拥有 checkpoint mechanics，缺旧 checkpoint 时显式使用 current-state reconstruction。

## 7. Routing catalog / projections

[ROUTING_CATALOG.yaml](../../../ROUTING_CATALOG.yaml) 采用 JSON-compatible YAML 1.2，18 个初始稳定 ID；只拥有 scene、reading/role、home、compatibility / projection metadata。四份完整生成投影是 [START_HERE](../../../START_HERE.md)、[READING_MAP](../../../READING_MAP.md)、[NAMESPACE](../../../NAMESPACE.md)、[ROUTING_INDEX](../../ROUTING_INDEX.md)。投影导航足够时无需再通读 catalog；协议 mechanics 不进入路由源。

标准库工具检查 schema/唯一与稳定 IDs、home 路径、L0 边界、四份投影逐字一致、相关 links/anchors 和有限公开形态。生成命令 `python tools/routing.py --write`，验证命令 `python tools/routing.py --check`。

## 8. Compatibility / forward pointers

旧路径没有删除：Session 原章节 anchors 转 Recovery；Context Mode Seed / handoff / capability 等模板保留原 anchors 并指向 canonical semantics。DeepSeek provider guide 标为 retired-forward，导向 Bootstrap / Interface / Change Lifecycle。human README 改为当前入口；旧 Depositor v0.1 加 historical/current forward，current Depositor 0.1.3 原样保留。

完整[兼容说明](../../migrations/R74_RECOVERY_ROUTING.md#compatibility-and-provenance)及 catalog compatibility records 可对账。旧 Session/provider/template 正文仍能由 frozen base Git blob 追溯；没有改写旧 Git/ADR，也没有把 #26 / #69 历史 evidence 提升为 authority。

## 9. Local checks and Actions

- `python tools/routing.py --check`：18 routes、4 deterministic projections、changed Markdown links/pointers、18 copyable surfaces、旧入口 anchors 与 L0 equality 通过。
- `python tools/test_routing.py`：15 项结构测试通过，含正向与负向 fixtures；不是 15 项全部为负向测试。
- `git diff --check` 对完整基线 diff 通过；Python AST、改动 JSON/JSONL、catalog JSON/YAML 等价、workflow YAML 及只读 permissions 可解析并核对。
- 每份 read log 的 source hash、文件长度、源行范围、计量总数对 frozen Git blobs 复核；logs 与七份 result 逐字保存，两份 result 仅 CRLF 转 LF。decision candidate 的 source_snapshot 本地 transport path 替换为 inert placeholder，其余观察不改；measurements 记录变换和原始/发布摘要。执行读取器与发布读取器逐字一致。
- 核心 exact-head Actions 已通过：[push](https://github.com/youling/ai-use/actions/runs/35510209226)、[pull_request](https://github.com/youling/ai-use/actions/runs/35510210499)，每次均为 Linux / Windows 两个 job。最终 evidence commit 的 exact-head Actions 收据另在 #74 报告绑定，不能用核心 head 的绿灯代替。

## 10. Five fresh-reader results

[RESULTS](RESULTS.md) 给出五组前后对照、每类 files/bytes/hops/blockers/current-home accuracy/crash outcome、source ambiguities 和评分理由。[measurements.json](measurements.json) 是从源行与日志复算的计量；[scoring.json](scoring.json) 是协调者按预定规则做的人工判读，两者不混为模型自证。

基线五类都能恢复，不能声称本轮把 recovery 从失败改成成功。实验判断是否更直接找到 current owner 并保留真实 gates。每格一个独立模型观察、synthetic verified 项目输入、部分工具截断/补读，均不是生产验收、tokens、延迟或一般成功率。旧 #69 whole-file 路径数值不是等价基线。

## 11. L0 semantic diff

`AGENTS.md` 的基线与最终 Git blob 完全相同，源文件 SHA-256 为 `5e1a4885d56fe20ee233ac7a461138054afe8c8f1281b0c9c04fde2170de72e0`。L0 不新增任何路由、recovery、GitHub native、Lab、Current Read 或 Diagram mechanics。CONSTITUTION、Change Lifecycle、Reconnaissance、Durable Data、Diagram、current Depositor 与 #69 审计历史也未改动。

## 12. Remaining risks / debt

- 合成读者单样本对比只提供方向性观察；不能证明所有后续项目的阅读成本下降。Infrastructure 的含重读字节有小幅回归，详见 RESULTS，按 freeze 将该冲突留给 Review，不扩大 scope 或选择性删除样本。
- L0 的 NAMESPACE + READING_MAP 指针与 Bootstrap 的 scene-based NAMESPACE 表述仍有轻微阅读顺序张力；本次读者没有因此阻塞。保留 L0，不能借迁移改其语义。
- ARCH-0 / L1–L2 仍须由实际 material decision 和 owner-local contract 判断；本实验没有提供真实项目设计或 production acceptance。独立 Global semantic Review 尚未完成。
- 公开示例 guard 是有限 surface / triple-backtick fixture 和明显 credential shape 检查，不是全仓 secret scanner。人工复核改动的 current shapes；历史 Git、旧 Issue/PR 文本仍保留 provenance，并未作历史清除承诺。
- 初始稳定 IDs、兼容 anchors、L0 equality 使用本次 migration baseline；未来经授权的 schema/L0/compatibility migration 应明确更新这些校验，不能静默删 ID 或改变源语义。
- 更完整 ownership/storage doctrine、GitHub capability adoption/promotion、Lab、平台执行 canary 与旧历史文本治理仍归原工单，不在本次报告中推定完成。

## 13. Explicit scope / stop confirmation

R1/R2 only。R3/R4/R5、#66/#67/#68 substantive work、App/PAT/OAuth/Organization、main protection/rulesets/admin settings 未修改；没有 merge，没有 history rewrite，没有向公共仓导入真实私有实例或 deployment topology。

最终 pushed head 的机械检查与回执完成后，#74 声明 `READY_FOR_GLOBAL_REVIEW`。后续动作是 Global Architect 对精确 head 进行语义 Review；本 executor 不自批、不合并、不关闭 #73/#74，也不进入后续 tranche。
