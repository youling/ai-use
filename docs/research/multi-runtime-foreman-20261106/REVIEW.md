# 总架构师审查记录与修订清单

关联 [#183](https://github.com/youling/ai-use/issues/183)。[总架构师 Review 5802110535](https://github.com/youling/ai-use/pull/184#pullrequestreview-5802110535) 已审阅原 head `1f733967a617179fa5aa364ec932c7e71d372944`，裁决为 **QUALIFIED_RESEARCH_ACCEPTANCE / NOT_READY_FOR_MERGE**：有条件接受 L3 案例与操作经验，要求先修 R1/R2。下表记录这次已经发生的裁决；运行器、模型及产品验证没有因此通过。

2026-11-11 修订依据：[DIRECT 历史纠正与有界修订回执](https://github.com/youling/ai-use/issues/183#issuecomment-6777678884)。本次补 DIRECT/DELEGATE 反例、更新审查状态并去除新正文私有 locator；该修订的精确 HEAD、delta Review、检查与最终收录事实统一见 [PR #184](https://github.com/youling/ai-use/pull/184) 的当前记录。

## 建议审阅顺序

1. 先看 [README §1](README.md#1-先纠正本次成绩的表述)：三执行器的结果并不相同。
2. 看 [旧经验差距表](README.md#2-旧经验哪些正确哪些需要补足)：区分执行偏差与手册缺口。
3. 有实例权限时从 owner 回执抽核原件；无权限时将事实置信度限制在作者去敏报告。
4. 按下表已有裁决核对本次修订与剩余缺口；只有明确需要规则变化才另走当前 Change Lifecycle，不因这份研究自动改 normative 文件。

| 编号 | 结论主题 | 证据类别 | 总架构师裁决与保留边界 |
|---|---|---|---|
| K01 | 保留旧 Foreman/Async 的角色、父验收、durable 规则 | 既有 canonical 文本 + 本次偏差 | **保留现行规则**。没有证据支持重造 Foreman 权责；本次偏差应纠正执行。 |
| K02 | 接入探针区分入口、身份、真实模型、工具、产物 | ZCode 探针、原生错误、实际运行对照 | **采纳为 L3 操作经验**。按当前 provider/version 选最小检查，不变成所有 Agent 的强制五步仪式。 |
| K03 | 工具拒绝需要逐层、逐目标看实际回执 | 空 SUCCESS + denied_actions；窄权限候选与后续产物 | **采纳为 L3 反例**。一次 regex/文件匹配行为不是公共稳定 API，也不准许绕过拒绝。 |
| K04 | 中断交接保留 source + dirty/未跟踪 + 产物/测试，先停旧 writer | 免费限额事件、中断快照、后继任务范围 | **采纳方法，实测缺口保留**。source/dirty/untracked、可恢复位置与旧 writer 停止须有回读；本稿未证明每次均无并发写域冲突。 |
| K05 | 双端共享核心与平台任务分开分配 | Flutter 共享目录与两平台执行路径 | **保留现行原则并采纳实例教训**。互斥还涉及 SDK/cache、设备和账号，不从目录不同推断完全隔离。 |
| K06 | 运行器 SUCCESS、构建、安装、可用、性能分别验收 | 原生输出、测试、现场观察与未接入能力 | **保留现行证据原则，接受案例**。100 PASS / 1 SKIP 只覆盖对应测试；登录、媒体、AI/性能仍未验收，不能降低产品目标。 |
| K07 | 研究关键结论必须有直接来源、日期和未知 | 被退回的 AI/富文本初稿及二次纠偏 | **采纳审查优先级，独立结论仍待证**。纠正初稿不代替重新核验被纠正的价格、竞品与服务能力。 |
| K08 | 聊天投递、接单、持久交付和审阅分开记录 | 跨对话 Work/接单/精确 PR 回执；本次 DIRECT 事件名误用 | **采纳操作澄清，并修 R1**。不新增 Work/attempt state；DIRECT 以真实 PR、HEAD、checks、Review 留痕，不制造 delegated CLAIM/TERMINAL。 |
| K09 | 工时与 resume 累计指标分开，避免宣传提速 | 额度暂停、平台等待、旧累计指标经验 | **保留 UNKNOWN，量化结论暂缓**。没有完整增量账单或有界对照，不报精确费用或加速倍数。 |
| K10 | 旧截图和当前代码/安装版本分别标记 | 截图 hash、安装信息、未成功的新截图采集 | **采纳 currentness 约束，现场缺口保留**。没有新 APK/source/真机截图对应性验收，也未补齐双端截图。 |

## 本次修订与原文件范围

- 新增 `docs/research/multi-runtime-foreman-20261106/README.md` 与本文件。
- 在研究总入口和 Antigravity 经验入口记录有条件审查状态，不重写其旧失败、旧版本和 QUALIFIED_SYNTHETIC_ONLY 范围。
- R1：#183 已追加历史更正，旧评论保留；本文与 README 补 DIRECT/DELEGATE 反例。误用事件名不产生真实 delegated dispatch/claim/terminal、owner 或验收。
- R2：记录既有 Review 与 K01–K10 裁决；K04/K07/K09/K10 的缺口继续保留，修订收录状态使用 PR 的精确版本记录。
- 新 README 的私有原件 locator 已替换为 source-class 描述；原始记录继续由实例 owner 受控保管，没有迁入公共仓。
- **不修改** AGENTS、Foreman canonical role、Agent Interface、权限、调度器、运行器或默认 provider。
- 若总架构师认为需要晋升规则，另在对应 owner 文件形成明确语义差异和验收；不能通过一次 research merge 隐式扩权。

## 审查与验收状态

- [x] 原 head 已完成具名总架构师有条件语义审阅；仅属 L3 经验审查，不是独立 runtime 验证。
- [x] 原稿三执行器成绩范围获接受；ZCode 仍没有模型施工成功证据。
- [x] 旧规则执行偏差与操作缺口已分类，K01–K10 已分别作出上述裁决。
- [x] #183 已追加 DIRECT 事件名称历史纠正；不改写旧评论，不伪造 delegated attempt。

本次修订的收录证据集中在 [PR #184](https://github.com/youling/ai-use/pull/184)：对应精确 HEAD 的 delta Review、文档/链接与公开边界检查、远端读回，以及有权限 owner 的最终合并决定。本文保留已发生的研究裁决与证据边界，不另复制一份易过期的 PR 状态清单。

K04/K07/K09/K10 的未完成实证不属于上面已勾选的“审查发生”事实；它们继续待证，不因文档收录变为 PASS。

## 未经过的验证

没有重新跑三供应商认证、模型推理、ZCode 生产接入、OS 权限对抗、完整双端功能或计费对照。文字/链接/hash检查不替代这些验证，也不替代总架构师审核。
