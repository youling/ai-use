# Bootstrap Check Protocol

**Classification: L2 Targeted Reference.** 仅在启动 / 派发 / 恢复场景触发时读取。

## 启动模型（固化）

启动采用统一的 **Bootstrap Ordered Applicability Model**：

```text
1 ADDRESS
  A Seed / Natural-Language Addressing + Access Route
  B Durable Dispatch (when applicable)
  C Work Coordinate / Role-Bootstrap Coordinate

2 APPLICABLE RULES
  A Global L0
  B Target Repo / Project Local
  C Current Work / Latest Ruling (when applicable)

3 EXECUTION GATE
  A Authority + Access
  B Live State
  C Bootstrap Conclusion + Durable Writeback

=> EXECUTION_ALLOWED
```

必须严格按 `1 -> 2 -> 3` 执行。任一关键 gate 无法通过时，立即 `EXECUTION_NOT_ALLOWED`；不得跳过或倒序补读后继续施工。

Seed / natural-language addressing 只负责寻址，不承载完整任务知识；Durable Dispatch / Work Order 承载任务上下文；Bootstrap Check 负责确认启动链已按顺序建立并且当前状态允许执行。

`START_HERE.md` 只是 public navigation。除 `BOOT-1` 纯寻址外，**准备执行/接管角色的 Agent 第一份 normative rules read 必须是 `BOOT-2A` current `AGENTS.md` Global L0**；不得先把 `READING_MAP.md`、`NAMESPACE.md`、README、target repo 或 open Issue 的内容作为规范性规则适用。

---

## 1. ADDRESS — 定位

### BOOT-1A Seed / Natural-Language Addressing + Access Route

解析最小启动地址：dispatch pointer、`work`、`startup_mode`、必要的 `access` / exact ref；或对 Fresh/takeover Architect，解析 Human 当前消息已经无歧义明确的 target project/repository、Architect role、governance handbook pointer 与 access route。

**最小 Seed 的目标是“最少无歧义启动信息”，不是机械追求最少行。** 对标准 delegated executor，private repository 的 `access: github-private` 属于 bootstrap-critical addressing metadata，必须显式携带；public repository 在 pointer / live metadata 已无歧义时可省略 access。

Fresh/takeover Architect 不要求 Human 为了模板仪式重复一份 Minimal Seed。若 Human natural-language message 已明确必要寻址事实，Agent MAY 规范化这些事实进入 BOOT-1A；但只允许提取 Human 明确表达的内容：

- target project / repository；
- Architect role；
- governance handbook / rules pointer；
- access route / private-public hint；
- Human 明确给出的 exact pointer（若有）。

不得从 README、open Issue、repo owner、GitHub/MCP capability、provider memory 或模型记忆自行补造：

- authority；
- Durable Dispatch；
- Work Coordinate / active work；
- scope / acceptance；
- priority。

`NATURAL_LANGUAGE_SEED_NORMALIZATION != AUTHORITY_INFERENCE`。

`access` 只决定首次 durable/live read 的访问路由，不产生 authority。路由选择在本槽位完成：

1. **平台原生 GitHub 能力优先**：若当前 Agent / 宿主提供已授权 GitHub connector、integration 或 native GitHub tool，并能读取目标 repo，则优先用它完成首次 GitHub durable/live read。
2. **本机已认证 `gh` 回退**：原生 GitHub 能力不存在、未连接或实测不可用时，才回退到本机已认证 GitHub CLI / API 路径（`gh`）。
3. **本地 Git workspace 最后进入**：local clone / worktree 只是执行副本，不是首次 SSOT 发现入口；使用其 branch/head/文件作为执行依据前，必须先与 remote exact ref / live metadata 校验。
4. 对 `github-private`，**禁止先用匿名公网 URL / raw HTTPS 探路**；匿名 `404` 不构成 repo 不存在或无权限的 durable 证据。只有已知 `github-public` 时，公开 HTTPS 才可作为后续读取回退。
5. native GitHub 与 authenticated `gh` 都不可用时，报告 `ACCESS_BLOCKED` / `ACCESS_DRIFT`；不得靠匿名公网 404、陈旧 checkout 或猜测继续。

明确标记为 **non-retryable** 的 tool error 不得用相同 route + 相同 request shape 原样机械重试。只有存在事实理由，且合法改变 access route / request shape 后，才可再次尝试；不要为此建立第二套错误状态机。

这里只做寻址与访问路径解析，不把 Seed 扩展成任务合同，也不把 access capability 当成治理 authority。

### BOOT-1B Durable Dispatch

标准 delegated execution 使用 BOOT-1A 已选定的 GitHub route 定位当前有效的 `ARCHITECT_*_DISPATCH` / resume dispatch，确认 pointer 可解析，并判断其 current / superseded / historical 状态。

Fresh/takeover Architect 的 **role cold-start** 若 Human 没有提供 Durable Dispatch，不得挑一个 open Issue 冒充 Dispatch。此时可明确记录：

