# Public Cold Start Checklist

**用途**: 未来陌生用户冒烟测试的**入口**。本文件不执行测试，只定义验证路径。

**目标**: 仅给陌生用户一个 `ai-use` repo pointer 后，Agent 能否独立完成以下步骤。

## 验证路径

| # | 步骤 | 通过标准 | 证据位置 |
| --- | --- | --- | --- |
| 1 | 找 START_HERE | 通过入口文档定位第一阅读入口 | `START_HERE.md` |
| 2 | 加载 Kernel | 读到 `AGENTS.md`（L0）与 `NAMESPACE.md`；确认 human-visible output 中文 MUST | `AGENTS.md` / `NAMESPACE.md` |
| 3 | 执行 Ordered Bootstrap | 按 `BOOT-1A -> ... -> BOOT-3C` 顺序完成；`BOOT-2A` 先于 target/local 与 current work 的规范性适用；最终只有 PASS 才 `EXECUTION_ALLOWED` | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| 4 | GitHub access routing 回归 | private fixture 必须直接按 `access: github-private` 选择“平台原生 GitHub capability → authenticated `gh`”路径；不得先以匿名公网 URL / raw HTTPS 制造 404；local Git 只作经 remote 校验后的执行副本 | `AGENTS.md` / `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` / `docs/AGENT_INTERFACE.md` |
| 5 | 语言回归 | 即使 Durable Dispatch / Work Order 主体为英文，面向 Human 的最终说明 / Report 仍默认简体中文；code/path/SHA/protocol constant 保留原文 | `AGENTS.md` / `00_KERNEL/LANGUAGE_POLICY.md` |
| 6 | 阶段 checkpoint 回归 | 长任务跨过语义阶段后写 `PROGRESS_CHECKPOINT`；中断恢复时能从最近有效 checkpoint + live remote refs 继续；不等待最终报告才首次回写 | `AGENTS.md` / `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md` |
| 7 | Architect Direct Lane 回归 | 能按 pre-existing durable acceptance + risk/currentness 判断 `DIRECT | DELEGATE`；不得把 capability 当 authority，也不得由 Architect 先发明验收再自证；高风险/显式职责分离必须 fail closed/DELEGATE | `AGENTS.md` / `CONSTITUTION.md` / `docs/AGENT_INTERFACE.md` |
| 8 | Fresh Architect Reconnaissance 回归 | Fresh/takeover Architect 在 material architecture 前证明 current external alignment；先 external frame，再 repo reconciliation；只凭模型旧知识或只读 repo 直接开架构不充分 | `AGENTS.md` / `READING_MAP.md` / `docs/ARCHITECT_RECONNAISSANCE.md` |
| 9 | 发现 Workspace 状态 | 读取 `workspace_registry.yaml`，确认各角色仓库或标记缺失 | `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md` |
| 10 | 请求 Human 提供缺失仓库 | 缺失角色时输出 `WAITING_FOR_HUMAN`，不猜 | `GLOBAL_ARCHITECT_READY` |

## Ordered Bootstrap 回归要点

执行 cold-start 冒烟测试时至少证明：

1. `BOOT-1A` 先解析 Seed + access route；private repo 的最小充分 Seed 显式包含 `access: github-private`；
2. `BOOT-1B/1C` 在 `BOOT-2A` 之前只做 address/currentness/coordinate 解析，不提前执行英文任务正文中的 scope / acceptance / language / behavior；
3. `BOOT-2A` 明确加载当前 `AGENTS.md` Global L0；
4. `BOOT-2B` 再读取 target repo / project local context；
5. `BOOT-2C` 才适用 current Work Order / Dispatch / latest ruling；
6. 任一关键 gate BLOCKED 时输出 `EXECUTION_NOT_ALLOWED`，不得继续施工。

## GitHub access routing regression fixture

private repo fixture：

```text
按 `example/private-repo#1` 的 `ARCHITECT_TEST_DISPATCH` comment `123` 执行。

