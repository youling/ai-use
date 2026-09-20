# ASTRA_AI_USE_R1_R2_BUILD_REPORT

Artifact Version: 1.1.0
Work: [#74](https://github.com/youling/ai-use/issues/74)
Decision: [#73 freeze](https://github.com/youling/ai-use/issues/73#issuecomment-5749622582)
Repair: [Review 5260592093](https://github.com/youling/ai-use/pull/75#pullrequestreview-5260592093) / [dispatch](https://github.com/youling/ai-use/issues/74#issuecomment-5749879372)

本版本记录同 lineage 的两项 MAJOR repair 与必要上游对账，替代初次交付的 current-head 声明。[旧报告](https://github.com/youling/ai-use/blob/39ae29dd682978dacafe36cf8c0db34a89be0128/docs/research/r74-fresh-readers/BUILD_REPORT.md)及[初次回执](https://github.com/youling/ai-use/issues/74#issuecomment-5749847951)保留历史事实。新的 exact final head / CI 收据由 #74 同名报告评论绑定；Global acceptance 仍需新 head Review。

## 1. Bases and current authority

R74 原始 dispatch base：`e6de9acdafbc3b9d12802ecf8de25f444074553b`。已审查旧 head：`39ae29dd682978dacafe36cf8c0db34a89be0128`。本次 live main / 合入的上游：`3198450f97607c4317498a34bac79523b4e850e9`。

main 已通过 #77/#79 接受 #76 Local Engineering Gate，#73 要求消费该现有组件。修复前读取 current native L0/ruling 并核对 branch/head；[delta plan](https://github.com/youling/ai-use/issues/74#issuecomment-5750577175)记录 Gate 和 scope。Windows adapter 0.1.1 在 clean task-private clone 返回 READY_WITH_WARNINGS：必要能力通过，仅 pwsh/gh stable-version 更新提示；本 Work 无 RequireLatest、Codex/OpenCode CLI 或 device probe 要求。

## 2. Exact-head binding

新报告评论绑定实际 pushed head、两个父提交与 PR head。feature branch 合入 accepted upstream 保留 ancestry，不重写 published history，也不修改 main。机械检查针对新 tree / exact head。

原五类 reader 的 source commit 是 `d38cb8aa6c74cc6a5b5f4a49ea39c3f51cf9674d`，tree `5d811690041acf9c5d2aa652ddcce1cccfad174b`；[原 73 文件 manifest](candidate-source-manifest.json)只证明初次交付的输入一致性。[repair delta](repair-delta.json)列出变化的原输入及新增上游文件，不再声称旧 manifest 与新 head 全部相同。

## 3. Branch / PR / lineage

同一 published branch `codex/r74-recovery-routing`，唯一 PR [#75](https://github.com/youling/ai-use/pull/75)。本次 WARM_RESUME / REPAIR 由原协调施工 lineage 执行，没有创建新 Fresh Builder 或自称 Global reviewer。原 Builder / readers 的独立性记录不变。

## 4. ADR

[ADR-0004](../../../90_HISTORY/ADR-0004_RECOVERY_ROUTING_SINGLE_SOURCE.md)仍承载原冻结裁决。Review 接受架构方向、三分支恢复、模板瘦身、preflight relocation、provider retirement、实验边界及 L0 不变。repair 使实现符合原裁决，不新增 unrelated Constitution 裁决。

## 5. Changed-file map

[repair-delta.json](repair-delta.json)给出对旧 reviewed head 的改动、对新 main 的完整 PR 文件表、旧 reader source 中受影响的文件。原 [60 文件表](changed-files.json)仅保留初次快照。

| 分组 | Delta |
| --- | --- |
| MAJOR 1 | routing.py / workflow 移除固定 R74 base；新增 opt-in migration proof；独立 Git history regression |
| MAJOR 2 | 仅 Constitution §10、README、Kernel README 的 routing ownership/pointer 表述归一 |
| Accepted upstream | 合入 Gate contract/adapter/workflow；保全 Bootstrap/Interface 内容；catalog 新增 targeted route，生成 views |
| Evidence | 本报告、实验 README、migration map 与 repair delta 区分旧观察和新源码/验证 |

## 6. Recovery semantic migration

[原 relocation map](../../migrations/R74_RECOVERY_ROUTING.md#semantic-relocation-map)保持成立：Recovery §1–3 拥有恰好三个 recovery_kind；§4–5 保全 context 枚举与 independence/delegation，§7 保全 project reproducibility。Interface 仍拥有 continuation/repair/completion，Bootstrap §4 拥有 targeted preflight，Trace 缺旧 checkpoint 时使用 current state。

本次不改 Recovery protocol、templates 或 provider forward。Bootstrap 1.3.0 保留上游 BOOT-3A.1 Gate 和 R1 relocation；Interface 2.6.0 保留上游 2.5.0 Gate 与 R1 指针，解决并行版本号冲突。Gate contract / adapter / Gate workflow 与新 main 完全相同。

## 7. Routing and current prose

[Routing Catalog](../../../ROUTING_CATALOG.yaml)为 19 个 ID：原 18 个不变，新增 local-engineering-gate 指向已接受的 L2 contract，只表达场景/home，不复制 mechanics。四个完整生成投影保持。

Constitution §10、README、Kernel README 的旧“Namespace/Reading Map 决定语义”表述改为 catalog 拥有 routing/applicability interpretation，投影供直接选路；不改 `AGENTS.md`，不作其它 Constitution 清理。

## 8. Compatibility and one-time proof

current compatibility records / paths 保留，七个旧入口 anchors 在本 tranche 通过独立证明。常规 validator 验证当前 pointers，不冻结历史 anchors 或 AGENTS blob。

[check_r74_migration.py](../../../tools/check_r74_migration.py)显式接收 migration base / candidate head，仅供 #74 验收，对两个 Git revisions 比较 L0 bytes 和七份旧入口 anchors。常规 CI 不自动调用它；未来迁移不会被本次历史基线永久约束。旧历史/observations 不改写。

## 9. Checks and Actions

常规命令：`python tools/routing.py --check --check-whitespace --base-ref <current-base-ref>`。检查 19 routes、4 deterministic projections、changed links/anchors、18 copyable surfaces、current compatibility pointers、kernel-only L0 route、当前 diff whitespace。CI 使用 PR base / push before；CLI 显式 base 优先，其次 env，本地默认 HEAD；零 before 使用 empty tree。没有 R74 SHA fallback。

`python tools/test_routing.py` 共 20 项结构测试，包含独立新 Git history 中接受未来 L0/旧锚点迁移、拒绝 event-base 后的 committed whitespace / bad links、CLI override、invalid/zero base、opt-in proof 边界。

本轮另执行 `python tools/check_r74_migration.py --base-ref e6de9acdafbc3b9d12802ecf8de25f444074553b --head-ref <new-head>`。新/改 machine-readable 文件 parse，Gate self-test、Git source/evidence blobs 对账。具体结果、final SHA 与新的 Linux/Windows Actions 由 #74 repair receipt 记录，不用旧 head 绿灯代替。

## 10. Five-reader evidence scope

[原 RESULTS](RESULTS.md)、[measurements](measurements.json)、[scoring](scoring.json)与十份 observations/logs 原样保留：25/25→25/25 canonical topics、五类均可恢复、无 adopted false blocker；合计 emitted bytes 599,317→490,471。

Review 接受该 synthetic evidence 的设计/限制，以及 infrastructure +1.59% emitted-byte 差异不是 blocker。本次不重跑或伪造新五类观察；新 prose / upstream Gate 对实际 reader 成本的影响未复测。原结果仅适用于 recorded source，不能外推为新 head 的阅读成功率。scoped repair 以结构回归和新 exact-head semantic Review 验收。

## 11. L0 semantic diff

`AGENTS.md` 相对 dispatch base、reviewed head、合入 main 均无 Git blob 变化，SHA-256 仍为 `5e1a4885d56fe20ee233ac7a461138054afe8c8f1281b0c9c04fde2170de72e0`。这是 #74 delivery proof，不是 generic validator 对未来 L0 的永久约束。Constitution 仅 §10 一句 correction，其余内容不变；R3/R4/R5 doctrine 不改。

## 12. Remaining limits

结构校验不替代 semantic Review，也不自动批准未来 L0/compatibility 改动。public guard 仍为有限集合，不声称全仓 secret scan/历史清除。原模型实验为单样本 synthetic evidence，受截断/补读影响，未重测 repair 后成本；实际项目 authority/currentness/production acceptance 不能由模型观察推定。L0 保持消费 Namespace/Reading Map 的指针，下层明确其 catalog 投影身份。Global Architect 必须对新 exact head 重新 Review。

## 13. Stop and scope confirmation

R1/R2 repair + necessary accepted-upstream reconciliation only。R3/R4/R5、#66/#67/#68 substantive work、App/PAT/OAuth/Organization、main protection/rulesets/admin settings 未修改。无 PR merge、无 history rewrite、无真实私有 topology 导入。

新 pushed-head 验证及 #74 回执完成后停止于 `READY_FOR_GLOBAL_REVIEW`；不自行接受 finding resolution、不关闭 #73/#74，也不进入后续 tranche。
