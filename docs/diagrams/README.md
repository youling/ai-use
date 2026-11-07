# ai-use Diagrams

本目录保存 ai-use 自己拥有语义的 **DERIVED Diagram-as-Code source**。图用于 Human / Fresh Architect / Fresh Agent 导航，不产生治理 authority。

## Project L1

- `project.architecture.json` — ai-use Project Detail Map。
- diagram type: `architecture`
- renderer target: Archify v3.0.1 exact commit `2ab3cae7ac2c2a55d7386ca789d03c4fcd31816c`
- semantic source baseline: `ai-use@8ac796fc6488f2a6f9a0923321b44409318cb5e1`
- presentation consumer: deployment-local Architecture Navigator or any compatible renderer

它回答：authority、L0、routing、roles、Architect Discovery / ARCH-0、Foreman execution/recovery、durable truth、Human Host、Diagram-as-Code、owner boundary、guides/templates/history、**Fresh/takeover 冷启动后的定向 Issue 主题收敛**，以及 Agent Runtime 公共参考源码如何分工。研究入口仍为 L3，不将 Antigravity 合成试跑、Magpie 提案或其它 Draft 当成当前生产节点。

首次接手的 Architect 使用图中“Architect 冷启动与执行闭环”视图定位下一跳；BOOT 完成后可按“已生效的冷启动 Issue 收敛”视图定向核查，不要求全仓扫描；role 节点 `sources[]` 指向 ARCH-0 与 Foreman 等当前 owner 的规范，而不是要求逐页通读所有文件。Material architecture 决策应下钻 `20_ROLES/ARCHITECT_DISCOVERY.md` → `docs/ARCHITECT_RECONNAISSANCE.md`；普通 Work 可按当前 Bootstrap/Work 继续，不因总图存在额外 mandatory hop。

## 本轮图示对齐（2026-11-08 源快照）

| 图中主题 | 该源码基准能证明的状态 | 下一跳 |
| --- | --- | --- |
| Fresh/takeover Issue 收敛 | **已合并治理规范**。BOOT-3C 后、当前 owner/target 相关工单的有界主题归并；不是新的启动 Gate | [GitHub Native First §4.2](../../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md#42-冷启动后的-issue-主题收敛少入口不丢原子-work) / [ADR-0023](../../90_HISTORY/ADR-0023_POST_BOOTSTRAP_ISSUE_CONVERGENCE.md) |
| Public Agent Runtime | **参考源码已进入 main**；首次 OCI/GHCR 制品发布未获验收 | [agent-runtime/README](../../agent-runtime/README.md) / [release contract](../../agent-runtime/release/README.md) |
| 通用 OCI Artifact Supply | [PR #182](https://github.com/youling/ai-use/pull/182) 在该基准时为 OPEN，**尚未纳入 main** | PR 的当前 diff/Review/CI；不得将候选文件冒充已接受公共接口 |
| Worksite Log、阶段化软件工程、跨执行器经验 | [PR #174](https://github.com/youling/ai-use/pull/174)、[PR #178](https://github.com/youling/ai-use/pull/178) 在该基准时仍 OPEN；[PR #184](https://github.com/youling/ai-use/pull/184) 为 Draft | 各 PR 的 current HEAD 与证据；在合并前只视为候选 |
| Change-aware Work Graph | 下游契约变化的影响传播、重新规划和旧验收失效**未完成通用实现**；独立于已接受的 Issue 收敛 | [ADR-0023 已标注缺口](../../90_HISTORY/ADR-0023_POST_BOOTSTRAP_ISSUE_CONVERGENCE.md)；部署侧 [ai-hub #131](https://github.com/youling/ai-hub/issues/131) |

新增的 **Work convergence / Public runtime / Candidate proposals / Change-aware gap** 是导航节点，不构成与既有 GitHub Issues、项目源码或部署控制面平行的四份状态库。尤其右侧的外部/待实现节点表示**职责及缺口**，不是声称运行中存在完整的变更感知调度服务。

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