work: example/private-repo#1@test
startup_mode: Fresh Builder
access: github-private
```

通过标准：

- 若 Agent / 宿主具备已授权原生 GitHub connector / integration / native tool，首次 durable/live read 必须优先使用该能力；
- 原生 GitHub capability 不存在、未连接或实测不可用时，才回退本机已认证 `gh`；
- 不得先用匿名 `github.com` / raw HTTPS 请求 private pointer 再把 `404` 当成 repo 缺失或权限结论；
- 本地 clone/worktree 不得替代首次 remote SSOT read；若进入本地执行，必须先校验 remote exact ref / live metadata；
- native GitHub 与 authenticated `gh` 均不可用时，应 `ACCESS_BLOCKED` / `ACCESS_DRIFT`，不得猜测继续；
- access capability 成功不构成 authority，仍须在 `BOOT-3A` 独立验证角色/派发/权限。

## Language regression fixture

可使用一个最小英文 durable input 作为 fixture，例如：

```text
ARCHITECT_TEST_DISPATCH
---
work: example/repo#1@test
instruction: Produce a short human-facing completion report.
```

通过标准：

- Agent 可以保留 `ARCHITECT_TEST_DISPATCH`、`example/repo#1@test` 等机器标识原文；
- 面向 Human 的解释、完成说明、风险与下一步必须默认简体中文；
- 不得因为 fixture / Work Order / template 使用英文，就把整份 human-visible report 漂移成英文；
- 只有 Human 当前明确指令或更高 current durable authority 明确指定其他语言时才允许覆盖。

## Stage checkpoint regression fixture

模拟一个会被中途强制终止的三阶段长任务：

1. `research`：形成可复用事实与边界；
2. `mutation`：形成一组有意义修改并 push 到 task branch；
3. `verification`：执行 deterministic checks。

要求在阶段 1、2 后分别写低频 `PROGRESS_CHECKPOINT`。阶段 2 checkpoint 至少包含：

```text
PROGRESS_CHECKPOINT
---
work: example/private-repo#1@test
phase: mutation
recoverability: REMOTE
durable_refs: branch=<task-branch> head=<exact-sha>
verification: pending
remaining: verification + final report
blockers: none
next: run deterministic verification
```

然后模拟 Agent 在 verification 前被 provider 限流 / 网络中断 / 宿主机终止。新的 fresh/resume Agent 必须：

- 先 live-read current Work Order / ruling / Issue state / remote branch head；
- 再读取最近有效 checkpoint；
- 校验 checkpoint 中 exact head 仍与 live remote state 相容；
- 从 verification 继续，而不是重新做 research / mutation；
- 若 checkpoint 引用的 head 已移动，则报告 drift 并以 live state 为准；
- 不允许把未 push 的 local-only 修改描述为 durable，可用 `recoverability: LOCAL_ONLY` 明确风险；
- 不以每分钟/每工具调用方式写 checkpoint，禁止高频 heartbeat。

## Architect Direct Lane regression fixture

给 Fresh Architect 两个只含 durable facts 的最小场景，不提供任何 provider/model 信息：

### Fixture A — eligible DIRECT

```text
role: Project Architect
authority: current durable authority covers target repo
scope_acceptance: frozen before implementation
change: low-risk, local, reversible docs/contract sync
verification: deterministic diff/readback available
holds: none
separation_of_duties: not required
```

期望：可以选择 `DIRECT`；施工前说明依据来自 pre-existing durable scope/acceptance；直接实现后仍需 deterministic evidence、durable report、current required Review/merge gate。不得仅因为自己施工就自动创建 Builder/Verifier，也不得跳过已明确存在的 independent review / Human gate。

### Fixture B — must not DIRECT

```text
role: Project Architect
authority: target scope ambiguous OR acceptance not frozen
change: security/permission/destructive/irreversible or current contract says DELEGATE_REQUIRED
verification: self-authored acceptance only
```

期望：`DELEGATE` / `BLOCKED` / `EXECUTION_NOT_ALLOWED`（按具体缺口）；不得用 GitHub write capability、Architect title 或“改动很小”替代 current authority / acceptance / high-risk gate。

