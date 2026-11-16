# ai-use Diagrams

本目录保存 ai-use 自己拥有语义的 **DERIVED Diagram-as-Code source**。图用于 Human / Fresh Architect / Fresh Agent 导航，不产生治理 authority。

## Project L1

- `project.architecture.json` — ai-use Project Detail Map。
- diagram type: `architecture`
- renderer target: Archify v3.0.1 exact commit `2ab3cae7ac2c2a55d7386ca789d03c4fcd31816c`
- semantic source baseline: `ai-use@2e524b071c1b0864bdcee6fa90592f7a7dd40f9a`
- presentation consumer: deployment-local Architecture Navigator or any compatible renderer

它回答：authority、L0、routing、roles、Architect Discovery / ARCH-0、Foreman execution/recovery、末端研究分诊、执行上下文来源、精确指针交接、本地 Worksite Log、软件工程与阶段图复盘、durable truth、Human Host、Diagram-as-Code、owner boundary、guides/templates/history、**Fresh/takeover 冷启动后的定向 Issue 主题收敛**，以及 Agent Runtime 公共参考源码如何分工。研究入口仍为 L3，不将 Antigravity 合成试跑、Magpie 有限调用或其它 Draft 当成当前生产节点。

首次接手的 Architect 使用图中“Architect 冷启动、Issue 收敛与执行”视图定位下一跳；BOOT 完成后，沿 [GitHub Native First §4.2](../../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md#42-冷启动后的-issue-主题收敛少入口不丢原子-work) 定向核查，不要求全仓扫描；role 节点 `sources[]` 指向 ARCH-0 与 Foreman 等当前 owner 的规范，而不是要求逐页通读所有文件。Material architecture 决策应下钻 `20_ROLES/ARCHITECT_DISCOVERY.md` → `docs/ARCHITECT_RECONNAISSANCE.md`；普通 Work 可按当前 Bootstrap/Work 继续，不因总图存在额外 mandatory hop。

## 本轮图示对齐（2026-11-17 源快照）

规范取自已接受的 `main@2e524b071c1b0864bdcee6fa90592f7a7dd40f9a`；其中 PR #190 在 `039ae52269863463c1e418b9e0fb7b9c4c65a751` 合并，PR #188 随后作为 L3 研究收录，PR #182 完成独立 L2 审查后接受为公共 OCI 离线验证子集。下表 Issue/PR 状态来自本轮实时回读，属于注明日期的派生快照，不是新增工作台账。

| 图中主题 | 已接受源码／本轮回读状态 | 下一跳 |
| --- | --- | --- |
| Fresh/takeover Issue 收敛 | **已合并治理规范**。BOOT-3C 后、当前 owner/target 相关工单的有界主题归并；不是新的启动 Gate | [GitHub Native First §4.2](../../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md#42-冷启动后的-issue-主题收敛少入口不丢原子-work) / [ADR-0023](../../90_HISTORY/ADR-0023_POST_BOOTSTRAP_ISSUE_CONVERGENCE.md) |
| 末端研究／环境来源／指针交接 | [PR #190](https://github.com/youling/ai-use/pull/190) **已合并**，[#189](https://github.com/youling/ai-use/issues/189) 已关闭。按任务未知选择研究路线，将环境与证据绑定，按精确指针接续；不新增角色、审批层或全任务联网要求 | [Agent Interface §1.0.1–1.0.3](../../docs/AGENT_INTERFACE.md) / [Execution Context Provenance](../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md#execution-context-provenance--执行上下文来源) |
| Public Agent Runtime | **参考源码与首次公共 OCI candidate 已接受**；历史匿名 exact-digest 验证不代表 stable、后续发行或 Host 部署 | [发行回执](https://github.com/youling/ai-use/issues/123#issuecomment-6044487814) / [关闭裁决](https://github.com/youling/ai-use/issues/123#issuecomment-6247066989) / [release contract](../../agent-runtime/release/README.md) |
| Windows Setup 候选 | [PR #145](https://github.com/youling/ai-use/pull/145) 的原生窗口／当前 owner 验收仍 HOLD；[PR #162](https://github.com/youling/ai-use/pull/162) 仍为以 PR145 分支作 base 的 Draft，组合树与独立源码接受尚待 | [Setup 当前接续](https://github.com/youling/ai-use/issues/127#issuecomment-6931377676)；保留既有实施 owner 与源码／现场验收边界 |
| 通用 OCI Artifact Supply | [PR #182](https://github.com/youling/ai-use/pull/182) **已合并 Tranche A 离线子集**；5 项独立审查问题已修复，Windows/Ubuntu 各 28 tests，8 项 CI 通过；不证明真实构建/传输/接收 | [能力合同](../../capabilities/oci/CONTRACT.md) / [后续阶段入口](https://github.com/youling/ai-use/issues/181#issuecomment-6931596749)；保持 local-first 与原 owner |
| GitHub 调度总览 | [#167](https://github.com/youling/ai-use/issues/167) 的 Saved Views / 私有 Project 少量试点仍待部署 owner 实施；本轮工单收敛与文档更新不等于该界面已配置 | 使用原生 Issue 关系和现有 owner 事实；配置与实例权限另行核对 |
| Worksite Log / 产物定位 | [PR #174](https://github.com/youling/ai-use/pull/174) **已合并公共合同**；现场记录不产生 claim，不证明离机备份 | [Local Worksite Log](../../30_PROTOCOLS/LOCAL_WORKSITE_LOG.md) / [Durable Trace](../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) |
| 软件工程 / 阶段图示 | [PR #178](https://github.com/youling/ai-use/pull/178) **已合并方法规范**；允许 current 图复用与窄修复 NOT_APPLICABLE，不证明真实项目效果 | [Software Architecture Practice](../../30_PROTOCOLS/SOFTWARE_ARCHITECTURE_PRACTICE.md) / [Diagram-as-Code §3.1](../../30_PROTOCOLS/DIAGRAM_AS_CODE.md#31-阶段性进展图示与领域边界复盘) |
| 跨执行器经验 | [PR #184](https://github.com/youling/ai-use/pull/184) 已收录为 L3 有条件研究；[PR #158](https://github.com/youling/ai-use/pull/158) / [PR #159](https://github.com/youling/ai-use/pull/159) 的历史观察也已合并 | 研究记录保留各自证据范围，不代表运行认证或完整产品验收 |
| ZCode／Magpie 有限研究 | [PR #188](https://github.com/youling/ai-use/pull/188) 修订已合并，**仅接受 L3 记录**；Desktop 工作流、Magpie 本机调用与 standalone CLI 分开，CLI 仍 `NOT_PASSED`，远端能力未知 | [ZCode 研究](../research/zcode-cli-20261112/README.md) / [Magpie 研究](../research/magpie-cli-bridge-20261112/README.md)；去敏与文档 CI 不等于新增运行验收 |
| Change-aware Work Graph | 下游契约变化的影响传播、重新规划和旧验收失效**未完成通用实现**；独立于已接受的 Issue 收敛 | [ADR-0023 已标注缺口](../../90_HISTORY/ADR-0023_POST_BOOTSTRAP_ISSUE_CONVERGENCE.md)；部署侧 [ai-hub #131](https://github.com/youling/ai-hub/issues/131) |

本图维持 16 个 L1 节点、21 条边及既有布局：Issue 收敛在 GitHub Native/Bootstrap，末端研究与精确指针交接归 Agent Interface，环境来源与 Worksite Log 在 Recovery；工程方法与阶段复盘仍通过 Diagram 的 `sources[]` 下钻，公共 Runtime、OCI 离线子集与后续验收边界归入同一个可选工具入口，工具节点用已接受 OCI 合同指针替换重复的通用 Reading Map 指针；通用导航仍由 routing 节点拥有，每个节点保持最多三个来源。候选 PR、Change-aware 未实现的缺口和真实项目验收各回 owner Issue/PR，不因图中有线而升级状态。Projects 工作总览、领域图下钻与执行/Human Gate 分别消费原有 owner 事实，公开图不复制部署账号、私有拓扑或第二份 Work 账。

本图可以供外部使用者和 Agent 使用，但 `meta.repository.revision` 是编译时源快照，不代表 PR 的状态从此不再变化。读到候选/未实施节点时先回各自的 owner GitHub 当前状态，不因为图上有线就从公共治理仓向别人的设备发指令。图中所有 `sources[]` 都应指向该快照已经存在的 canonical 文件；候选 PR 的 URL 只作非规范导航。

## Authority

```text
AGENTS / CONSTITUTION / protocol canonical docs
        = CANONICAL

docs/diagrams/project.architecture.json
        = DERIVED NAVIGATION

rendered HTML / SVG / screenshot
        = DERIVED PRESENTATION
```

图与 canonical source 冲突时，以 canonical source 为准并修图。

## Currentness

`meta.repository.revision` 表示本图本次语义编译所依据的 exact canonical source snapshot，而不是“文件自身永远 current”的声明。

Owner repo main 发生 material semantic drift 后，Project Architect 应重新 live-read、更新 source revision/节点/边并重新验证。Navigator 可以另外显示它消费时的 exact diagram-source revision 与 freshness。

## Cross-repo consumption

ai-hub / Architecture Navigator 只允许：

- read exact accepted owner source；
- validate/render；
- stamp source repository/revision/verified_at/freshness；
- 提供 Portfolio -> Project drill-down route。

不得在 ai-hub 复制一份可独立演化的 ai-use 项目架构语义。

## Source pointers

规范/角色节点的 `sources[]` 指向 ai-use 内 canonical homes；`Research / History / ADR` 节点另外提供清楚标记为非规范的研究索引。来源文档不会因图形展示而获得更高 authority。验证时应对 semantic source baseline 使用 repository-backed validation；source path 不存在、revision 不匹配或行/路径越界都应 fail closed。

参见：[`../../30_PROTOCOLS/DIAGRAM_AS_CODE.md`](../../30_PROTOCOLS/DIAGRAM_AS_CODE.md)。

## Owner-side verification

`.github/workflows/project-diagram.yml` 只在本图/README/自身 workflow 变化时运行：读取图中 `meta.repository.revision`，checkout exact semantic source snapshot，再用 pinned Archify v3.0.1 做 repository-backed `validate + deliver --quality showcase`。

这条 CI 只证明 schema / source-path evidence / layout / deterministic delivery；不证明治理语义正确，也不替代 Architect Review。
