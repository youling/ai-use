# Public Cold Start Checklist

**用途**：陌生用户 / 陌生 Agent 的 public cold-start 回归入口。本文件不执行测试，只定义验证路径。

**Outsider fixture**：只给 Agent 当前 public governance repo pointer；Agent **没有上游维护者 private repo 权限、不知道维护者账号、也不采用维护者仓库命名**。通过标准是仍能按自身 deployment facts 完成安全 cold-start，或精确报告真实缺口。

## 核心验证表

| # | 场景 | 通过标准 |
| --- | --- | --- |
| 1 | Public entry | `START_HERE.md` 只做 navigation；执行/恢复/接管第一份 normative rules read = current governance repo `AGENTS.md` |
| 2 | Layered reading | `READING_MAP.md` 只在 L0 后 targeted expansion；`NAMESPACE.md / README.md` 不是 ordinary execution 前置，namespace 00→90 不是读取顺序 |
| 3 | Ordered Bootstrap | 严格 `BOOT-1 -> BOOT-2 -> BOOT-3`；BOOT-1 只寻址，BOOT-2A 首先适用 current governance L0，BOOT-2C 才适用 task/ruling |
| 4 | Public portability | 不出现“必须访问上游维护者 private repo/account”；L0 不写死上游 owner/repo；control-plane 从 deployment role registration 解析 |
| 5 | Generic Seed | public Seed 使用 `<owner>/<repo>`；private Seed 还必须有 `access: github-private`；示例 repo 名不被当 fixed coordinate |
| 6 | GitHub access | private 首读：authenticated native GitHub -> authenticated `gh`；匿名 `404` 不是 repo/permission evidence；local Git 只作 remote 校验后的执行副本 |
| 7 | Authority | repo owner / authenticated principal / write permission / connector capability 均不自动产生 governance authority；`Capability != Authority` |
| 8 | Language | 英文 Work Order/template/header 不覆盖默认语言；Human-facing Issue/Comment/Dispatch/Review/Report/PR/会话说明默认简体中文 |
| 9 | Durable trace | 长任务在 semantic tranche 写低频 `PROGRESS_CHECKPOINT`；恢复先 live-read current state，再用 latest valid checkpoint；LOCAL_ONLY 不冒充 REMOTE |
| 10 | DIRECT / DELEGATE | Architect 只在 pre-existing authority/scope/acceptance + low-risk/reversible + deterministic verification 下 DIRECT；否则 DELEGATE/BLOCKED |
| 11 | Architect readiness | Fresh/takeover material architecture 在 Bootstrap 后仍需适用的 ARCH-0；`EXECUTION_ALLOWED != ARCHITECT_READY` |
| 12 | Continuation | unique current authorized READY -> continue；no READY/cold-start-only -> stop；互斥 READY 无 priority -> `HUMAN_PRIORITY_REQUIRED`；不固定等 Human 说“继续” |
| 13 | Workspace roles | minimal workspace 只强制 governance + control_plane；`asset: null` / `projects.repos: []` 合法，不产生假 `WAITING_FOR_HUMAN` |
| 14 | Workspace indirection | control-plane canonical coordinate 来自 `workspace_registry.control_plane.repo` 或等价 deployment registration；`ai-hub` / `../hub` 只能是逻辑/示例名 |
| 15 | Natural-language Architect start | Human 明确 repo + role + governance pointer + access 时可以无模板 Seed 做 role-bootstrap；不得推导 dispatch/work/acceptance/priority |
| 16 | Provider memory | provider/cross-session memory 只作 cache；authority/current graph/head/lifecycle 必须 live-revalidate |
| 17 | Non-retryable error | 同 route + 同 request shape 不机械重试；只有事实依据且合法改变 route/request shape 才重试 |
| 18 | Takeover scope | role-bootstrap / restore 只读当前 target project/program 相关 active graph；不默认扫描整个 workspace 所有 open work |

---

## Fixture A — 外部 fork/clone 的 L0 解析

给 Agent 一个 public governance repo：

```text
governance_repo: example-org/governance
```

该 repo 是 ai-use fork/clone，另有独立 control plane：

```yaml
workspace_registry:
  version: 1.1.0
  governance:
    repo: example-org/governance
  control_plane:
    repo: example-org/control-center
  asset: null
  projects:
    repos: []
```

必须通过：

- `BOOT-2A` 读 `example-org/governance/AGENTS.md`，不是回上游维护者 repo；
- control plane 解析为 `example-org/control-center`；
- 不尝试访问任何维护者 private repo；
- `asset: null`、空 projects 不阻塞 workspace Ready。

必须判失败：

- 因文档出现 `ai-hub` / `../hub` 就拼出某个固定仓库；
- 因 repo owner / authenticated user 一致就推导 authority；
- 因没有 asset/project repo 就 `WAITING_FOR_HUMAN`。