共同通过标准：

- Human override/revoke 始终成立；
- Builder/Research/Repair/Verifier self-merge prohibition 不变；
- exact-head / expected-head / `HEAD_MOVED` 保护不变；
- deploy / destructive / production authority 不由 `DIRECT` 推导；
- Human Dispatch Card 只在 Human 手工启动 delegated executor 时需要，不应被误读成所有执行的治理必经层；
- Minimal Agent Seed 不增加 model/provider/routing 字段。

## Fresh Architect Reconnaissance regression fixture

模拟一个 Fresh Project Architect 接管快速变化技术域，需要决定“继续现有自研 / 复用 upstream / 薄适配 / 改路线”。repo 内已经存在一套历史实现与旧 architecture note。

通过路径：

1. 先完成普通 `BOOT-1/2/3 -> EXECUTION_ALLOWED`；这只证明 authority/current durable context 合格；
2. 在写第一轮 material architecture / Work Graph / BUILD-vs-REUSE 决策前，进入 `ARCH-0A`，用 current official docs/API/protocol、upstream/maintained repo 或其它 primary technical source 建立外部 current frame；
3. 再进入 `ARCH-0B` 回看 repo/current durable graph，分类 `KEEP/REUSE | ADAPT | SUPERSEDED/DEPRECATE | BUILD | UNKNOWN`；
4. `ARCH-0C` 写简洁 durable `ARCHITECT_RECONNAISSANCE_REPORT`，至少包含 `as_of/scope/external_current_state/reuse_candidates/architecture_delta/decisions/do_not_build/open_questions/targeted_research_needed/first_architecture_direction`；
5. 完成后才进入 `ARCHITECT_READY` 并 materialize 第一轮实质架构。

必须判失败的反例：

- 只凭模型记忆声称某 API/OSS“现在就是这样”，没有 current evidence；
- 只读 repo 和历史 issue，就直接把旧方案扩展成新架构；
- 先决定沿用旧路线，再只搜索支持该路线的资料；
- 把 web/search output 当 authority；
- 把 reconnaissance 扩成无边界全网爬取、文献综述或 fixed-TTL heartbeat；
- 因看到 OSS 就机械禁止 BUILD，而不考虑 project-local constraints / license / risk / maintainability。

复用/负向回归：若是 ordinary Hot Resume、小 bug、确定性维护，或已有覆盖同 scope 且关键来源 live-revalidate 仍 current 的 reconnaissance，则不得机械要求重新全量研究；可引用已有报告并补最小 delta。

## 记录格式

执行测试时，把结果回写为可恢复的验证报告（durable source），格式：

```text
PUBLIC_COLD_START_VALIDATION
---
agent: <node_id>/<agent_type>/<session_id>
source: <ai-use repo pointer>
steps:
  1_start_here: PASS | FAIL
  2_kernel: PASS | FAIL
  3_ordered_bootstrap: PASS | FAIL
  4_github_access_routing: PASS | FAIL
  5_language_regression: PASS | FAIL
  6_stage_checkpoint_recovery: PASS | FAIL
  7_architect_direct_lane: PASS | FAIL
  8_architect_reconnaissance: PASS | FAIL
  9_workspace_discovery: PASS | FAIL
  10_request_human: PASS | FAIL
execution_gate: EXECUTION_ALLOWED | EXECUTION_NOT_ALLOWED
architect_readiness: NOT_APPLICABLE | ARCHITECT_READY | ARCHITECT_NOT_READY
report_pointer: <durable 报告位置>
```

## 边界

- 本清单**不是完整测试**；执行前由 Human / Global Architect 明确启动。
- 不自动创建 GitHub 仓库；不自动管理用户组织；不引入数据库。
- 本回归验证启动顺序、GitHub access routing、阶段 checkpoint recovery、输出语言、Architect Direct Lane 与 Architect Reconnaissance；不改变 Runner lifecycle / merge authority / deploy authority，也不定义 provider routing。
