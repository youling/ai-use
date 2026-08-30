# ai-use Namespace

本文件定义 ai-use 的 **zero-prompt navigation chain**：让陌生 Human / Agent 在没有额外提示词的情况下，知道当前层处理完以后应该往哪里走。

它定义的是**自主路由顺序**，不是“每次 cold-start 必须把 00→90 全部通读”的 full-read order。

> 准备执行、恢复或接管角色时，`BOOT-1` 可以先做纯寻址；进入 normative rules 后，`00_KERNEL` 的必经入口是 current governance repo 根目录的 `AGENTS.md`（机器 L0）。L0 加载后，Agent MUST 能依据本链 + `READING_MAP.md` 自主决定下一跳，不需要 Human 再提示“接下来读什么”。

---

## Zero-prompt routing chain

```text
00_KERNEL
   ↓
10_BOOT
   ↓
20_ROLES
   ↓
30_PROTOCOLS
   ↓
40_GUIDES
   ↓
50_TEMPLATES
   ↓
90_HISTORY
```

这是一条**可短路、可跳过的链**。进入每一层时只允许产生以下 routing result：

- `NEXT` —— 当前层有被角色/场景触发的必要内容；targeted 读取后继续下一层。
- `SKIP` —— 当前层没有适用内容；不读该层正文，直接进入下一层。
- `STOP_READY` —— 当前任务所需规则/上下文已经充分，且 Bootstrap / authority / live-state gate 已通过；退出文档链进入执行。
- `STOP_BLOCKED` —— 存在真实 authority / access / currentness / Human / security / dependency blocker；停止并报告精确 gate。

**不得因为链存在就顺序通读所有目录。** `NEXT` 只读取 `READING_MAP.md` 当前角色/场景命中的 targeted 文档；未命中就 `SKIP`。

**不得仅因为没有新的 Human prompt 就停止。** 若只是不知道下一份该读什么，应继续按本链自主路由。

---

## 各层的默认路由语义

| 层 | 默认职责 | zero-prompt 判定 |
| --- | --- | --- |
| `00_KERNEL` | 稳定规则与核心治理不变量 | **必经入口**：先读根目录 `AGENTS.md` L0；其它 Kernel 文档仅按 `READING_MAP` 触发 |
| `10_BOOT` | Ordered Bootstrap / workspace 初始化 | 启动、恢复、接管、workspace 初始化时 `NEXT`；否则可 `SKIP` |
| `20_ROLES` | 角色划分与职责边界 | 当前 role / authority boundary 已无歧义则 `SKIP`；否则 targeted `NEXT` |
| `30_PROTOCOLS` | Dispatch、durable trace、session/recovery 等协作协议 | 当前任务触发哪个协议就只读哪个；无触发则 `SKIP` |
| `40_GUIDES` | 场景指南 / regression / detailed human-facing guidance | 只有对应场景或验证需要时 `NEXT`；普通执行通常 `SKIP` |
| `50_TEMPLATES` | 可复用输出/启动/报告模板 | 只有需要生成对应 artifact/card/report 时 `NEXT`；否则 `SKIP` |
| `90_HISTORY` | 历史、案例、rationale | 默认 `SKIP`；只有明确需要 historical rationale / Incident deep-dive 时 `NEXT` |

在任意层，只要已经满足 current task 的最小充分上下文且 execution gate 已通过，可 `STOP_READY`，**不要求为了走完整条链而继续读后面的层**。

---

## 各层职责与映射

| 层 | 职责 | 对应文档 |
| --- | --- | --- |
| `00_KERNEL` | 稳定规则与核心解释 | [`AGENTS.md`](AGENTS.md)（机器 L0）、[`CONSTITUTION.md`](CONSTITUTION.md)、`00_KERNEL/LANGUAGE_POLICY.md` |
| `10_BOOT` | Ordered Bootstrap / workspace 初始化 | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`、`10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`、[`docs/PROGRESSIVE_CONTEXT_BOOT.md`](docs/PROGRESSIVE_CONTEXT_BOOT.md) |
| `20_ROLES` | 角色划分与职责边界 | [`CONSTITUTION.md`](CONSTITUTION.md) §2、[`README.md`](README.md) Governance model |
| `30_PROTOCOLS` | 固定接口契约与原则 | [`docs/AGENT_INTERFACE.md`](docs/AGENT_INTERFACE.md)、`30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`、[`docs/SESSION_LIFECYCLE.md`](docs/SESSION_LIFECYCLE.md) |
| `40_GUIDES` | 场景验证 / 人类可见表达指南 | `00_KERNEL/LANGUAGE_POLICY.md`、`40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md` |
| `50_TEMPLATES` | 可复用启动/报告/交互模板 | `50_TEMPLATES/`；Workspace 初始化见 `HUMAN_WORKSPACE_BOOTSTRAP.md` |
| `90_HISTORY` | 历史、案例、rationale | 默认不进入 Agent 上下文 |

---

## 使用规则

- 第一次不知道仓库是什么：`START_HERE.md` 负责 public navigation。
- 准备执行/恢复/接管：`00_KERNEL` 先加载 current governance repo 根目录 `AGENTS.md` L0。
- L0 后无需等待新提示词；按本文件的 00→90 链推进，并用 `READING_MAP.md` 判断每层 `NEXT | SKIP | STOP_*`。
- `BOOT-1 -> BOOT-2 -> BOOT-3` 仍是 execution applicability/gate 顺序；Namespace 链负责“下一份上下文往哪找”，两者不是竞争协议。
- 链式导航不改变 authority，不允许把目录顺序、repo 名称或文档存在本身推导成任务 scope / acceptance / priority。
- 禁止为了“完整”通读整个仓库。

## 兼容性

- Namespace 继续保持 `00 -> 10 -> 20 -> 30 -> 40 -> 50 -> 90` 的链式启动设计；本轮只澄清它是 **zero-prompt routing order，而非 mandatory full-read order**。
- 不移动、不重命名已有文件，不破坏相对路径。
- `docs/` 下文档继续保留；本表只做路由与映射，不制造第二份内容副本。
- 新增文档仍由 `READING_MAP.md` 的 L0/L1/L2/L3 规则决定是否在某一跳被触发。
