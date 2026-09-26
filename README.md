# ai-use

一套围绕 **Human governance + 专职 AI Agent + Git/GitHub durable state** 形成的人机协作方法论。

它的工程出发点很简单：**默认 Human 不可靠、默认 AI 不可靠、默认执行环境不可靠。** 这里的“不可靠”不是价值判断，而是故障模型——Human 会遗忘、分心、离开项目；AI 会丢上下文、漂移、自述失真或突然中断；设备、网络、会话和执行节点会离线、损坏或被替换。ai-use 的目标不是消灭这些故障，而是让系统在这些故障发生后仍然可以从 durable state 恢复、核验并继续。

> 第一次进入？先读 [`START_HERE.md`](START_HERE.md)。准备执行/接管角色时，第一份 normative rules read 是 current [`AGENTS.md`](AGENTS.md) L0。

[路由总览（派生）](docs/ROUTING_INDEX.md) · [路由目录源](ROUTING_CATALOG.yaml)

---

## Why

ai-use 从三个默认故障假设开始：

- **Human 不可靠**：记忆会衰减，注意力会切换，人会离开几天甚至忘记某条施工线；Human 不应成为消息总线、状态数据库或唯一调度时钟。
- **AI 不可靠**：上下文会丢、模型会漂移、Agent 会自述“完成”却缺少 durable evidence，也可能因为 token、provider、网络或会话中断突然消失。
- **执行环境不可靠**：电脑、节点、容器、网络、本地 workspace 和 provider runtime 都可能失效；任何单台设备都应当可丢弃、可替换。

因此，系统把 **Git/GitHub durable state** 作为可恢复协作基础，把聊天和本地现场降为 working cache，并用显式 authority、evidence、checkpoint、review 与 fail-closed gate 对抗这些不可靠性。

AI 很强，但如果只用聊天来驱动它写代码，长期工程会逐渐劣化：

- 聊天记忆会丢，人一走、会话一断，上下文就没了；
- 角色混乱：同一个 AI 既定义需求、又实现、又评审、又宣布"完成"；
- 无限 Review：为了"保险"不断加验证，却没人定义什么时候停；
- 上下文膨胀：每个 Agent 冷启动都要通读全部文档，成本随仓库线性增长；
- 自评完成：靠"我觉得没问题/生产级"收尾，而不是靠可验证证据；
- 多 Agent 相互污染：B 读 A 的结论，C 读 B 的结论，最后一起错。

ai-use 要解决的，不是"让 AI 写更多代码"，而是让 Human 与 AI 以一种**可恢复、可验证、成本与风险相称**的方式长期协作。

---

## Goal

ai-use 不追求让任何单个 Human、AI 或执行节点变得绝对可靠。它追求的是：

> **在参与者与执行环境都可能失败的前提下，让协作系统整体变得更可靠。**

这里的“更可靠”有明确含义：关键事实能够恢复，当前状态能够核验，权限边界能够判断，失败能够被观察，工作能够被其他合格参与者接管，最终结论能够追溯到 durable evidence。

因此，宪法不是某个 Architect 的个人习惯，而是所有参与者共享的协作边界。Human、Architect、Builder、Research、Repair、Verifier、Runner 以及未来新增角色，都处在同一治理体系内。

但**治理覆盖所有参与者，不等于所有参与者都要通读全部治理文本**：

```text
GOVERNANCE_SCOPE = UNIVERSAL
CONTEXT_LOADING = ROLE_SCOPED + SCENE_TARGETED + PROGRESSIVE
```

每个参与者只加载当前角色与当前场景所需的最小充分规则：先获得稳定 Kernel，再根据 role、Work 与 scene 逐层展开；触发更深规则时再继续读取。宪法应当贯穿整个系统，而不是淹没每一个上下文。

这也要求宪法本身具有比普通项目文档更高的语义纪律：**少概念、硬边界、单一语义归属、最小重复、可判定优先。** 能用一个稳定不变量表达的，不写成多套近义规则；能放到下层协议的 mechanics，不塞进 Kernel；任何新增复杂度都必须证明它减少了更大的系统不确定性。

---

## Governance model

```
Human
  └─ Global Architect
       ├─ Project Architect A
       │     ├─ Builder
       │     ├─ Research
       │     └─ Verifier
       ├─ Project Architect B
       │     ├─ Builder
       │     └─ ...
       └─ ...
```

- **Human** 拥有最终主权：决定目标、优先级、接受标准、接受风险与重大治理方向，并可 override / revoke delegated authority。
- 普通 repository merge 可以按 current durable authority 委托给 Architect；production deploy、destructive / irreversible external action 的 authority 独立判断。
- **Human + Global Architect** 共同维护跨项目的"现行法"（宪法、阅读索引、跨项目边界、冲突裁决）。
- **Project Architect** 负责自己项目的架构自治，只背负本项目及必要跨仓契约的上下文。
- **Builder / Research / Repair / Verifier** 是临时、可替换的专业执行角色，不拥有长期治理权。
- **Runner** 是确定性执行与安全工具，不是架构师，不是审批官。

