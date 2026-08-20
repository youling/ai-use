# Bootstrap Check Protocol

**Classification: L2 Targeted Reference.** 仅在启动/派发/恢复场景触发时读取。

**Protocol Version: 1.0.0**

## 启动模型（固化）

启动由三层分工，各司其职，**不要把完整任务知识塞入 Seed**：

| 层 | 职责 |
| --- | --- |
| **Seed** | 只负责**定位 durable source**（寻址），不承载任务知识。规范格式见 `docs/AGENT_INTERFACE.md` §3。 |
| **Durable Dispatch** | 负责**任务上下文**（角色、scope、acceptance 等），见 `docs/AGENT_INTERFACE.md` §1。 |
| **Bootstrap Check** | 负责**启动状态验证**（本文件）：执行前确认身份/入口/权限/访问/任务/边界/状态已就绪。 |

Seed 不复制 Dispatch/Work Order 的任务知识；Dispatch 不替代 Bootstrap Check 的状态验证；
Bootstrap Check 不承载完整任务上下文。

## 用途边界

Bootstrap Check 的用途是**验证初始化状态**。它**不是**：

- 补充上下文（上下文加载见 `docs/PROGRESSIVE_CONTEXT_BOOT.md`）；
- 恢复聊天历史（聊天不是 durable source）；
- 重新解释架构（架构说明见 `CONSTITUTION.md` / 项目 README）。

## 固定检查项

执行前按序确认以下 7 项：

1. **Identity** —— 当前身份（node / agent_type / session）已知且无歧义。
2. **Entry Point** —— 已定位 durable source 入口（pointer / ref），且能无歧义启动。
3. **Authority** —— 当前角色在范围内拥有对应权限，不越权。
4. **Access** —— 所需访问路径（github-private / github-public）与 live metadata 一致。
5. **Active Mission** —— 已确认当前精确任务（Work Order）及其当前状态。
6. **Boundary** —— 已确认 owns / forbidden / acceptance 边界。
7. **State** —— 已核对 durable / live state，与 seed 冲突时以 durable source 为准。

## Bootstrap Check Report Schema v1.0.0

Bootstrap Check 的输出必须是**机器可解析结构 + 人类可读说明**。

### 协议常量

```text
BOOTSTRAP_CHECK_REPORT
version: 1.0.0
```

### 固定结构（机器区）

字段名与顺序**稳定固定**，Agent 不得自由增删、改名或重排核心字段。

```yaml
BOOTSTRAP_CHECK_REPORT
version: 1.0.0
result: PASS | BLOCKED
identity:
  role: <role>
entry:
  durable_source: <pointer>
authority:
  source: <authority source>
access:
  status: <ok | drift | unknown>
mission:
  current: <current mission / work coordinate>
rules_loaded:
  - <loaded rule reference>
boundary:
  owns: <owns>
  forbidden: <forbidden>
state:
  status: <consistent | conflict | unknown>
blockers:
  - <blocker description | none>
```

### 字段说明（说明区，人类可读）

| 字段 | 含义 | 取值 |
| --- | --- | --- |
| `result` | 整体启动验证结果 | `PASS` / `BLOCKED` |
| `identity.role` | 当前身份角色 | 角色名 |
| `entry.durable_source` | 定位到的 durable source 入口 pointer | exact ref / issue pointer |
| `authority.source` | 当前 authority 来源 | 权威源引用 |
| `access.status` | 访问路径与 live metadata 一致性 | `ok` / `drift` / `unknown` |
| `mission.current` | 当前精确任务 / work coordinate | `owner/repo#issue@step` |
| `rules_loaded` | 已加载的规则引用列表 | 文档路径列表 |
| `boundary.owns` / `boundary.forbidden` | 职责边界 | 描述 |
| `state.status` | durable / live state 一致性 | `consistent` / `conflict` / `unknown` |
| `blockers` | 阻塞项 | 列表；无阻塞时为 `none` |

说明区允许在机器结构下方追加中文说明，但**不得改变核心字段**的名称、顺序或取值语义。

### 语言边界

- **机器区**：允许英文 key 与取值（如 `result:` / `identity:` / `authority:` / `PASS` / `BLOCKED`）。
- **说明区**：默认简体中文。
- **禁止**：协议英文导致全文英文化；人类可读说明一律中文，机器 key 保留英文。

## 可回写要求

**Bootstrap Check Report 必须可回写 durable source**（当前 authority issue / dispatch comment）。
仅存在于聊天中的"我已确认"不算数；未回写 durable source 时，按未验证处理。

## 输出

Bootstrap Check 结果按本 schema 输出，与 `ARCHITECT_*_DISPATCH` / Work Order 对齐后，可回写为确认评论；
状态冲突或无法确认某项时报告 `BLOCKED`，不靠猜继续。
