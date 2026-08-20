# Human Workspace Bootstrap — 首次使用清单

**分层**: Human 层（新用户首次搭建 workspace）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 给新用户首次搭建 workspace 的人类侧清单 |
| 谁使用 | 新组织的 Human / 首次搭建者 |
| 什么时候使用 | 第一次使用 ai-use 搭建自己的 workspace 时 |
| 禁止用途 | 不假设用户使用任何特定仓库名（如 `youling/ai-use` / `youling/ai-hub`）；不自动创建仓库；不引入数据库 |

## 首次使用步骤

1. **准备 governance repo** —— 规则、协议、Agent Interface 所在的仓库。
   - 可以直接 fork / clone `ai-use` 作为起点，也可以自建。
2. **准备 control plane repo** —— 任务、Issue、状态流转所在的仓库。
   - 建议使用空仓库，用于追踪 Work Order。
3. **准备 asset repo** —— 资产事实源所在的仓库。
   - 按你的业务需要决定是否必需。
4. **注册 workspace** —— 在 governance repo 内创建 `workspace_registry.yaml`，声明各角色仓库。
5. **启动 Global Architect** —— 执行 Bootstrap Check，确认 `GLOBAL_ARCHITECT_READY`。

## 填空模板

```text
HUMAN_WORKSPACE_BOOTSTRAP
---
governance_repo: <owner/repo>
control_plane_repo: <owner/repo>
asset_repo: <owner/repo>
project_repos:
  - <owner/repo>

已准备: <governance / control_plane / asset / projects>
已注册: <workspace_registry.yaml 位置>
Global Architect 状态: <READY | BLOCKED | WAITING_FOR_HUMAN>
```

## 规范源

- `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`（角色定义、registry、GLOBAL_ARCHITECT_READY）
- `START_HERE.md`（公共入口）