这里描述的是**职责分层**，不是封建审批链：Project Architect 在自己项目内拥有日常架构自治，Global Architect 只在跨项目依赖、共享契约、治理冲突或资源优先级时才介入。

---

## Core ideas

- **Git/GitHub durable state** —— 持久事实源是 Git/GitHub；聊天只是 working memory，本地 workspace 默认可丢弃。
- **evidence > self-report** —— 机器可验证证据（exact-head、tests、Git facts）强于自然语言自评。
- **minimum sufficient workflow** —— 治理强度与真实风险成比例，不做为治理而治理。
- **project-local truth** —— 项目事实留在项目仓，公共方法论不复制私有运行态。
- **layered reading** —— 文档存在于本仓 ≠ 每个 Agent 必读；冷启动成本与任务规模相关，不随文档总量线性增长。
- **independent workspace** —— 写任务使用物理隔离的可变工作区，不覆盖他人现场。
- **verification proportional to observed risk** —— 低风险可直接验收，普通高风险默认最多 1 个独立 Verifier，多验证只在 Incident Mode。
- **convergence > ceremony** —— 收敛优先于仪式完整。

---

## Read this repo

| 文件 | 给谁看 | 何时读 |
| --- | --- | --- |
| [`START_HERE.md`](START_HERE.md) | 全角色（首次进入者） | 第一次进入 ai-use、需要知道从哪开始 / 如何初始化 workspace 时 |
| [`CONSTITUTION.md`](CONSTITUTION.md) | 全角色（尤其 Architect） | 治理冲突、重大裁决、理解体系时；普通任务不必通读 |
| [`READING_MAP.md`](READING_MAP.md) | 全角色（机器/人类导航） | L0 已加载后，需要知道当前角色/场景该 targeted 读什么时 |
| [`NAMESPACE.md`](NAMESPACE.md) | 全角色（zero-prompt 路由） | L0 后理解 `00→10→20→30→40→50→90` 的默认 next-hop chain；可 `SKIP` / `STOP_*`，不是 mandatory full-read order |
| [`AGENTS.md`](AGENTS.md) | 所有执行 Agent（机器 L0） | 每个执行/恢复/接管角色进入 normative rules 时首先读取 |
| [`human/README.md`](human/README.md) | 二脑协作者 / Human | 跨 AI 记录 Human、日终提炼、上下文漂移后冷启动或切换协作者时 |
| [Recovery & Handoff](30_PROTOCOLS/RECOVERY_HANDOFF.md) | 需要恢复、交接或 context 判定的人 | 当前三分支 recovery 与 context contract；[旧 Session 路径](docs/SESSION_LIFECYCLE.md) 只保留兼容转向 |
| [`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`](10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md) | 所有执行 Agent | 启动状态验证（L2 按需） |
| [`10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`](10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md) | 新组织 / Global Architect | 初始化 workspace、发现仓库角色、确认 Global Architect Ready（L2 按需） |
| [`30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`](30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) | 所有执行 Agent | 需要留痕/返回 pointer 时（L2 按需） |
| [`00_KERNEL/LANGUAGE_POLICY.md`](00_KERNEL/LANGUAGE_POLICY.md) | 所有执行 Agent | 人类可见输出默认简体中文（L2 按需） |

一句话版：**不要通读整个仓库。** `START_HERE` 只做导航；执行/恢复/接管时先加载 `AGENTS.md` L0，随后通过 [Routing Catalog](ROUTING_CATALOG.yaml) 的生成投影选路：`NAMESPACE.md` 展示 zero-prompt 下一跳，`READING_MAP.md` 展示当前层 `NEXT | SKIP | STOP_*` 与 targeted homes。routing / applicability interpretation 归 catalog，投影不另立解释源。普通执行者通常只需要 L0 + 自己的精确任务 + 项目本地上下文。

---

## governance repo vs control-plane role

| | governance repo（通常是 `ai-use` fork/clone） | `control_plane` role（仓库名由部署方自定） |
| --- | --- | --- |
| 性质 | 公开/可复用的方法论、治理体系、协作模式 | 部署实例自己的控制面 / runtime |
| 内容 | 原则、角色、模式、案例、rationale、阅读索引 | Work Order、项目路由、执行现场、安全核验、少量机器契约 |
| 定位 | 当前 governance repo 本身 | 由 `workspace_registry.control_plane.repo` 或等价 deployment registration 解析 |

`ai-hub` 只是一个常见的 control-plane 仓库命名示例，**不是公共 ai-use 指向上游维护者某个私有仓库的固定地址**。

ai-use **不负责**私有项目实时状态、active project topology、Runner runtime、本地 workspace 状态、私有 registry、当前谁在跑什么任务。这些属于部署实例自己的 `control_plane` role 或各项目仓。

本仓不保存具体私有项目的实时拓扑与状态，也不要求公共使用者读取任何上游维护者的私有控制面。

---

## License

见 [`LICENSE`](LICENSE)。
