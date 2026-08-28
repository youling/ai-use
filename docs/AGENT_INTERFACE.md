# Agent Interface — Canonical L2 Reference

**Classification: L2 Targeted Reference.** Only read when dispatching, executing, or reviewing Agent work orders.

**Protocol Version: 2.0.3**

本文编纂 Human 与 Agent 之间的固定接口契约。所有 ai-hub 映射以本文为准；ai-hub 只做自身映射，不重复全文。

---

## 1. Dispatch Structure

每次 Agent 派发由两层组成：

1. **Durable Dispatch Comment** — Architect 在 Work Order 发布的 `ARCHITECT_*_DISPATCH` 评论，携带角色/启动元数据。scope/base/owns/forbidden/acceptance 已在 Work Order 中，dispatch comment 不重复。
2. **Human Dispatch Card** + **Minimal Agent Seed** — Human Card 给用户决策；Seed 给 Agent 寻址。

### 1.1 Durable Dispatch Comment

每次 Agent-facing 执行派发**必须**有一个 `ARCHITECT_*_DISPATCH` comment，位于 Human seed 之前。Durable dispatch 携带 task knowledge；Human seed 只寻址。

Dispatch comment 的字段由 Architect 按任务需要填写，不强制统一字段集。以下为常见字段参考（非必须全集）：

```text
ARCHITECT_EXECUTOR_DISPATCH
---
work_coordinate: `<owner/repo>#<issue>@<step>`
role: `<Builder | Verifier | Research | Repair | Release>`
startup_mode: `<Fresh Builder | Warm Resume | Fresh Verifier | ...>`
access: `github-private | github-public`
```

Durable Work Order + dispatch layer 携带任务知识；Human seed 只负责寻址。派发前 Architect 必须确认 durable source 足以让 fresh Agent 执行。

### 1.2 Agent 启动适用顺序

Seed 只提供地址；Agent 执行时必须按 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` 的统一主干完成：

`BOOT-1 ADDRESS -> BOOT-2 APPLICABLE RULES -> BOOT-3 EXECUTION GATE -> EXECUTION_ALLOWED`。

其中：

- `BOOT-1A` 解析 Seed 与 access route；`github-private` 优先当前 Agent / 宿主的已授权原生 GitHub capability，实测不可用时回退 authenticated `gh`；禁止先以匿名公网 URL / raw HTTPS 试探 private repo；
- `BOOT-1B/1C` 在 `BOOT-2A` 前只解析 dispatch / coordinate 的地址与 currentness，**不得提前适用任务正文**；
- `BOOT-2A` 必须先加载 Global L0 `AGENTS.md`；
- `BOOT-2B` 再加载 target repo / project local context；
- `BOOT-2C` 才规范性适用 current Work Order / Dispatch / latest ruling；
- 任一关键 gate 未通过时不得进入 execution。

本节只提供接口 pointer，不复制完整 Bootstrap 协议。

## 2. Human Dispatch Card

Human Dispatch Card **恰好五个字段**，按以下顺序：

| # | 字段 | 内容 |
|---|------|------|
| 1 | 任务 | 一句话任务标题 |
| 2 | 为什么做 | 背景 / 理由 |
| 3 | 你要做什么 | 本轮工作内容 |
| 4 | 调度建议 | 只给 Human：难度、上下文规模、模型建议、词元/时间粗估、并行策略、本轮重点 |
| 5 | 本轮终点 | 完成边界 / stop condition |

调度建议**只属于 Human 调度层**，不进入 Agent seed。Human Card 是用户决策提示，不是 Agent 指令或状态源。

### 示例

```text
任务: ai-hub#50 / routing + docs 收敛
为什么做: #40/#46/#47/ai-use#4 已退场，文档仍残留旧 Gate / 双验证 / 全量 Bootstrap 语义
你要做什么: ACTIVE_PROJECTS routing、registry 补齐、Bootstrap/协议对齐 ai-use 2.0、验证政策收敛
调度建议: 难度 2/5；上下文 Medium；文档编辑 + targeted GitHub 核验；可单 Builder 完成
本轮终点: 提交 PR，报告 exact head + 验证结果后停止，等 Architect Review
```

## 3. Default Minimal Agent Seed

Minimal Agent Seed 的目标是**最少无歧义启动信息**，不是固定追求最少行。

### 3.1 Public / access 已无歧义

当目标 repo 为 public，或 exact pointer 已足以无歧义解析访问路由时，默认 Seed 保持三行：

```text
按 `youling/<repo>#<issue>` 的 <DISPATCH_TYPE> comment `<id>` 执行。

work: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
```

### 3.2 Private GitHub canonical seed

private repo 的首次 durable read 依赖 authenticated route，因此 `access: github-private` 是 bootstrap-critical addressing metadata，**必须包含**：

```text
按 `youling/ai-hub#123` 的 `ARCHITECT_BUILD_DISPATCH` comment `456789` 执行。

