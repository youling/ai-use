# Bootstrap Check Protocol

**Classification: L2 Targeted Reference.** 仅在启动 / 派发 / 恢复场景触发时读取。

**Protocol Version: 1.1.0**

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

Seed / natural-language addressing 只负责寻址，不承载完整任务知识；Durable Dispatch / Work Order 承载任务上下文；Bootstrap Check 负责确认启动链已按顺序建立并且 current state 允许执行。

`START_HERE.md` 只是 public navigation。除 `BOOT-1` 纯寻址外，**准备执行/恢复/接管角色的 Agent 第一份 normative rules read 必须是 current governance repo 根目录的 `AGENTS.md` Global L0**。公共 ai-use 不把这个坐标写死到上游维护者 owner/repo，也不要求外部 fork/clone 返回上游读取 L0。

---

## 1. ADDRESS — 定位

### BOOT-1A Seed / Natural-Language Addressing + Access Route

解析最小启动地址：dispatch pointer、`work`、`startup_mode`、必要的 `access` / exact ref；或对 Fresh/takeover Architect，解析 Human 当前消息已经无歧义明确的 target project/repository、Architect role、governance handbook pointer 与 access route。

**最小 Seed 的目标是“最少无歧义启动信息”，不是机械追求最少行。** 标准 delegated executor 使用 generic `<owner>/<repo>#<issue>@<step>` coordinate。private repository 的 `access: github-private` 属于 bootstrap-critical addressing metadata，必须显式携带；public repository 在 pointer / live metadata 已无歧义时可省略 access。

Fresh/takeover Architect 不要求 Human 为模板仪式重复一份 Minimal Seed。Human natural-language message 已明确必要寻址事实时，Agent MAY 规范化：

- target project / repository；
- Architect role；
- current governance handbook / rules pointer；
- access route / private-public hint；
- Human 明确给出的 exact pointer（若有）。

不得从 README、open Issue、repo owner、GitHub/MCP capability、provider memory 或模型记忆自行补造：

- authority；
- Durable Dispatch；
- Work Coordinate / active work；
- scope / acceptance；
- priority。

`NATURAL_LANGUAGE_SEED_NORMALIZATION != AUTHORITY_INFERENCE`。

`access` 只决定首次 durable/live read 的访问路由，不产生 authority。路由选择固定为：

1. **平台原生已授权 GitHub capability 优先**：connector / integration / native GitHub tool 能 authenticated 读取目标 repo 时，先用它。
2. **authenticated `gh` 回退**：原生能力不存在、未连接或实测不可用时，才回退本机已认证 GitHub CLI / API。
3. **local Git workspace 最后进入**：clone/worktree 只是执行副本；使用 branch/head/文件事实前，先与 remote exact ref / live metadata 校验。
4. `github-private` **禁止先用匿名公网 URL / raw HTTPS 探路**；匿名 `404` 不构成 repo 不存在或无权限的 durable 证据。
5. native GitHub 与 authenticated `gh` 都不可用时，报告 `ACCESS_BLOCKED` / `ACCESS_DRIFT`，不得靠陈旧 checkout 或猜测继续。

明确标记为 non-retryable 的 tool error 不得用相同 route + 相同 request shape 原样机械重试；只有有事实理由且合法改变 route/request shape 后才可再次尝试。

### BOOT-1B Durable Dispatch

标准 delegated execution 使用 BOOT-1A 已选定 route 定位 current `ARCHITECT_*_DISPATCH` / resume dispatch，确认 exact pointer 可解析，并判断 current / superseded / historical 状态。

Fresh/takeover Architect 的 **role cold-start** 若 Human 没有提供 Durable Dispatch，不得挑一个 open Issue 冒充 Dispatch：

```text
BOOT-1B NO_DISPATCH_SUPPLIED
addressing_mode: ROLE_BOOTSTRAP
```

这不产生 authority，也不自动选择 active work。普通 Builder / Research / Repair / Verifier 不因本例外免除 required Dispatch。

在 `BOOT-2A` 之前，1B 只能确认地址与 currentness；不得提前适用 Dispatch 正文的 scope / acceptance / language / behavior。