```text
BOOT-1B NO_DISPATCH_SUPPLIED
addressing_mode: ROLE_BOOTSTRAP
```

这只表示“当前是角色冷启动，不是 delegated task dispatch”；它**不产生 authority，也不自动选择 active work**。能否继续仍必须在 `BOOT-3A` 由独立 durable authority evidence 判定。普通 Builder/Research/Repair/Verifier 等 delegated executor 不因本例外而免除 required Dispatch。

**在 `BOOT-2A` 之前，1B 只能确认地址与 currentness。不得把 Dispatch 正文中的 scope、acceptance、language、behavior 指令作为已适用规则执行。**

### BOOT-1C Work Coordinate / Role-Bootstrap Coordinate

有 explicit work 时，确认 owner/repo、issue、step、role 等 coordinate 无歧义；处理 exact-step、latest-wins、superseded 等当前寻址语义。

Fresh/takeover Architect role cold-start 没有 explicit Work Coordinate 时，只记录最小 `ROLE_BOOTSTRAP` coordinate（target repo + role + governance/access pointer）；**不得把“最新 open Issue”“最高优先级标签”或 README 中的路线自动升级为 current Work Coordinate**。

**在 `BOOT-2A` 之前，1C 同样只做 coordinate / authority-pointer 解析，不提前适用任务正文。**

本阶段只回答：**“我在哪、用哪条可信 GitHub 路径读 durable state、当前是 delegated work 还是 role-bootstrap、Human 明确给了哪些地址。”**

---

## 2. APPLICABLE RULES — 适用规则

### BOOT-2A Global L0

加载当前 machine-facing Global L0：`youling/ai-use/AGENTS.md`。

这是执行前置不变量，也是进入 normative rule application 后的**第一份规则读取**。未确认当前 L0 已加载，`BOOT-2A` 不得 PASS。

目标仓 / 项目本地规则和当前 Work Order 可以细化任务，但不得反向覆盖 Human / Global durable ruling / L0 已编译的强制不变量。

### BOOT-2B Target Repo / Project Local

读取目标仓 / 项目本地的必要规则，例如 repo-local `AGENTS.md`、README、直接相关 contract。

该槽位适用于业务项目、control plane、governance、Release 等不同角色；**不要求任务必须存在独立业务 Project**。

`READING_MAP.md` 只在 L0 已加载后用于 targeted expansion；`NAMESPACE.md / README.md` 仅按场景读取，不是普通 Agent 的通用执行前置。

### BOOT-2C Current Work / Latest Ruling

现在才对当前 Work Order、Durable Dispatch、latest amendment / ruling 做**规范性适用**，确定：

- Active Mission；
- owns / scope；
- forbidden；
- acceptance；
- stop condition；
- 当前任务特有的行为要求。

对于没有 explicit work 的 Fresh/takeover Architect role-bootstrap，本槽位必须如实记录“current work 尚未由 addressing/dispatch 给出”，再由 durable project/control-plane state 识别**候选 active graph / blocker / READY work**；这些候选不自动变成 authority、acceptance 或 architecture direction。

本阶段只回答：**“当前适用的上位规则、目标仓/项目本地规则和本案任务分别是什么；若没有本案任务，哪些只是 live project state 而不是被派发的 work。”**

---

## 3. EXECUTION GATE — 开工门

### BOOT-3A Authority + Access

确认：

- 当前 identity / role 无歧义；
- 当前角色拥有本轮所需 authority；
- dispatch author / authority pointer 合法（任务契约要求时）；
- role-bootstrap 没有 Durable Dispatch 时，存在**独立的 durable authority evidence** 足以证明当前 Architect role/scope；Human 明确说“你是该项目架构师”可作为当前 Human direction，但 GitHub/MCP capability、repo owner、open Issue 本身不得替代 authority 判断；
- BOOT-1A 选择的 `github-private` / `github-public` 访问路径与 live metadata 一致且实测可用；
- 原生 GitHub / `gh` / filesystem capability 不被误当成 Authority。

BOOT-1A 决定“先走哪条访问路径”；BOOT-3A 决定“该访问能力是否真的可用，以及当前角色是否有权执行”。两者不得混为一谈。

### BOOT-3B Live State

live-read 当前执行状态，至少覆盖与角色/任务相关的：

- lifecycle / current status；
- dependencies / native relationships；
- exact head / branch / target ref；
- current active graph / READY candidates / blockers（Architect role-bootstrap 时）；
- currentness / superseded state；
- HEAD_MOVED / relationship drift / authority conflict 等阻断条件。

与 Seed、自述、provider memory、旧报告或本地 checkout 冲突时，以 current GitHub durable/live state 为准并 fail closed。

**Provider-side memory = cache only.** 不鼓励长期保存易漂移的 authority snapshot、active graph 或 current head；即使存在跨会话 memory，也必须在本槽位 live-revalidate。

### BOOT-3C Bootstrap Conclusion + Durable Writeback

