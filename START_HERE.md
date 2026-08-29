# START HERE

陌生 Human 或 Agent 第一次进入 `ai-use` 时的启动文档。

---

## 1. ai-use 是什么

ai-use 是一套围绕 **Human governance + 专职 AI Agent + Git/GitHub durable state** 的人机协作方法论：

- 定义 Human / Global Architect / Project Architect / Builder / Verifier 的职责分层；
- 定义 Agent 的启动、派发、完成、留痕协议；
- 以 Git/GitHub 为唯一持久事实源，聊天只作 working memory。

它不是运行时、不是数据库、不是 Router。它是规则与协议。

### ai-use 的位置

**ai-use = governance layer template（治理层模板），不是你的项目 workspace。**

clone ai-use ≠ 你的系统已经就绪。它像操作系统镜像：clone 后还需要按本文件初始化你的仓库（governance / control plane / asset）与 workspace。

### Global Architect 的角色

**Global Architect is an AI coordination role, not an organizational authority over human decisions.**

Global Architect 是 AI 协调角色：维护规则、调度 Agent、收敛治理；它不对人类决策拥有组织级权威。Human 拥有最终主权。

## 2. 第一阅读入口

`START_HERE.md` 是 **public navigation**，不是执行型 Agent 的 normative rules layer。

准备执行任务、恢复任务或接管 Architect 角色时：

1. **第一份 normative rules read 必须是 [`AGENTS.md`](AGENTS.md)（Global L0）**；
2. L0 加载后，再用 [`READING_MAP.md`](READING_MAP.md) 判断当前角色/场景需要哪些 targeted L1/L2；
3. [`NAMESPACE.md`](NAMESPACE.md) 只用于命名空间导航，[`README.md`](README.md) 只用于体系概览；二者都不是普通 Agent 获得 `EXECUTION_ALLOWED` 的前置。

`BOOT-1 ADDRESS` 的自然语言寻址可以发生在 L0 前，但此时只允许提取地址事实；不得提前适用 target repo / current work 的 scope、acceptance、priority、authority 或 behavior。完整顺序见 [`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`](10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md)。

## 3. Agent 如何启动

Agent 可以由 **Minimal Agent Seed** 或 Human 已经明确表达的 **natural-language addressing** 启动；Human 不需要为了模板仪式再次复制同一组寻址事实。

标准 delegated executor 的最小 seed 仍只寻址，不复制任务知识：

```text
按 `youling/<repo>#<issue>` 的 <DISPATCH_TYPE> comment `<id>` 执行。

work: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
```

对 Fresh / takeover Architect，如果 Human 当前消息已经无歧义明确了 target project/repository、Architect role、governance handbook pointer 与 access route，例如：

```text
你是 <repo> 的项目架构师；工作手册是 <ai-use>；private GitHub 使用已授权 connector/MCP。
```

Agent MAY 把这些**明确表达的事实**规范化为 `BOOT-1A` addressing facts。不得从 README、open Issue、repo owner、GitHub/MCP capability 或模型记忆自行补造 Durable Dispatch、Work Coordinate、authority、acceptance 或 priority。

`NATURAL_LANGUAGE_SEED_NORMALIZATION != AUTHORITY_INFERENCE`。

任务型 Agent 的统一 cold-start 主干是：

```text
1 ADDRESS
  BOOT-1A Seed / natural-language addressing + Access Route
  BOOT-1B current Durable Dispatch（若适用）
  BOOT-1C Work Coordinate / role-bootstrap coordinate

2 APPLICABLE RULES
  BOOT-2A Global L0 (`AGENTS.md`)
  BOOT-2B target repo / project local
  BOOT-2C current Work Order / latest ruling（若适用）

3 EXECUTION GATE
  BOOT-3A Authority + Access
  BOOT-3B Live State
  BOOT-3C Bootstrap Conclusion + required durable writeback

