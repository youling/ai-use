# ai-use Namespace

本文件是 ai-use 文档仓库的**命名空间入口**。它定义冷启动的阅读顺序，让 Fresh Agent
只需看本表即可理解"该往哪个方向读"，而不必通读整个仓库。

> 本文件只是入口/索引，不是第二套 L0 规则。实际规则仍以 `AGENTS.md`（机器 L0）为准。

---

## 启动流向

```
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

## 各层职责与映射

| 层 | 职责 | 对应文档 |
| --- | --- | --- |
| `00_KERNEL` | 稳定权威与接口入口；机器 L0 与治理原则 | [`AGENTS.md`](AGENTS.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`README.md`](README.md)、[`READING_MAP.md`](READING_MAP.md)、`00_KERNEL/LANGUAGE_POLICY.md` |
| `10_BOOT` | 启动路由：确认下一步要读什么，避免全仓扫描 | `10_BOOT/README.md`、`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`、[`docs/PROGRESSIVE_CONTEXT_BOOT.md`](docs/PROGRESSIVE_CONTEXT_BOOT.md) |
| `20_ROLES` | 角色划分与职责边界 | 角色分层见 [`CONSTITUTION.md`](CONSTITUTION.md) §2、[`README.md`](README.md) Governance model |
| `30_PROTOCOLS` | 固定接口契约与原则 | [`docs/AGENT_INTERFACE.md`](docs/AGENT_INTERFACE.md)、`30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`、[`docs/SESSION_LIFECYCLE.md`](docs/SESSION_LIFECYCLE.md) |
| `40_GUIDES` | 人类可见输出与表达规范 | `00_KERNEL/LANGUAGE_POLICY.md`（语言政策） |
| `50_TEMPLATES` | 可复用的启动 / 报告 / 交互模板 | `50_TEMPLATES/`（Agent Seed、Bootstrap Check、Dispatch Card、Completion、对齐、授权等填空模板）；历史完整协议见 [`docs/SESSION_LIFECYCLE.md`](docs/SESSION_LIFECYCLE.md) §3–§6 |
| `90_HISTORY` | 历史、案例、rationale | 当前为空；默认不进入 Agent 上下文 |

> 注：`20_ROLES` / `40_GUIDES` / `50_TEMPLATES` / `90_HISTORY` 尚无独立文档时，由本表直接
> 指向现有文档对应章节。命名空间是**逻辑分层**，不是必须为每层新建空文件。

## 兼容性

- 本命名空间为**增量入口**，不移动、不重命名任何已有文件，不破坏已有相对路径。
- 现有 `docs/` 下文档继续保留；本入口只做映射，不制造第二份内容副本。
- 低层默认不读 L2/L3；具体该读哪层按 [`READING_MAP.md`](READING_MAP.md) 决定。
