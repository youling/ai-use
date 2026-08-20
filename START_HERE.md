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

按顺序读（不要通读全仓）：

1. [`READING_MAP.md`](READING_MAP.md) —— 决定"按当前角色/场景该读哪几篇"；
2. [`NAMESPACE.md`](NAMESPACE.md) —— 理解 00→90 命名空间流向；
3. [`AGENTS.md`](AGENTS.md) —— 机器 L0 规则，执行 Agent 默认只读这一层；
4. [`README.md`](README.md) —— 体系概览与治理模型。

## 3. Agent 如何启动

Agent 通过**最小 seed**（只寻址）启动，不复制任务知识：

```text
按 `youling/<repo>#<issue>` 的 <DISPATCH_TYPE> comment `<id>` 执行。

work: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
```

启动路径：Seed 寻址 → Kernel（`AGENTS.md`）→ Boot Protocol（`10_BOOT/`）→ Bootstrap Check（`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`）→ 执行。

详见 [`docs/AGENT_INTERFACE.md`](docs/AGENT_INTERFACE.md) 与 [`50_TEMPLATES/`](50_TEMPLATES/)。

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

如果 Agent 第一次进入 ai-use，执行：

1. START_HERE
2. Kernel
3. Bootstrap Check
4. Workspace Bootstrap

不要：扫描全部历史。

## Common Agent Operations

常用操作的入口（陌生 Human / Agent 无需询问作者）：

| 操作 | 指向 |
| --- | --- |
| 初始化检查 | Bootstrap Check Template（`50_TEMPLATES/bootstrap_check_request.md`） |
| 分配任务 | Human Dispatch Template（`docs/AGENT_INTERFACE.md` §2 Human Dispatch Card） |
| 完成回报 | Completion Report Template（`docs/AGENT_INTERFACE.md` §4 Human Completion Card） |
| 状态对齐 | Alignment Template（`CONSTITUTION.md` §1 Human sovereignty） |

## 验证入口

冷启动冒烟测试清单：`40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md`
