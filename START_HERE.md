# START HERE

陌生 Human 或 Agent 第一次进入 `ai-use` 时的启动文档。

---

## 1. ai-use 是什么

ai-use 是一套围绕 **Human governance + 专职 AI Agent + Git/GitHub durable state** 的人机协作方法论：

- 定义 Human / Global Architect / Project Architect / Builder / Verifier 的职责分层；
- 定义 Agent 的启动、派发、完成、留痕协议；
- 以 Git/GitHub 为唯一持久事实源，聊天只作 working memory。

它不是运行时、不是数据库、不是 Router。它是规则与协议。

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

新组织 / 新用户第一次搭建时，按 [`10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`](10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md) 初始化：

1. 准备 **governance repo**（规则、协议、Agent Interface）；
2. 准备 **control plane repo**（任务、Issue、状态流转）；
3. 准备 **asset repo**（资产事实源）；
4. 注册 workspace（`workspace registry`）；
5. 启动 Global Architect，确认 `GLOBAL_ARCHITECT_READY`。

人类侧清单见 [`50_TEMPLATES/HUMAN_WORKSPACE_BOOTSTRAP.md`](50_TEMPLATES/HUMAN_WORKSPACE_BOOTSTRAP.md)。

> 不要假设仓库名称（如 `youling/ai-use` / `youling/ai-hub`）。仓库角色通过 role registration 确定，与具体名称无关。

## 验证入口

冷启动冒烟测试清单：`40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md`