# ai-use

一套围绕 **Human governance + 专职 AI Agent + Git/GitHub durable state** 形成的人机协作方法论。

> 第一次进入？先读 [`START_HERE.md`](START_HERE.md)。准备执行/接管角色时，第一份 normative rules read 是 current [`AGENTS.md`](AGENTS.md) L0。

---

## Why

AI 很强，但如果只用聊天来驱动它写代码，长期工程会逐渐劣化：

- 聊天记忆会丢，人一走、会话一断，上下文就没了；
- 角色混乱：同一个 AI 既定义需求、又实现、又评审、又宣布"完成"；
- 无限 Review：为了"保险"不断加验证，却没人定义什么时候停；
- 上下文膨胀：每个 Agent 冷启动都要通读全部文档，成本随仓库线性增长；
- 自评完成：靠"我觉得没问题/生产级"收尾，而不是靠可验证证据；
- 多 Agent 相互污染：B 读 A 的结论，C 读 B 的结论，最后一起错。

ai-use 要解决的，不是"让 AI 写更多代码"，而是让 Human 与 AI 以一种**可恢复、可验证、成本与风险相称**的方式长期协作。

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
| [`docs/SESSION_LIFECYCLE.md`](docs/SESSION_LIFECYCLE.md) | Architect / 需要恢复或交接的人 | L2 按需参考，仅在 session/handoff/recovery 场景触发 |
| [`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`](10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md) | 所有执行 Agent | 启动状态验证（L2 按需） |
| [`10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`](10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md) | 新组织 / Global Architect | 初始化 workspace、发现仓库角色、确认 Global Architect Ready（L2 按需） |
| [`30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`](30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) | 所有执行 Agent | 需要留痕/返回 pointer 时（L2 按需） |
| [`00_KERNEL/LANGUAGE_POLICY.md`](00_KERNEL/LANGUAGE_POLICY.md) | 所有执行 Agent | 人类可见输出默认简体中文（L2 按需） |

一句话版：**不要通读整个仓库。** `START_HERE` 只做导航；执行/恢复/接管时先加载 `AGENTS.md` L0，随后由 `NAMESPACE.md` 给出 zero-prompt 下一跳、由 `READING_MAP.md` 判断当前层 `NEXT | SKIP | STOP_*` 并 targeted expansion。普通执行者通常只需要 L0 + 自己的精确任务 + 项目本地上下文。

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