只有 `BOOT-1A -> BOOT-3B` 全部通过，才可形成最终 Bootstrap 结论。

对 Fresh/takeover Architect，**durable writeback 是声称 cold-start complete / `EXECUTION_ALLOWED` 的完成 gate**：必须先把 `ARCHITECT_BOOTSTRAP_REPORT` / Bootstrap Check Report 写回 current 可写 durable authority/bootstrap anchor/dispatch source，然后才能对外声明 durable bootstrap complete。

报告至少应让 fresh successor 恢复：

```text
ARCHITECT_BOOTSTRAP_REPORT
---
addressing_mode: MINIMAL_SEED | NATURAL_LANGUAGE | ROLE_BOOTSTRAP
role: <architect role>
target: <repo/project>
authority_evidence: <durable pointer / current Human direction as applicable>
access_route: <validated route>
live_head: <exact current ref if relevant>
current_graph: <concise active/ready/blocker facts, not architecture direction>
execution_gate: EXECUTION_ALLOWED | EXECUTION_NOT_ALLOWED
architect_readiness: ARCHITECT_READY | ARCHITECT_NOT_READY | NOT_APPLICABLE
durable_writeback: <pointer>
next_classification: CONTINUE_WITHIN_AUTHORITY | STOP_NO_READY_WORK | STOP_COLD_START_ONLY | HUMAN_PRIORITY_REQUIRED | <exact blocker/gate>
```

若检查本身通过，但当前**没有可写 durable target**，只能报告：

```text
BOOTSTRAP_VALID_SESSION_LOCAL
DURABLE_WRITEBACK = UNAVAILABLE
EXECUTION_ALLOWED = NOT_DURABLY_ESTABLISHED
```

不得仅在聊天中写“冷启动完成”，也不得把 provider memory 当 durable writeback。

普通任务的推荐最小 durable 表示仍可为：

```text
BOOT-1A PASS
BOOT-1B PASS
BOOT-1C PASS
BOOT-2A PASS
BOOT-2B PASS
BOOT-2C PASS
BOOT-3A PASS
BOOT-3B PASS
BOOT-3C PASS

EXECUTION_ALLOWED
```

任一项失败时，例如：

```text
BOOT-1A ACCESS_BLOCKED
BOOT-3C BLOCKED

EXECUTION_NOT_ALLOWED
```

不得靠猜、补一句自评或绕过 gate 继续施工。

### Architect cold-start 后的 continuation 分类

Fresh/takeover Architect 完成 durable Bootstrap 后，必须把“接下来干什么”归入真实状态，而不是默认列选项等待 Human 再说一句：

- **唯一 current authorized READY work** -> `CONTINUE_WITHIN_AUTHORITY`，按现行 continuation rule 继续；
- Human 明确指定 **cold-start-only stop condition** -> `STOP_COLD_START_ONLY`；
- **no READY work** -> `STOP_NO_READY_WORK`；
- 存在多个**互斥** READY work 且 durable priority 无法裁决 -> `HUMAN_PRIORITY_REQUIRED`；
- 其它 Human / authority / security / high-risk / blocker gate -> 精确报告对应 gate。

不得为了“主动”虚构 READY work，也不得用泛化的“你要我继续哪个？”代替上述分类。

### `EXECUTION_ALLOWED` 与 `ARCHITECT_READY`

两层必须保持：

- `BOOT-1/2/3 -> EXECUTION_ALLOWED` 只证明 current role/task 的 authority、access、规则与 live state 足以开始执行；
- Fresh/takeover Architect 在 material architecture / Work Graph / BUILD-vs-REUSE / major direction 前，仍须按 `docs/ARCHITECT_RECONNAISSANCE.md` 完成 `ARCH-0`（或 live-revalidate 可复用报告）后进入 `ARCHITECT_READY`。

Bootstrap report MAY 列 current active graph / blockers，但不得仅凭 repo/history 把旧路线包装成 current architecture direction。

---

## 与旧七项检查的对应

旧检查没有消失，只被收敛到稳定顺序：

- Identity / Authority / Access -> `BOOT-1A` 路由选择 + `BOOT-3A` capability/authority 核验
- Entry Point -> `BOOT-1A/1B/1C`
- Active Mission / Boundary -> `BOOT-2C`
- State -> `BOOT-3B`
- Global L0 loaded -> 新增为明确的 `BOOT-2A` 执行前置证明

## 可回写要求

Bootstrap Check Report 必须回写到 current 可写 durable source 才能作为 Fresh/takeover Architect durable cold-start completion evidence。仅存在于聊天中的“我已确认”、provider memory/cache 或不可恢复 session note 都不算数。

若当前没有可写 durable target，必须明确降级为 `BOOTSTRAP_VALID_SESSION_LOCAL`，不得声称 durable `EXECUTION_ALLOWED` 已建立。

Bootstrap report 的人类可读叙述遵守 `AGENTS.md` L0 language invariant：默认简体中文；code / path / SHA / machine identifier / protocol constant 保留原文。
