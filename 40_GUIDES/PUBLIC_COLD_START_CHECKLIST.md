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
| 6 | 发现 Workspace 状态 | 读取 `workspace_registry.yaml`，确认各角色仓库或标记缺失 | `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md` |
| 7 | 请求 Human 提供缺失仓库 | 缺失角色时输出 `WAITING_FOR_HUMAN`，不猜 | `GLOBAL_ARCHITECT_READY` |

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
  6_workspace_discovery: PASS | FAIL
  7_request_human: PASS | FAIL
execution_gate: EXECUTION_ALLOWED | EXECUTION_NOT_ALLOWED
report_pointer: <durable 报告位置>
```

## 边界

- 本清单**不是完整测试**；执行前由 Human / Global Architect 明确启动。
- 不自动创建 GitHub 仓库；不自动管理用户组织；不引入数据库。
- 本回归只验证启动顺序、GitHub access routing 与输出语言不变量，不改变 Runner lifecycle / merge authority / deploy authority。