### BOOT-1C Work Coordinate / Role-Bootstrap Coordinate

有 explicit work 时，确认 `<owner>/<repo>#<issue>@<step>`、role 等 coordinate 无歧义，并处理 exact-step / latest-wins / superseded。

Fresh/takeover Architect role cold-start 没有 explicit Work Coordinate 时，只记录最小 `ROLE_BOOTSTRAP` coordinate（target repo + role + governance/access pointer）；不得把“最新 open Issue”“最高优先级标签”或 README 路线自动升级为 current Work Coordinate。

若当前场景需要寻找 deployment-local control plane，优先从 current governance repo 的 `workspace_registry.control_plane.repo`（或等价 deployment role registration）解析；**不得通过示例仓库名、物理 sibling 路径、repo owner 或上游维护者账号猜真实 control-plane 地址。**

---

## 2. APPLICABLE RULES — 适用规则

### BOOT-2A Global L0

加载**当前 governance repo 根目录的 `AGENTS.md`**。

这是进入 normative rule application 后的第一份规则读取。未确认 current L0 已加载，`BOOT-2A` 不得 PASS。

对于直接使用上游 public ai-use 的场景，current governance repo 可以就是该 public repo；对于 fork/clone/自建兼容 governance repo，L0 必须来自**该部署当前注册的 governance repo**，不是固定返回某个上游 owner/repo。

目标仓/项目本地规则和 current Work Order 可以细化任务，但不得反向覆盖 Human / Global durable ruling / L0 强制不变量。

### BOOT-2B Target Repo / Project Local

读取目标仓/项目本地必要规则，例如 repo-local `AGENTS.md`、README、直接相关 contract。

`READING_MAP.md` 只在 L0 已加载后用于 targeted expansion；`NAMESPACE.md / README.md` 仅按场景读取，不是普通 Agent 的通用执行前置。

### BOOT-2C Current Work / Latest Ruling

现在才对 current Work Order、Durable Dispatch、latest amendment / ruling 做规范性适用，确定：

- Active Mission；
- owns / scope；
- forbidden；
- acceptance；
- stop condition；
- 当前任务特有行为要求。

没有 explicit work 的 Fresh/takeover Architect role-bootstrap 必须如实记录“current work 尚未由 addressing/dispatch 给出”，再从**当前 target project/program 的 targeted durable state**识别候选 active graph / blocker / READY work；不得为恢复角色默认扫描整个 workspace 的全部 open work，也不得把候选状态自动升级成 authority、acceptance 或 architecture direction。

---

## 3. EXECUTION GATE — 开工门

### BOOT-3A Authority + Access

确认：

- current identity / role 无歧义；
- current role 拥有本轮所需 authority；
- dispatch author / authority pointer 合法（任务契约要求时）；
- role-bootstrap 无 Durable Dispatch 时，存在独立 durable authority evidence；Human 当前明确任命可作为 current direction，但 repo owner / GitHub login / connector capability / open Issue 本身不能替代 authority；
- BOOT-1A 的 access route 与 live metadata 一致且实测可用；
- capability 不被误当成 Authority。

`Capability != Authority`。

### BOOT-3B Live State

live-read 与当前角色/任务**直接相关**的：

- lifecycle / current status；
- dependencies / native relationships；
- exact head / branch / target ref；
- target project/program 的 current active graph / READY candidates / blockers（Architect role-bootstrap 时）；
- currentness / superseded state；
- `HEAD_MOVED` / relationship drift / authority conflict 等阻断条件。

与 Seed、自述、provider memory、旧报告或 local checkout 冲突时，以 current GitHub durable/live state 为准并 fail closed。

**Provider-side memory = cache only.** authority snapshot、active graph、current head / lifecycle 使用前必须 live-revalidate。

### BOOT-3C Bootstrap Conclusion + Durable Writeback

只有 `BOOT-1A -> BOOT-3B` 全部通过，才可形成最终 Bootstrap 结论。

