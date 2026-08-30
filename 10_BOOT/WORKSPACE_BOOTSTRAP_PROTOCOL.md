# Workspace Bootstrap Protocol

**Classification: L2 Targeted Reference.** 新组织 / 新 Global Architect 初始化 workspace 时触发读取。

**Protocol Version: 1.1.0**

## 目的

新组织仅提供 governance repo 时，Global Architect 需要能完成：

- 工作空间发现（哪些仓库属于本 workspace）；
- 仓库角色识别（每个仓库承担什么职责）；
- 新组织初始化（首次搭建最小可运行 workspace）；
- Global Architect Ready 状态确认。

## 仓库角色（role registration）

**不要假设仓库名称。** 仓库按角色注册，名称由各组织自定。

| 角色 | 必需性 | 职责 |
| --- | --- | --- |
| `governance` | 必需 | 规则、协议、Agent Interface。 |
| `control_plane` | 必需 | Work Order、Issue、状态流转、dispatch / coordination。 |
| `asset` | 可选 | 需要独立资产事实源时注册。 |
| `project` | 可选，可多个 | 具体项目代码；workspace 可先无 project。 |

角色必须通过 registry 显式声明，不得通过仓库名猜测角色。公共文档中的 `ai-use` / `ai-hub` 只能作为常见命名示例，不是固定远端地址。

## Workspace Registry（最小结构）

workspace 的仓库拓扑以 YAML 声明，**机器可读 + 人类可读**，不引入数据库。Protocol 1.1.0 只澄清 registry schema `1.0.0` 字段的 optionality / resolution 语义，**不引入新 schema generation**；已有合法 1.0.0 registry 不需要迁移。

```yaml
workspace_registry:
  version: 1.0.0
  governance:
    repo: <owner/repo>
  control_plane:
    repo: <owner/repo>
  asset: null
  projects:
    repos: []
```

字段说明：

- `workspace_registry.version` —— registry 结构版本，保持 `1.0.0`；
- `governance.repo` —— current governance 仓库位置；
- `control_plane.repo` —— deployment-local control-plane 仓库的 canonical repo coordinate；**公共 ai-use 需要引用“自己的 hub/control plane”时应通过这里（或等价 deployment registration）解析，不指向上游维护者私有仓库，也不假设 sibling 目录名称**；
- `asset` —— 可选；需要时写 `{ repo: <owner/repo> }`，不需要时为 `null` / omit；已有 1.0.0 registry 仍写具体 `asset.repo` 继续有效；
- `projects.repos` —— 项目仓库列表，可为空数组。

registry 保存在 governance repo 内（例如 `workspace_registry.yaml`），作为 workspace topology 的 durable source。

## 初始化步骤

1. **定位 governance** —— 以当前 governance repo 为入口，确认 `AGENTS.md` / bootstrap 协议可达。
2. **读取或建立 registry** —— 已存在 `workspace_registry.yaml` 时读取；首次搭建且尚不存在时，按 Human 明确提供的 repo facts 创建/提交 registry，**不得把“文件尚不存在”误判成一个已经存在但不可访问的 workspace**。
3. **确认必需角色** —— `governance` + `control_plane` 必须无歧义；缺失任一必需角色才 `WAITING_FOR_HUMAN`。`asset` / `project` 缺失不阻塞最小 workspace。
4. **注册 workspace** —— 把 registry 写入 durable governance repo。
5. **启动 Global Architect** —— 执行 Bootstrap Check（`10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`）。
6. **确认 Ready** —— 输出 `GLOBAL_ARCHITECT_READY` 状态。

## Workspace State Machine

workspace 的初始化状态按序演进。**local registry 直接代表 READY** 是错误语义。

```text
WORKSPACE_EMPTY
   ↓
WORKSPACE_DISCOVERED
   ↓
WORKSPACE_REGISTERED_LOCAL
   ↓
WORKSPACE_REGISTERED_DURABLE
   ↓
GLOBAL_ARCHITECT_READY
```

各状态含义：

| 状态 | 含义 |
| --- | --- |
| `WORKSPACE_EMPTY` | 尚未发现/声明必需 workspace topology。 |
| `WORKSPACE_DISCOVERED` | 已获得足够 repo facts，但 registry 尚未 durable。 |
| `WORKSPACE_REGISTERED_LOCAL` | registry 已写入，但仅存在本地（未进入 durable source）。 |
| `WORKSPACE_REGISTERED_DURABLE` | registry 已进入 durable governance repo。 |
| `GLOBAL_ARCHITECT_READY` | 必需角色完整、registry durable，Global Architect 可按 current authority 接手调度。 |

判定规则：

- 若 registry 只存在本地：状态为 `WORKSPACE_REGISTERED_LOCAL`，不得视为 READY。
- 仅当 registry 已进入 durable source：才允许 `WORKSPACE_REGISTERED_DURABLE`。
- `GLOBAL_ARCHITECT_READY` 只要求 **governance + control_plane** 两个必需角色已注册且 current；`asset: null` / `projects.repos: []` 是合法 READY 状态。
- 可选角色日后增加时更新 registry，不需要重建 governance identity 或迁移 schema version。

## Global Architect Ready 状态

初始化完成时输出固定状态块：

```yaml
GLOBAL_ARCHITECT_READY
version: 1.0.0
identity:
  node: <node_id | none-if-not-applicable>
  agent_type: global-architect
  session: <session_id | none-if-not-applicable>
workspace:
  status: <initialized | partial>
repositories:
  governance: <owner/repo>
  control_plane: <owner/repo>
  asset: <owner/repo | none>
  projects: [<owner/repo>]
authority_root:
  source: <governance repo + constitution/current Human authority pointer>
status: READY | BLOCKED | WAITING_FOR_HUMAN
blockers:
  - <blocker description | none>
```

状态取值：

- `READY` —— 必需 workspace roles 完整且 registry durable；可选 role 可以为空。
- `BLOCKED` —— 存在 currentness / authority / access 冲突，无法安全自解。
- `WAITING_FOR_HUMAN` —— 缺少**必需** role 的 repo fact（governance / control_plane），或多个候选无法从 durable facts 裁决。

## 回写要求

`GLOBAL_ARCHITECT_READY` 状态必须可回写 durable source（registry 所在 governance repo / current authority anchor）。仅存在于聊天的“已就绪”不算数。

## 边界

- 本协议只定义 workspace 初始化与角色发现；不实现 Router / Fleet 调度。
- 不自动创建 GitHub 仓库，不自动管理用户组织。
- 不把 repo name / repo owner / authenticated GitHub principal 自动提升为 role/authority。
- 具体仓库名称由各组织决定；control-plane 地址以 role registration 为准。
