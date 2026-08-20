# Reading Map

**DO NOT READ EVERYTHING.**

本仓是治理/方法论文档库，文档会持续增长。默认冷启动成本必须与当前任务规模相关，
**不随 ai-use 文档总量线性增长**。先按你的角色/场景查这张表，再决定读哪几篇。

---

## 阅读层级

- **L0 Constitution Runtime** —— 极少量、稳定、跨角色的执行原则；默认 Agent 启动只读这一层。
- **L1 Role / Task Context** —— 当前角色、当前 Work Order、项目本地 README/AGENTS/contract 等直接上下文。
- **L2 Targeted Reference** —— 仅在场景触发后按需读取。
- **L3 Rationale / Case / Archive** —— 理念、案例、历史；默认不进入 Agent 上下文。

---

## 角色 / 场景阅读表

| 角色/场景 | 默认读取 (L0) | 按需读取 (L1/L2) | 默认不读 |
| --- | --- | --- | --- |
| **Generic Executor** | `AGENTS.md` | 当前项目本地规则、精确 Work Order、当前 owns 范围；启动时按需读 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（L2） | 完整 Constitution、Session Lifecycle、其他项目、治理 rationale |
| **Project Architect** | `AGENTS.md` | 本项目 Bootstrap、项目 README/architecture index、active Issues/PRs；治理冲突/重大裁决时读 `CONSTITUTION.md`；恢复/交接时读 `docs/SESSION_LIFECYCLE.md`；派发/完成时读 `docs/AGENT_INTERFACE.md`（L2）；启动状态验证时读 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（L2）；仅明确依赖时读跨仓 contract | 其他项目代码、全量 ai-use |
| **Global Architect** | `AGENTS.md` | `CONSTITUTION.md`、`READING_MAP.md`、`NAMESPACE.md`、当前 governance canonical issue、targeted 项目摘要 | 为普通项目决策扫描所有项目代码 |
| **Builder** | `AGENTS.md` | 精确任务、项目本地规则、owns 代码；派发/完成时按需读 `docs/AGENT_INTERFACE.md`（L2）；启动状态验证时读 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（L2） | 完整 Constitution、Session Lifecycle、治理 rationale |
| **Verifier** | `AGENTS.md` | 原始要求、exact-head diff/code/tests、任务引用的 verification contract；派发/完成时按需读 `docs/AGENT_INTERFACE.md`（L2） | Builder 自评、无关文档 |
| **Release** | `AGENTS.md` | exact release dispatch、当前 PR/merge/cleanup 事实 | 为 cleanup 重建整个项目历史 |
| **Incident** | `AGENTS.md` | 扩大到相应 L2 reference（见下） | —— |

---

## 场景触发（L2）

| 场景 | 读什么 |
| --- | --- |
| session / handoff / recovery | `docs/SESSION_LIFECYCLE.md` |
| dispatch / completion / interface contract | `docs/AGENT_INTERFACE.md` |
| 启动状态验证 | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| durable trace / 事实留痕 | `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md` |
| 命名空间导航 / 冷启动入口 | `NAMESPACE.md` |
| 人类可见输出语言 | `00_KERNEL/LANGUAGE_POLICY.md` |
| verification | 任务引用的 verification contract |
| incident | 相关 L2 reference；**只有事故才扩大验证范围** |
| release | release dispatch + 当前 PR/merge/cleanup 事实 |
| architecture conflict / 跨项目 | `CONSTITUTION.md` + 明确依赖的跨仓 contract |
| security / 权限边界 | 相关安全 reference |

---

## 默认规则

> 新的 ai-use 文档默认属于 **L2/L3**，除非本 READING_MAP 明确将其提升为 **L0/L1**。

这样，未来 ai-use 每新增一篇文档，不会自动加重所有 Agent 的 Bootstrap。
需要提升层级时，由 Global Architect 在本文件显式声明。
