# ai-use

一套围绕 **Human governance + 专职 AI Agent + Git/GitHub durable state** 形成的人机协作方法论。

版本：2.0.0

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

- **Human** 拥有最终主权：决定目标、优先级、接受风险，以及 merge/deploy 等重大动作。
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
| [`CONSTITUTION.md`](CONSTITUTION.md) | 全角色（尤其 Architect） | 治理冲突、重大裁决、理解体系时；普通任务不必通读 |
| [`READING_MAP.md`](READING_MAP.md) | 全角色（机器/人类导航） | 需要知道"我该读什么"时 |
| [`AGENTS.md`](AGENTS.md) | 所有执行 Agent（机器 L0） | 每个 Agent 启动时默认只读这一层 |
| [`docs/SESSION_LIFECYCLE.md`](docs/SESSION_LIFECYCLE.md) | Architect / 需要恢复或交接的人 | L2 按需参考，仅在 session/handoff/recovery 场景触发 |

一句话版：**不要通读整个仓库。** 先看 `READING_MAP.md` 决定你按当前角色/场景该读哪几篇；普通执行者默认只需要 `AGENTS.md`(机器 L0) + 自己的精确任务 + 项目本地上下文。

---

## ai-use vs ai-hub

| | `ai-use` | `ai-hub` |
| --- | --- | --- |
| 性质 | 公开的方法论 / 治理体系 / 协作模式 | 私有控制台 / runtime |
| 内容 | 原则、角色、模式、案例、rationale、阅读索引 | Runner、项目路由、执行现场、安全核验、少量机器契约 |
| 增长 | 允许长期增长（L2/L3 按需读） | 只承载少量已冻结的机器规则 |

ai-use **不负责**私有项目实时状态、active project topology、Runner runtime、本地 workspace 状态、私有 registry、当前谁在跑什么任务。这些属于 ai-hub 或各项目仓。

本仓不保存具体私有项目的实时拓扑与状态，也不引用任何活跃项目代号。

---

## License

见 [`LICENSE`](LICENSE)。
