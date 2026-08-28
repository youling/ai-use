# Reading Map

**DO NOT READ EVERYTHING.**

本仓是治理/方法论文档库，文档会持续增长。默认冷启动成本必须与当前任务规模相关，
**不随 ai-use 文档总量线性增长**。先按你的角色/场景查这张表，再决定读哪几篇。

---

## 阅读层级

- **L0 Constitution Runtime** —— 极少量、稳定、跨角色的执行原则；默认 Agent 启动必须加载这一层。
- **L1 Role / Task Context** —— 当前角色、当前 Work Order、目标仓/项目本地 README/AGENTS/contract 等直接上下文。
- **L2 Targeted Reference** —— 仅在场景触发后按需读取。
- **L3 Rationale / Case / Archive** —— 理念、案例、历史；默认不进入 Agent 上下文。

启动时的适用顺序不是“按需任选”：必须按 `BOOT-1 -> BOOT-2 -> BOOT-3`，其中 `BOOT-2A` 先加载 `AGENTS.md` Global L0，再进入 `BOOT-2B` 目标仓/项目本地规则和 `BOOT-2C` 当前任务。完整顺序见 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`。

`00_KERNEL/LANGUAGE_POLICY.md` 仍是 L2 解释与示例；其关键行为已经编译进 `AGENTS.md` L0。**L2 不要求每个 Agent 额外读取，不等于其 L0 invariant 可不遵守。**

---

## 角色 / 场景阅读表

| 角色/场景 | 默认读取 (L0) | 按需读取 (L1/L2) | 默认不读 |
| --- | --- | --- | --- |
| **Generic Executor** | `AGENTS.md` | 当前目标仓/项目本地规则、精确 Work Order、当前 owns 范围；启动时按需读 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（L2） | 完整 Constitution、Session Lifecycle、其他项目、治理 rationale |
| **Project Architect** | `AGENTS.md` | 本项目 Bootstrap、项目 README/architecture index、active Issues/PRs；Fresh/takeover 或 material new-domain/architecture pivot 时读 `docs/ARCHITECT_RECONNAISSANCE.md`（L2）；GitHub identity-sensitive review/merge/privileged mutation 或多 principal access 模式下，读项目本地 GitHub execution identity/access mapping（若提供，约定可位于 `docs/GITHUB_EXECUTION_IDENTITIES.md`）；治理冲突/重大裁决时读 `CONSTITUTION.md`；恢复/交接时读 `docs/SESSION_LIFECYCLE.md`；派发/完成时读 `docs/AGENT_INTERFACE.md`（L2）；启动状态验证时读 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（L2）；仅明确依赖时读跨仓 contract | 其他项目代码、全量 ai-use |
| **Global Architect** | `AGENTS.md` | `CONSTITUTION.md`、`READING_MAP.md`、`NAMESPACE.md`、当前 governance canonical issue、targeted 项目摘要；Fresh/takeover 或 material new-domain/architecture pivot 时读 `docs/ARCHITECT_RECONNAISSANCE.md`（L2）；GitHub identity-sensitive review/merge/privileged mutation 或 authority-registry identity 对齐时，读目标项目本地 GitHub execution identity/access mapping；新组织初始化 / workspace 发现时读 `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`（L2） | 为普通项目决策扫描所有项目代码 |
| **Builder** | `AGENTS.md` | 精确任务、目标仓/项目本地规则、owns 代码；派发/完成时按需读 `docs/AGENT_INTERFACE.md`（L2）；启动状态验证时读 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（L2） | 完整 Constitution、Session Lifecycle、治理 rationale |
| **Verifier** | `AGENTS.md` | 原始要求、exact-head diff/code/tests、任务引用的 verification contract；派发/完成时按需读 `docs/AGENT_INTERFACE.md`（L2） | Builder 自评、无关文档 |
| **Release** | `AGENTS.md` | exact release dispatch、当前 PR/merge/cleanup 事实 | 为 cleanup 重建整个项目历史 |
| **Incident** | `AGENTS.md` | 扩大到相应 L2 reference（见下） | —— |

---

## 场景触发（L2）

| 场景 | 读什么 |
| --- | --- |
| 公共入口 / 首次进入 | `START_HERE.md` |
| workspace 初始化 / 角色发现 | `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md` + `50_TEMPLATES/HUMAN_WORKSPACE_BOOTSTRAP.md` |
| 冷启动冒烟测试准备 | `40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md` |
| Fresh/takeover Architect 实质架构启动；material new-domain / major capability / major pivot | `docs/ARCHITECT_RECONNAISSANCE.md`；在 Bootstrap `EXECUTION_ALLOWED` 后完成 `ARCH-0` 或 live-revalidate 可复用报告，进入 `ARCHITECT_READY` 后再 materialize 第一轮架构 |
| 普通 Architect Hot Resume / 小 bug / 确定性维护 | 不因角色为 Architect 自动重复 `ARCH-0`；仅当 external ecosystem 变化可能改变当前方案时 targeted 刷新 |
| Architect GitHub identity-sensitive review / merge / privileged mutation；项目存在多个 GitHub principal/channel | 读取**项目本地** GitHub execution identity/access mapping，并 live-read 当前 authenticated principal；公共 ai-use 不定义任何项目私有账号名。不得推断 repo owner = authenticated principal、GitHub principal = governance role、repository permission = governance authority |
| session / handoff / recovery | `docs/SESSION_LIFECYCLE.md` |
| dispatch / completion / interface contract | `docs/AGENT_INTERFACE.md` |
| 启动状态验证 | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| durable trace / 事实留痕 | `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md` |
| 命名空间导航 / 冷启动入口 | `NAMESPACE.md` |
| 人类可见输出语言（详细解释/例子） | `00_KERNEL/LANGUAGE_POLICY.md`；关键 MUST 已在 `AGENTS.md` L0 |
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
