# Agent Interface — Canonical L2 Reference

**Classification: L2 Targeted Reference.** Only read when dispatching, executing, or reviewing Agent work orders.

本文编纂 Human 与 Agent 之间的固定接口契约。所有 ai-hub 映射以本文为准；ai-hub 只做自身映射，不重复全文。

---

## 1. Dispatch Structure

每次 Agent 派发由两层组成：

1. **Durable Dispatch Comment** — Architect 在 Work Order 发布的 `ARCHITECT_*_DISPATCH` 评论，携带角色/启动元数据。scope/base/owns/forbidden/acceptance 已在 Work Order 中，dispatch comment 不重复。
2. **Human Dispatch Card** + **Minimal Agent Seed** — Human Card 给用户决策；Seed 给 Agent 寻址。

### 1.1 Durable Dispatch Comment

每次 Agent-facing 执行派发**必须**有一个 `ARCHITECT_*_DISPATCH` comment，位于 Human seed 之前。

```text
ARCHITECT_EXECUTOR_DISPATCH
---
work_coordinate: `<owner/repo>#<issue>@<step>`
parent_coordinate: `<parent_owner/repo>#<issue>@<step>`
source_global_dispatch: `<owner/repo>#<issue>` comment `<id>`
source_architect_plan: `<owner/repo>#<issue>` comment `<id>`
role: `<Builder | Verifier | Research | Repair | Release>`
Builder: `<identity>`
startup_mode: `<Fresh Builder | Warm Resume | Fresh Verifier | ...>`
access: `github-private | github-public`
```

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

Default Minimal Agent Seed **恰好三行**，只负责寻址：

```text
按 `youling/<repo>#<issue>` 的 <DISPATCH_TYPE> comment `<id>` 执行。

work: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
```

### 3.1 Seed 允许的最小扩展

只有当 pointer 无法无歧义启动时，才补最少的精确引用（如 access hint、exact ref）。Seed **不得**复制以下内容：

- scope / acceptance / requirements / reporting / stop；
- 难度、词元/时间估计、模型建议等人类调度信息；
- 依赖关系、native relationships；
- Builder 自评、旧 findings、Architect 既往裁决或其他 counted Verifier 输出。

若 fresh Agent 仅凭 exact dispatch pointer 无法从 durable source 取得这些事实，说明 Work Order/dispatch 不完整：先修 durable source，再派发。

### 3.2 访问路由

`access: github-private | github-public` 描述控制面入口路由，不承载任务合同。优先 authenticated 读取 `github-private` pointer；live repository metadata 与 access hint 冲突时以 live metadata 为准并报告 drift。

## 4. Human Completion Card

Agent 完成后，Builder/Research/Repair/Verifier 保持详细的持久报告。Human Completion Card **恰好五个语义**：

| # | 字段 | 内容 |
|---|------|------|
| 1 | 结果 | 完成情况 |
| 2 | 交付 | 交付物（PR / commit / document） |
| 3 | 验证 | 验证方法与结果 |
| 4 | 剩余风险 | 已知风险 / 未覆盖区域 |
| 5 | 下一步 | 建议的后续动作 |

## 5. Versioned Definitions

- Human Dispatch Card 五字段顺序：任务 → 为什么做 → 你要做什么 → 调度建议 → 本轮终点。
- Minimal Agent Seed 三行：pointer → work → startup_mode。
- Human Completion Card 五语义：结果 → 交付 → 验证 → 剩余风险 → 下一步。
- Dispatch Comment 携带 task knowledge；Human seed 只携带 addresses。

## 6. Boundary Conditions

- 本文只定义公开/通用方法论。不包含 ai-hub 私有状态/拓扑/heads/endpoints/secrets。
- 本文不改变 Runner/程序行为。
- `ARCHITECT_*_DISPATCH` comment 在 Human seed 之前；seed 不替代 dispatch comment。
- 派发前 Architect 必须确认 durable source 足以让 fresh Agent 执行（见 Work Order 完整性要求）。
