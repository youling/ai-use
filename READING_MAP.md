# Reading Map

**DO NOT READ EVERYTHING.**

本仓会持续增长；默认 cold-start cost 必须与当前 task 规模相关，**不随 ai-use 文档总量线性增长**。准备执行 / 恢复 / 接管时先加载 `AGENTS.md` L0；之后由 `NAMESPACE.md` 的 zero-prompt chain + 本表 scene trigger 自主选择下一跳。

---

## 阅读层级

- **L0 Kernel** —— 极少量、stable、cross-role invariants；默认 execution/recovery/takeover 必须加载。
- **L1 Role / Task Context** —— current role、Work Order、target-local README/AGENTS/contract 等直接上下文。
- **L2 Targeted Reference** —— scene trigger 后才读取的 canonical mechanics / protocol / guide。
- **L3 Rationale / Case / Archive** —— 理念、案例、历史；默认不进入 execution context。

规范适用顺序仍是 `BOOT-1 -> BOOT-2 -> BOOT-3`。`BOOT-1` 可做 pure addressing；进入 normative rules 时 `BOOT-2A` 先加载 current governance repo `AGENTS.md` L0，再进入 target-local/current-work。完整 mechanics 见 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`。

`AGENTS.md 3.0.0` 以后，L0 **不再复制 downstream mechanics**。一条语义没有常驻 L0，不代表语义被删除；当 scene trigger 命中时，本表必须把 Agent 路由到它的 canonical home。

---

## Zero-prompt 链式路由

`NAMESPACE.md` 保留 `00 -> 10 -> 20 -> 30 -> 40 -> 50 -> 90` 默认 chain。本表负责每一跳：

- `NEXT` —— scene/role 命中；只读 targeted canonical content，再继续；
- `SKIP` —— 当前层无适用内容；不读正文；
- `STOP_READY` —— minimum sufficient context + current execution gates 已满足；退出文档链进入执行；
- `STOP_BLOCKED` —— 真实 blocker；停止并报告 exact gate。

**zero-prompt != full-read**。没有 Human 新提示本身不是 blocker；若唯一缺口是“下一份该读什么”，继续按 Namespace + Reading Map 自主路由。

---

## Canonical semantic homes

| Semantic | Canonical home |
| --- | --- |
| L0 authority/truth/scope/fail-closed primitives | `AGENTS.md` |
| Governance hierarchy / merge principle / verification / Incident | `CONSTITUTION.md` |
| Bootstrap + GitHub access/currentness mechanics | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| Workspace role registration / initialization | `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md` |
| Common mutation workspace/scope hygiene；DIRECT / DELEGATE / dispatch / continuation / Maintenance Lane | `docs/AGENT_INTERFACE.md` |
| Fresh/takeover material architecture current-state alignment；stage-aware external reuse / External Wheel Admission Gate | `docs/ARCHITECT_RECONNAISSANCE.md` |
| Durable checkpoints / recovery trace | `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md` |
| Docs-as-code / code+document change level / Issue-ADR-PR lifecycle | `30_PROTOCOLS/CHANGE_LIFECYCLE.md` |
| Diagram-as-code / topology navigation / diagram currentness | `30_PROTOCOLS/DIAGRAM_AS_CODE.md` |
| Durable business data / data model / schema migration | `docs/DURABLE_DATA_DOCTRINE.md` |
| Human-facing language details / override | `00_KERNEL/LANGUAGE_POLICY.md` |
| Work Context lifecycle / durable-before-fragile / fresh triggers (playbook) | `docs/SESSION_LIFECYCLE.md` §10 |
| Context / mode / continuation / independence / delegation copyable contract | `50_TEMPLATES/CONTEXT_MODE_SEED.md` |
| zero-prompt next-hop | `NAMESPACE.md` + this map |

其它文档只引用，不复制完整 mechanics。

---

## 角色 / 场景阅读表

| 角色/场景 | 默认读取 (L0) | 按需读取 (L1/L2) | 默认不读 |
| --- | --- | --- | --- |
| **Generic Executor** | `AGENTS.md` | current target-local rules、exact Work Order/Dispatch、owns scope；任何 mutation/workspace ownership scene -> Agent Interface §1.0；startup/recovery -> Bootstrap；Completion/Seed interface -> Agent Interface | full Constitution、Session Lifecycle、其它项目、governance rationale |
| **Project Architect** | `AGENTS.md` | target project README/architecture index/current active graph；startup/recovery -> Bootstrap；material new-domain/pivot、成熟项目拟引入新 external framework/runtime/subsystem -> Reconnaissance；mutation hygiene / `DIRECT | DELEGATE` / dispatch / Review/Repair/continuation -> Agent Interface；docs/code material change classification -> Change Lifecycle；复杂 topology / ownership / lifecycle / status visualization -> Diagram-as-Code；merge/verification/Incident/governance conflict -> Constitution；identity-sensitive GitHub mutation -> project-local identity/access mapping（若有）；仅明确依赖时读 cross-repo contract | 其它项目代码、全量 ai-use、整个 workspace open work |
| **Global Architect** | `AGENTS.md` | current governance canonical source + targeted project summary；workspace init -> Workspace Bootstrap；material architecture/governance direction、成熟项目 external reuse/import 裁决 -> Reconnaissance；mutation hygiene / execution/dispatch/continuation/Maintenance Lane -> Agent Interface；docs/code material change classification -> Change Lifecycle；portfolio topology / cross-project status / architecture delta -> Diagram-as-Code；merge/verification/Incident/governance conflict -> Constitution；identity-sensitive mutation -> target-local identity/access mapping | 为普通任务扫描所有项目代码/全部 open work |
| **Builder / Research / Repair** | `AGENTS.md` | exact Dispatch/Work Order、target-local rules、owns content；mutation/workspace hygiene + Seed/Completion/interface -> Agent Interface；startup gate -> Bootstrap；durable checkpoint -> Durable Trace；只有派单要求产出/修改治理 Artifact 或判定 L0/L1/L2 时读 Change Lifecycle；只有派单要求创建/修改 diagram source 时读 Diagram-as-Code | full Constitution、governance rationale、unrelated project context |
| **Verifier** | `AGENTS.md` | original requirements、exact-head diff/code/tests、current verification contract；若会 mutation/repair workspace -> Agent Interface §1.0；verification policy ambiguity -> Constitution；Completion interface -> Agent Interface | Builder self-report 作为结论、unrelated docs |
| **Release** | `AGENTS.md` | exact release dispatch、current PR/head/merge/cleanup facts；任何 cleanup/mutation -> Agent Interface §1.0；merge authority -> Constitution；startup/currentness -> Bootstrap | 为 cleanup 重建全项目历史 |
| **Incident** | `AGENTS.md` | `CONSTITUTION.md` §8 + incident-relevant targeted references/evidence | —— |

---

## 场景触发（L2）

| 场景 | 读什么 |
| --- | --- |
| Public entry / 第一次不知道从哪开始 | `START_HERE.md`；只做 navigation |
| zero-prompt next-hop | `NAMESPACE.md` 给 chain；本表判断 `NEXT | SKIP | STOP_*` |
| startup / recovery / access / live-state gate | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| workspace initialization / role registration | `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md` + `50_TEMPLATES/HUMAN_WORKSPACE_BOOTSTRAP.md` |
| any write/mutation / workspace ownership / scope hygiene | `docs/AGENT_INTERFACE.md` §1.0；适用于 Direct 与 delegated executor |
| Fresh/takeover Architect material architecture；material new-domain / major capability / major pivot | `docs/ARCHITECT_RECONNAISSANCE.md`；Bootstrap `EXECUTION_ALLOWED` 后完成适用的 ARCH-0，再进入 `ARCHITECT_READY` |
| mature/production project 拟直接引入新的 OSS/framework/runtime/subsystem/重型依赖 | `docs/ARCHITECT_RECONNAISSANCE.md` §5；先判 project stage，再过 External Wheel Admission Gate；默认不得把“发现可用代码”直接等价为“应导入依赖” |
| ordinary Architect Hot Resume / small bug / deterministic maintenance | 不机械重复 ARCH-0；只对可能改变方案的 external delta targeted refresh |
| Architect 选择 DIRECT/DELEGATE、dispatch/review/repair、continuous advancement、Maintenance Lane | `docs/AGENT_INTERFACE.md` |
| Human Dispatch / Minimal Seed / Completion Card / execution dependency taxonomy | `docs/AGENT_INTERFACE.md` |
| 文档即代码、代码/文档变更分级、Issue/ADR/PR 留痕、周期性文档维护 | `30_PROTOCOLS/CHANGE_LIFECYCLE.md`；需要可复制形态再读 `50_TEMPLATES/CHANGE_LIFECYCLE.md` |
| 复杂架构图 / ownership topology / status overlay / workflow / sequence / dataflow / lifecycle / diagram drift | `30_PROTOCOLS/DIAGRAM_AS_CODE.md`；需要可复制形态再读 `50_TEMPLATES/DIAGRAM_AS_CODE.md` |
| repository merge authority / merge gate | `CONSTITUTION.md` §2 + current project/local contract；identity-sensitive 时再读 project-local identity/access mapping |
| verification policy / Incident Mode | `CONSTITUTION.md` §§7–8 + task-specific verification contract |
| execution continuation / WARM_RESUME / PREMATURE_YIELD / completion boundary | `docs/AGENT_INTERFACE.md` §1.4 / §1.6–§1.9 |
| Work Context lifecycle / durable-before-fragile / fresh triggers | `docs/SESSION_LIFECYCLE.md` §10 |
| context / mode / delegation copyable contract | `50_TEMPLATES/CONTEXT_MODE_SEED.md`；日常先读 `50_TEMPLATES/DISPATCH_PAIR.md` 的 pointer |
| durable trace / checkpoint / recovery trace | `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md` |
| durable business data / data model / schema migration | `docs/DURABLE_DATA_DOCTRINE.md` |
| Human-facing language/override ambiguity | `00_KERNEL/LANGUAGE_POLICY.md`；L0 只保留 default + pointer |
| session / handoff / recovery playbook | **先 Bootstrap** 恢复 current authority/access/live state；`docs/SESSION_LIFECYCLE.md` 只作 compatibility playbook |
| public cold-start / Kernel ABI regression | `40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md` |
| architecture conflict / cross-project governance | `CONSTITUTION.md` + explicit dependent contract |
| security / permission boundary | relevant current security/project reference；缺失则 fail closed |

---

## Session Lifecycle compatibility note

`docs/SESSION_LIFECYCLE.md` §10 是 Work Context lifecycle 的 current playbook；continuation 与完成边界的 authority 仍在 `docs/AGENT_INTERFACE.md`。早期模板说明如下：

`docs/SESSION_LIFECYCLE.md` 包含早期完整模板，保留 recovery/handoff 背景价值，但不是 current bootstrap/execution authority。特别是：

- 恢复单一 project 不默认扫描整个 workspace 所有 OPEN Work Orders；只读 current target project/program 的 targeted active graph；
- “先给 Human 确认后再继续”不是通用 stop；current continuation 以 `docs/AGENT_INTERFACE.md` 为 canonical；
- provider/model/runtime 示例不是 Minimal Seed canonical fields；
- historical template 与 L0 / Bootstrap / Agent Interface 冲突时，先用 L0 判断并隔离 lower-layer drift。

---

## 默认规则

> 新 ai-use 文档默认属于 **L2/L3**，除非本 Reading Map 明确提升为 **L0/L1**。

提升到 L0 前必须通过 `AGENTS.md` / `00_KERNEL/README.md` 的 Kernel Residency Test。这样 ai-use 可以继续增长，而 Kernel 与 default bootstrap context 不随功能线性膨胀。
