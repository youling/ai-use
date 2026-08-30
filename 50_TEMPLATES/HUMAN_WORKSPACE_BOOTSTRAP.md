# Human Workspace Bootstrap — 首次使用清单

**分层**: Human 层（新用户首次搭建 workspace）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 给新用户首次搭建 workspace 的人类侧清单 |
| 谁使用 | 新组织的 Human / 首次搭建者 |
| 什么时候使用 | 第一次使用 ai-use 搭建自己的 workspace 时 |
| 禁止用途 | 不假设用户使用任何特定 owner/repo 或仓库名；不把上游维护者私有控制面当作公共依赖；不自动创建仓库；不引入数据库 |

## 首次使用步骤

1. **准备 governance repo（必需）** —— 规则、协议、Agent Interface 所在的仓库。
   - 可以 fork / clone ai-use 作为起点，也可以自建兼容 governance repo。
2. **准备 control-plane repo（必需）** —— Work Order、Issue、状态流转所在的部署实例控制面。
   - 名称由你决定；在 registry 中以 `control_plane` role 注册。
3. **按业务需要准备可选 repo** —— `asset` / `project` 都可以暂时为空；不要为了模板完整创建无实际用途的空仓库。
4. **注册 workspace** —— 在 governance repo 内创建/提交 `workspace_registry.yaml`，至少声明 governance + control_plane；control-plane canonical coordinate 由 `workspace_registry.control_plane.repo` 解析。
5. **启动 Global Architect** —— 执行 Bootstrap Check，确认 `GLOBAL_ARCHITECT_READY`。

## 填空模板

```text
HUMAN_WORKSPACE_BOOTSTRAP
---
governance_repo: <owner/repo>
control_plane_repo: <owner/repo>
asset_repo: <owner/repo | none>
project_repos: [] | [<owner/repo>, ...]

已准备: <governance + control_plane；可选 asset/projects>
已注册: <workspace_registry.yaml 位置>
Global Architect 状态: <READY | BLOCKED | WAITING_FOR_HUMAN>
```

判定边界：

- 缺 governance / control_plane 的真实 repo fact -> `WAITING_FOR_HUMAN`；
- `asset_repo: none` 或 `project_repos: []` -> 合法，不阻塞最小 workspace；
- repo 名称、repo owner、GitHub 登录身份本身不产生 role / authority。

## 规范源

- `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`（角色定义、registry、GLOBAL_ARCHITECT_READY）
- `START_HERE.md`（公共入口）