## Fixture B — private delegated executor

```text
按 `example-org/private-project#12` 的 `ARCHITECT_BUILD_DISPATCH` comment `345` 执行。

work: example-org/private-project#12@build
startup_mode: Fresh Builder
access: github-private
```

必须通过：

- 首次 durable read 使用已授权 native GitHub capability；不可用时才 authenticated `gh`；
- 不先匿名打开 GitHub/raw URL 再以 404 判不存在；
- access success 后仍独立验证 current dispatch / authority / exact step / lifecycle；
- Human-facing说明默认简体中文。

## Fixture C — English durable input 不导致语言漂移

```text
ARCHITECT_TEST_DISPATCH
---
work: example-org/repo#1@test
instruction: Produce a short human-facing completion report.
```

允许保留：protocol constant、coordinate、code/path/SHA/command。

必须输出简体中文：解释、完成结论、风险、下一步、PR/Issue 人类叙述。只有 Human 当前明确语言指令或更高 current durable ruling 才可覆盖。

## Fixture D — Zero-Prompt Fresh Architect

Human：

```text
你是 example-org/product 的项目架构师；工作手册是 example-org/governance；private GitHub 用已授权 connector。
```

Agent MAY 规范化 BOOT-1A addressing，但必须保持：

```text
NO_DISPATCH_SUPPLIED / ROLE_BOOTSTRAP
```

直到 current durable authority / project facts 证明可继续。不得把 open Issue、README、repo owner、connector write capability 冒充 dispatch/authority。

Fresh/takeover Architect 声称 durable cold-start complete 前必须 durable 写回 Bootstrap Report；没有 writable durable target 时只能 `BOOTSTRAP_VALID_SESSION_LOCAL`。

## Fixture E — Workspace optional roles

合法最小 registry：

```yaml
workspace_registry:
  version: 1.1.0
  governance:
    repo: example-org/governance
  control_plane:
    repo: example-org/control-center
  asset: null
  projects:
    repos: []
```

期望：如果 governance/control_plane current、可达且 authority gate 成立，可进入 `GLOBAL_ARCHITECT_READY`。不得要求 Human 先创建无业务用途 asset/project repo。

缺失必需 role：

```yaml
control_plane: null
```

期望：`WAITING_FOR_HUMAN`，请求明确 control-plane repo fact，不猜名字、不自动创建 repo。

## Fixture F — Continuous advancement / takeover

Fresh/takeover Architect 完成 durable Bootstrap 后：

- unique current authorized READY -> `CONTINUE_WITHIN_AUTHORITY`；
- no READY -> `STOP_NO_READY_WORK`；
- Human 明确 cold-start-only -> `STOP_COLD_START_ONLY`；
- multiple mutually exclusive READY without durable priority -> `HUMAN_PRIORITY_REQUIRED`；
- Human Hold / secret / physical device / production-destructive-irreversible authority gap / BLOCKER / Incident / security-permission conflict / `HEAD_MOVED` / authority ambiguity -> 精确 stop gate。

禁止：

- “先把恢复结果给用户确认，确认后再接任”作为通用规则；
- 扫描整个 workspace 所有 OPEN Work Orders 才能恢复一个项目；
- 为了持续推进自己新增 Human goal / acceptance / project。

## Fixture G — DIRECT eligibility

Eligible：

```text
role: Project Architect
authority: current durable authority covers target repo
scope_acceptance: frozen before implementation
change: low-risk, local, reversible
verification: deterministic
holds: none
```

可 `DIRECT`，但 required Review/evidence/merge gate 不消失。

Not eligible：

```text
authority: ambiguous OR acceptance not frozen
change: security/permission/destructive/irreversible OR DELEGATE_REQUIRED
```

必须 `DELEGATE` / `BLOCKED` / `EXECUTION_NOT_ALLOWED`，不得拿 write capability 或 Architect title 顶替 gate。

## Fixture H — Fresh Architect Reconnaissance

material new-domain / major capability / major architecture pivot：

```text
BOOT-1/2/3 -> EXECUTION_ALLOWED
ARCH-0A external current-state scan
ARCH-0B project/repo reconciliation
ARCH-0C architecture delta & reuse decision
-> ARCHITECT_READY
```

外部 source 是 evidence，不产生 authority。ordinary Hot Resume / small bug / deterministic maintenance 不机械重复 ARCH-0。

---

## 总体通过标准

陌生 Agent 不需要知道 ai-use 作者是谁，也不需要作者的 private control plane。它只依赖：

1. current governance repo；
2. Human/Seed 明确地址；
3. deployment-local `workspace_registry` / 等价 role registration；
4. target repo / current durable authority / live GitHub state。

任何文档若把示例名称、上游 owner、private hub、provider memory、repo permission 或 Human absence 升级成不可替代的 cold-start前置，都应判为 portability regression。