work: youling/ai-hub#123@step
startup_mode: Fresh Builder
access: github-private
```

这不是把任务合同塞回 Seed；`access` 只告诉 BOOT-1A 目标访问类别。

### 3.3 Seed 允许的最小扩展

只有当 pointer 无法无歧义启动时，才补最少的 bootstrap-critical 精确引用（如 private/public access hint、exact ref）。Seed **不得**复制以下内容：

- role（当 `startup_mode` 已无歧义表达角色时）、scope / acceptance / requirements / reporting / stop；
- 启动读取顺序、输入依据/evidence 列表、当前目标、执行步骤、禁止事项或验证清单；
- 难度、词元/时间估计、模型建议等人类调度信息；
- 依赖关系、native relationships；
- Builder 自评、旧 findings、Architect 既往裁决或其他 counted Verifier 输出。

若 fresh Agent 仅凭 exact dispatch pointer + 必要 access metadata 无法从 durable source 取得这些事实，说明 Work Order/dispatch 不完整：先修 durable source，再派发。

### 3.4 访问路由

`access: github-private | github-public` 描述 BOOT-1A 的控制面入口路由，不承载任务合同，也不授予 authority。

访问优先级固定为：

1. **当前 Agent / 宿主的已授权原生 GitHub capability**：例如平台内建 GitHub connector / integration / native GitHub tool；若它能 authenticated 读取目标 repo，优先使用。
2. **本机已认证 `gh`**：原生 capability 不存在、未连接或实测失败时回退。
3. **本地 Git workspace**：只作为执行副本；在使用 branch/head/文件事实前必须与 remote exact ref / live metadata 校验，不是首次 SSOT 发现入口。
4. 对 `github-public`，必要时可再回退公开 HTTPS；对 `github-private`，禁止把匿名公网 URL/raw HTTPS 作为首次探路手段。

private repo 的匿名 `404` 不构成 repo 不存在或无权限的 durable 证据。native GitHub 与 authenticated `gh` 都不可用时，报告 `ACCESS_BLOCKED` / `ACCESS_DRIFT`，不得靠陈旧 local clone 或猜测继续。

Capability != Authority：能读 private repo 不代表能施工、Review、merge 或 deploy；authority 在 BOOT-3A 独立验证。

## 4. Human Completion Card

Agent 完成后，Builder/Research/Repair/Verifier 保持详细的持久报告。Human Completion Card **恰好五个语义**：

| # | 字段 | 内容 |
|---|------|------|
| 1 | 结果 | 完成情况 |
| 2 | 交付 | 交付物 + 精确可恢复指针（PR / commit / exact head / durable report pointer） |
| 3 | 验证 | 验证方法与结果 |
| 4 | 剩余风险 | 已知风险 / 未覆盖区域 |
| 5 | 下一步 | 建议的后续动作 |

## 5. Versioned Definitions

- `2.0.3`：把 Minimal Seed 从“最少行”收敛为“最少无歧义启动信息”；private repo 固定携带 `access: github-private`；BOOT-1A 统一访问顺序为平台原生 GitHub capability → authenticated `gh` → 经 remote 校验后的 local Git workspace，private repo 禁止匿名公网 404 探路。
- `2.0.2`：同步 Bootstrap Ordered Applicability；不改变 Seed 字段，只增加 `BOOT-1 -> BOOT-2 -> BOOT-3` 的启动顺序 pointer，并明确 BOOT-1 不提前适用任务正文。
- `2.0.1`：clarification patch；不增加新的任务知识字段，只强化 Minimal Agent Seed 的唯一职责是 bootstrap addressing，并给出 private GitHub 的最小 `access` 扩展示例。
- Human Dispatch Card 五字段顺序：任务 → 为什么做 → 你要做什么 → 调度建议 → 本轮终点。
- Minimal Agent Seed：public / access 已无歧义时三行；private repo canonical 四行（pointer → work → startup_mode → `access: github-private`）。
- Human Completion Card 五语义：结果 → 交付 → 验证 → 剩余风险 → 下一步。
- Dispatch Comment 携带 task knowledge；Human seed 只携带 addresses / bootstrap-critical access metadata。

## 6. Boundary Conditions

- 本文只定义公开/通用方法论。不包含 ai-hub 私有状态/拓扑/heads/endpoints/secrets。
- 本文不改变 Runner/程序行为。
- `ARCHITECT_*_DISPATCH` comment 在 Human seed 之前；seed 不替代 dispatch comment。
- 派发前 Architect 必须确认 durable source 足以让 fresh Agent 执行（见 Work Order 完整性要求）。
- 人类可见叙述的语言遵守 `AGENTS.md` L0 invariant；英文任务/模板本身不构成 language override。
