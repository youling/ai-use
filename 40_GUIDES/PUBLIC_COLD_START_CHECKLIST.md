# Public Cold Start Checklist

**用途**: 未来陌生用户冒烟测试的**入口**。本文件不执行测试，只定义验证路径。

**目标**: 仅给陌生用户一个 `ai-use` repo pointer 后，Agent 能否独立完成以下步骤。

## 验证路径

| # | 步骤 | 通过标准 | 证据位置 |
| --- | --- | --- | --- |
| 1 | 找 START_HERE | 通过入口文档定位第一阅读入口 | `START_HERE.md` |
| 2 | 加载 Kernel | 读到 `AGENTS.md`（L0）与 `NAMESPACE.md` | `AGENTS.md` / `NAMESPACE.md` |
| 3 | 执行 Bootstrap Check | 输出 `BOOTSTRAP_CHECK_REPORT` 并回写 durable source | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| 4 | 发现 Workspace 状态 | 读取 `workspace_registry.yaml`，确认各角色仓库或标记缺失 | `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md` |
| 5 | 请求 Human 提供缺失仓库 | 缺失角色时输出 `WAITING_FOR_HUMAN`，不猜 | `GLOBAL_ARCHITECT_READY` |

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
  3_bootstrap_check: PASS | FAIL
  4_workspace_discovery: PASS | FAIL
  5_request_human: PASS | FAIL
report_pointer: <durable 报告位置>
```

## 边界

- 本清单**不是完整测试**；执行前由 Human / Global Architect 明确启动。
- 不自动创建 GitHub 仓库；不自动管理用户组织；不引入数据库。