=> EXECUTION_ALLOWED
```

`BOOT-1` 只定位，不提前适用任务正文；任务 scope / acceptance / behavior 的规范性适用发生在 `BOOT-2C`。只有 `1 -> 2 -> 3` 全部通过，且 Fresh/takeover Architect 的 required Bootstrap Report 已写回可写 durable anchor，才可声称 durable cold-start complete / `EXECUTION_ALLOWED`。

完整定义见 [`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`](10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md)；Human / Agent 接口见 [`docs/AGENT_INTERFACE.md`](docs/AGENT_INTERFACE.md)。

## 4. 如何初始化自己的 workspace

新组织 / 新用户第一次搭建时，按 [`10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`](10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md) 初始化。
推荐仓库结构与完整流程见下文（Recommended Workspace Layout / First Time Setup）。

人类侧清单见 [`50_TEMPLATES/HUMAN_WORKSPACE_BOOTSTRAP.md`](50_TEMPLATES/HUMAN_WORKSPACE_BOOTSTRAP.md)。

> 不要假设仓库名称。仓库角色通过 role registration 确定，与具体名称无关。

---

## Recommended Workspace Layout

一个标准 AI 工作空间建议包含以下仓库。名称不是强制要求，但建议保持推荐命名。

### 1. Governance Repository

职责：存放

- Constitution
- Agent Interface
- Protocol
- Templates

推荐命名：`ai-use`

说明：名称不是强制要求，但建议保持。

### 2. Control Plane Repository

职责：存放

- Issue lifecycle
- Task state
- Dispatch
- Agent coordination

推荐命名：`ai-hub`

说明：名称不是强制要求。

### 3. Asset Repository

职责：资产事实源，存放

- hardware assets
- software assets
- ownership
- lifecycle evidence

推荐命名：`assets`

说明：不要使用个人语言命名作为公共接口。

---

## First Time Setup

流程：

1. 创建 governance repo
2. 引入 ai-use
3. 创建 control plane repo
4. 创建 asset repo
5. 注册 workspace
6. 启动 Global Architect

## Naming Principle

规则：

- **公共基础设施**：优先英文。
  原因：跨语言、Agent 易理解、开源复用。
- **个人内部**：可以使用任意语言。

例如：

- 推荐：`ai-use` / `ai-hub` / `assets`
- 不强制：`my-ai-rule` / `company-assets`

## 缺失环境处理

如果缺少 `control plane repo` 或 `asset repo`，Agent **不应该创建假设**。

应该输出：

```text
WORKSPACE_NOT_READY
WAITING_FOR_HUMAN
```

并请求 Human 提供缺失仓库。

## Agent 首次启动说明

如果 Agent 第一次进入 ai-use：

1. 用 `START_HERE` 只做 public navigation / address discovery；
2. 第一份 normative rules read 加载 `AGENTS.md` L0；
3. L0 后再按 `READING_MAP.md` targeted expansion；
4. 执行 Bootstrap Check（`BOOT-1 -> BOOT-2 -> BOOT-3`）；
5. 只有 workspace 初始化场景才进入 Workspace Bootstrap。

`NAMESPACE.md / README.md` 不是普通任务 cold-start 的强制前置。不要扫描全部历史。

## Agent Handoff 流程

总架构师交接（含跨节点 / 跨设备）按序执行：

1. Capability Self Check —— `50_TEMPLATES/capability_self_check.md`
2. Handoff Request —— `50_TEMPLATES/architect_handoff_transaction.md`（`ARCHITECT_HANDOFF_REQUEST`）
3. Handoff Check —— `50_TEMPLATES/architect_handoff_check.md`
4. Handoff Accepted —— `50_TEMPLATES/architect_handoff_transaction.md`（`ARCHITECT_HANDOFF_ACCEPTED`）
5. Bootstrap Check —— `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`
6. Resume Work

交接只转移 AI 工作角色调度权，不转移所有权，不赋予 GitHub owner / 人类组织 / 商业决策权限（Capability != Authority）。

## Common Agent Operations

常用操作的入口（陌生 Human / Agent 无需询问作者）：

| 操作 | 指向 |
| --- | --- |
| 初始化检查 | Bootstrap Check Template（`50_TEMPLATES/bootstrap_check_request.md`） |
| 能力盘点 | Capability Self Check Template（`50_TEMPLATES/capability_self_check.md`） |
| 分配任务 | Human Dispatch Template（`docs/AGENT_INTERFACE.md` §2 Human Dispatch Card） |
| 完成回报 | Completion Report Template（`docs/AGENT_INTERFACE.md` §4 Human Completion Card） |
| 状态对齐 | Alignment Template（`CONSTITUTION.md` §1 Human sovereignty） |
| 架构师交接验收 | Architect Handoff Check Template（`50_TEMPLATES/architect_handoff_check.md`） |

## 验证入口

冷启动冒烟测试清单：`40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md`