对 Fresh/takeover Architect，**durable writeback 是声称 cold-start complete / `EXECUTION_ALLOWED` 的完成 gate**：必须先把 `ARCHITECT_BOOTSTRAP_REPORT` / Bootstrap Check Report 写回 current 可写 durable authority/bootstrap anchor/dispatch source。

推荐报告：

```text
ARCHITECT_BOOTSTRAP_REPORT
---
addressing_mode: MINIMAL_SEED | NATURAL_LANGUAGE | ROLE_BOOTSTRAP
role: <architect role>
target: <repo/project>
governance_repo: <current governance owner/repo>
control_plane_repo: <workspace_registry.control_plane.repo | explicit durable pointer | none>
authority_evidence: <durable pointer / current Human direction as applicable>
access_route: <validated route>
live_head: <exact current ref if relevant>
current_graph: <targeted active/ready/blocker facts, not architecture direction>
execution_gate: EXECUTION_ALLOWED | EXECUTION_NOT_ALLOWED
architect_readiness: ARCHITECT_READY | ARCHITECT_NOT_READY | NOT_APPLICABLE
durable_writeback: <pointer>
next_classification: CONTINUE_WITHIN_AUTHORITY | STOP_NO_READY_WORK | STOP_COLD_START_ONLY | HUMAN_PRIORITY_REQUIRED | <exact blocker/gate>
```

若检查本身通过，但当前没有可写 durable target，只能报告：

```text
BOOTSTRAP_VALID_SESSION_LOCAL
DURABLE_WRITEBACK = UNAVAILABLE
EXECUTION_ALLOWED = NOT_DURABLY_ESTABLISHED
```

不得仅在聊天中宣称“冷启动完成”，也不得把 provider memory 当 durable writeback。

普通 delegated task 可使用更短的 PASS block；任一关键项失败时必须 `EXECUTION_NOT_ALLOWED`。

### Architect cold-start 后的 continuation 分类

Fresh/takeover Architect 完成 durable Bootstrap 后必须按真实状态分类：

- 唯一 current authorized READY work -> `CONTINUE_WITHIN_AUTHORITY`；
- Human 明确 cold-start-only -> `STOP_COLD_START_ONLY`；
- no READY work -> `STOP_NO_READY_WORK`；
- 多个互斥 READY 且 durable priority 不足 -> `HUMAN_PRIORITY_REQUIRED`；
- 其它 Human / authority / security / high-risk / blocker gate -> 精确报告对应 gate。

**没有额外 Human prompt 本身不构成 blocker。** 不得用“先给用户确认再接任/再继续”作为 Fresh/takeover Architect 的通用 stop，也不得为了主动而虚构 READY work。

### `EXECUTION_ALLOWED` 与 `ARCHITECT_READY`

两层必须保持：

- `BOOT-1/2/3 -> EXECUTION_ALLOWED` 只证明 current role/task 的 authority、access、规则与 live state 足以开始执行；
- Fresh/takeover Architect 在 material architecture / Work Graph / BUILD-vs-REUSE / major direction 前，仍须按 `docs/ARCHITECT_RECONNAISSANCE.md` 完成 `ARCH-0`（或 live-revalidate 可复用报告）后进入 `ARCHITECT_READY`。

Bootstrap report MAY 列 current active graph / blockers，但不得仅凭 repo/history 把旧路线包装成 current architecture direction。

---

## Portability invariants

陌生外部使用者 cold-start 必须满足：

1. 不要求访问上游维护者的 private repo / account。
2. 不把 maintainer-specific owner/repo、示例 control-plane 名称或示例物理路径当成 fixed coordinate。
3. governance L0 从 current governance repo 解析；control-plane 从 `workspace_registry.control_plane.repo` 或等价 deployment registration 解析。
4. private repo 首次 durable read 使用 authenticated route；匿名 404 不是权限/存在性证据。
5. missing optional `asset` / `project` role 不阻塞最小 workspace；只有必需 role 或真实 authority/access/currentness 缺口才 fail closed。
6. `NAMESPACE.md` 定义 L0 后的 zero-prompt next-hop routing chain；它不是 mandatory full-read order，也不产生 authority / scope / acceptance / priority。
7. Human-facing narrative 默认简体中文；英文 template/header 不构成 language override。
