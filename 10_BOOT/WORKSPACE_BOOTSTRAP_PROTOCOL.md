# Workspace Bootstrap Protocol

**Classification: L2 Targeted Reference.** 新组织 / 新 Global Architect 初始化 workspace 时触发读取。

**Protocol Version: 1.0.0**

## 目的

新组织仅提供 `ai-use`（governance repo）时，Global Architect 需要能完成：

- 工作空间发现（哪些仓库属于本 workspace）；
- 仓库角色识别（每个仓库承担什么职责）；
- 新组织初始化（首次搭建完整 workspace）；
- Global Architect Ready 状态确认。

## 仓库角色（role registration）

**不要假设仓库名称**。仓库按**角色**注册，名称由各组织自定。角色与职责：

| 角色 | 职责 |
| --- | --- |
| `governance` | 规则、协议、Agent Interface。 |
| `control_plane` | 任务、Issue、状态流转。 |
| `asset` | 资产事实源。 |
| `project` | 具体项目代码（可多个）。 |

角色必须通过 registry 显式声明，不得通过仓库名猜测角色。

## Workspace Registry（最小结构）

workspace 的仓库拓扑以 YAML 声明，**机器可读 + 人类可读**，不引入数据库。

```yaml
workspace_registry:
  version: 1.0.0
  governance:
    repo: <owner/repo>
  control_plane:
    repo: <owner/repo>
  asset:
    repo: <owner/repo>
  projects:
    repos:
      - <owner/repo>
```

字段说明：

- `workspace_registry.version` —— registry 结构版本，当前 `1.0.0`；
- `governance.repo` —— governance 仓库位置；
- `control_plane.repo` —— control plane 仓库位置；
- `asset.repo` —— asset 仓库位置；
- `projects.repos` —— 项目仓库列表（可为空数组）。

registry 保存在 governance repo 内（如 `workspace_registry.yaml`），作为 workspace 拓扑的 durable source。

## 初始化步骤

1. **定位 governance** —— 以 ai-use（governance repo）为入口，确认 Kernel 与协议可达。
2. **发现角色** —— 读取 `workspace_registry.yaml`，确认各角色仓库位置；缺失角色标记 `WAITING_FOR_HUMAN`。
3. **注册 workspace** —— 首次搭建时按 §Registry 声明各角色仓库。
4. **启动 Global Architect** —— 执行 Bootstrap Check（`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`）。
5. **确认 Ready** —— 输出 `GLOBAL_ARCHITECT_READY` 状态。

## Global Architect Ready 状态

初始化完成时输出固定状态块：

```yaml
GLOBAL_ARCHITECT_READY
version: 1.0.0
identity:
  node: <node_id>
  agent_type: global-architect
  session: <session_id>
workspace:
  status: <initialized | partial>
repositories:
  governance: <owner/repo>
  control_plane: <owner/repo | none>
  asset: <owner/repo | none>
  projects: [<owner/repo>]
authority_root:
  source: <governance repo + constitution pointer>
status: READY | BLOCKED | WAITING_FOR_HUMAN
blockers:
  - <blocker description | none>
```

状态取值：

- `READY` —— workspace 完整，Global Architect 可接手调度。
- `BLOCKED` —— 存在无法自解的状态冲突，需报告，不靠猜。
- `WAITING_FOR_HUMAN` —— 缺少角色仓库（如 control_plane / asset / project），需 Human 提供。

## 回写要求

`GLOBAL_ARCHITECT_READY` 状态必须可回写 durable source（registry 所在 repo / 当前 authority issue）。
仅存在于聊天的"已就绪"不算数。

## 边界

- 本协议只定义 workspace 初始化与角色发现；不实现 Router / Fleet 调度。
- 不自动创建 GitHub 仓库，不自动管理用户组织。
- 具体仓库名称由各组织决定，本协议不绑定任何具体命名。