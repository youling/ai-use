# ai-use Namespace

本文件是 ai-use 文档仓库的**命名空间导航**。它帮助 Human / Agent 理解文档按什么职责分层、需要时往哪里找；**它不定义执行型 Agent 的 cold-start 顺序，也不是 Fresh Agent 的第一规则入口。**

> 执行、恢复或接管角色时，`START_HERE.md` 只做 public navigation；进入 normative rules 后第一份必须读取 current `AGENTS.md`（机器 L0），随后才按 `READING_MAP.md` targeted expansion。完整 Ordered Bootstrap 见 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`。

---

## 命名空间分层（不是执行顺序）

```text
00_KERNEL    稳定规则 / 核心解释
10_BOOT      启动与 workspace 协议
20_ROLES     角色边界
30_PROTOCOLS 协作协议 / durable trace / session
40_GUIDES    场景指南 / regression
50_TEMPLATES 可复用模板
90_HISTORY   历史 / rationale
```

上述编号只用于**文档分类与定位**。不得把 `00 -> 10 -> ... -> 90` 解释成“每次冷启动都要依次读取这些目录”。

## 各层职责与映射

| 层 | 职责 | 对应文档 |
| --- | --- | --- |
| `00_KERNEL` | 稳定权威与接口解释 | [`AGENTS.md`](AGENTS.md)（机器 L0）、[`CONSTITUTION.md`](CONSTITUTION.md)、`00_KERNEL/LANGUAGE_POLICY.md` |
| `10_BOOT` | Ordered Bootstrap / workspace 初始化 | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`、`10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`、[`docs/PROGRESSIVE_CONTEXT_BOOT.md`](docs/PROGRESSIVE_CONTEXT_BOOT.md) |
| `20_ROLES` | 角色划分与职责边界 | 角色分层见 [`CONSTITUTION.md`](CONSTITUTION.md) §2、[`README.md`](README.md) Governance model |
| `30_PROTOCOLS` | 固定接口契约与原则 | [`docs/AGENT_INTERFACE.md`](docs/AGENT_INTERFACE.md)、`30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`、[`docs/SESSION_LIFECYCLE.md`](docs/SESSION_LIFECYCLE.md) |
| `40_GUIDES` | 场景验证 / 人类可见表达指南 | `00_KERNEL/LANGUAGE_POLICY.md`（语言政策）、`40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md`（冷启动测试入口） |
| `50_TEMPLATES` | 可复用的启动/报告/交互模板 | `50_TEMPLATES/`；Workspace 初始化见 `HUMAN_WORKSPACE_BOOTSTRAP.md` |
| `90_HISTORY` | 历史、案例、rationale | 默认不进入 Agent 上下文 |

## 使用规则

- 第一次不知道仓库是什么：读 `START_HERE.md` 做 public navigation。
- 准备执行/恢复/接管：第一份 normative rules read = `AGENTS.md`。
- L0 加载后，需要知道当前场景还应读什么：查 `READING_MAP.md`。
- 只有为了定位文档类别时才需要本 Namespace；普通 task cold-start 不要求读取本文件。
- 低层默认不读 L2/L3；禁止为了“完整”按目录顺序通读整个仓库。

## 兼容性

- 本命名空间只做逻辑分类，不移动、不重命名已有文件，不破坏相对路径。
- `docs/` 下文档继续保留；本表只做映射，不制造第二份内容副本。
- 新增文档默认仍按 `READING_MAP.md` 的 L0/L1/L2/L3 规则决定是否进入当前上下文。
