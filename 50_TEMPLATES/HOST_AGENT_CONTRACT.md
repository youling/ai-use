# HOST_AGENT.md 可复制模板

先读 `../30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md`。本模板是 **Agent-facing resolved Host Contract shape**：服务 AI Agent / Human-AI 协作所需的 Host 上下文发现，不是全机配置数据库、desired profile、资产档案、Work SSOT 或 secret store。无适用项就删掉，不保留空壳。

> 默认 materialization：`<OS-native Documents folder>/HOST_AGENT.md`。
> canonical resolved copy / owner pointer：`<deployment-local pointer>`

## Initial V1 — minimum required shape

Human current direction: initial `HOST_AGENT.md` should stay deliberately small. V1 only standardizes the common Agent directories/context already agreed plus the current OpenCode runtime projection. New Agent classes extend the file later with a new runtime block; they do not redesign the common section.

```yaml
host_agent_version: 1.0.0
observed_at: <timestamp>

durable:
  work: <GitHub / owner durable pointer>
  governance: <ai-use/current pointer>

paths:
  workspace: <resolved workspace root/policy>
  config: <non-secret config + declared-variable area>
  state: <Agent/application state area>
  cache: <rebuildable cache area>
  temp: <attempt-local temp area>
  exchange:
    in: <Host -> container bounded input>
    out: <container -> Host bounded output>
  secrets:
    catalog_ref: <logical pointer to the user's key/secret catalog, e.g. 我的文件夹/密钥>
    runtime_root: </run/secrets or platform-equivalent>
    refs:
      github_machine:
        ref: <logical secret reference>
        class: GITHUB_MACHINE_IDENTITY
        custody: HOST_SECRET_STORE
        materialize: SHORT_LIVED_RUNTIME_CREDENTIAL
      model_provider:
        ref: <logical secret reference>
        class: MODEL_PROVIDER_AUTH
        custody: HOST_SECRET_STORE
        materialize: RUNTIME_SECRET_FILE

agents:
  opencode:
    enabled: true
    runtime: container
    image: <immutable image/config/manifest pointer>
    command: <foreground OpenCode entry, e.g. serve>
    workspace: <Linux-native workspace policy/path>
    config: <OpenCode non-secret config projection>
    state: <OpenCode session/state lifecycle>
    cache: <OpenCode cache path/lifecycle>
    temp: <OpenCode temp path/lifecycle>
    exchange:
      in: <resolved input projection>
      out: <resolved output projection>
    github:
      credential_ref: <logical machine-identity / short-lived token projection reference>
      recovery_required: true
    model_auth:
      credential_ref: <logical provider SecretReference>
      materialize: </run/secrets/opencode/...>
```

### V1 rules

- `paths.*` is the common Agent collaboration context; do not copy the whole machine configuration into it.
- `paths.secrets.catalog_ref` points to the Human-owned secret/key catalog. It may resolve to a local folder such as `我的文件夹/密钥`, but no key/token/private-key value enters `HOST_AGENT.md`.
- Secret entries in V1 are classification metadata only: `ref / class / custody / materialize`. The initial classes are `GITHUB_MACHINE_IDENTITY` and `MODEL_PROVIDER_AUTH`; add new classes only when a real Agent/runtime need appears.
- `agents.opencode.*` contains only OpenCode-specific launch/runtime context. Do not pre-create DSH/Claude Code fields in V1.
- GitHub recovery is mandatory for the OpenCode runtime: a fresh runtime must be able to recover durable Work/source from GitHub using a Host-projected credential reference.
- `state/cache/temp` are distinct even if a concrete Host maps some of them near each other physically.
- New Agent class = add a sibling runtime block under `agents:` and only extend common fields when that new runtime proves a genuinely shared need.

---

## 0. Host identity / currentness

```text
host_ref: <stable local/private reference>
asset_ref: <optional pointer>
role: <human workstation / control host / ...>
observed_at: <timestamp>
profile_owner: <pointer>
resolved_contract_owner: <pointer>
```

## 1. Agent entry rules

- **本文件只面向 Agent 协作上下文。** Agent 应把它当 single discovery surface，不得推断成所有 Host 数据的唯一物理来源。
- Durable Work/Knowledge：`<pointer>`
- 本机只是 materialized execution environment；不要把本地 cache/temp/session 当 SSOT。
- Secret 只用 reference，不读取/写入 raw value。
- Vendor-owned runtime/state 不因存在共享工具就自动去重。
- 路径是 current resolution，不是永恒配置；先做低成本 drift probe。
- 有 material drift 才重新解析；重新解析不等于自动迁移。
- 不同 Agent runtime 只读取与自己相关的字段；不要要求 OpenCode/DSH/Claude Code 复制维护各自一整套 Host 规则。

## 2. Placement-relevant observation

| 对象 | 当前观察 | 为什么与布局有关 |
| --- | --- | --- |
| OS / filesystem | ... | ... |
| Disk / volume / mount topology | ... | ... |
| Capacity pressure | ... | ... |
| IO / device class | ... | ... |
| hardlink/reflink/CAS/locality | ... | ... |
| container/runtime storage | ... | ... |

只保留影响 execution/placement 的 current observation；完整长期硬件事实指向 Assets/owner。

## 3. Seven domains

| Domain | Current path/store | Owner/class | Lifecycle / boundary |
| --- | --- | --- | --- |
| Execution | ... | host/vendor | ... |
| Workspace | ... | host/project | ... |
| Config | ... | host/vendor | non-secret |
| State | ... | app/vendor | preserve |
| Cache | ... | rebuildable | GC-able |
| Temp | ... | attempt/runtime | short-lived |
| Secrets | <reference only> | vault/device | never raw |

## 4. Resolved semantic roots

```text
CODE_ROOT        <path or N/A>
WORK_ROOT        <path or N/A>
TOOLS_ROOT       <path or N/A>
CONFIG_ROOT      <path or DECLARE-ONLY/N/A>
CACHE_ROOT       <path or DECLARE-ONLY/N/A>
AGENT_TEMP_ROOT  <path or DECLARE-ONLY/N/A>
```

## 5. Agent runtime projections

只为实际存在/启用的 Agent runtime 建小节；每个 Agent 只记录会改变其启动、执行、恢复或权限判断的 Host-local 投影。

```text
agents:
  opencode:
    execution: <runtime/image/version pointer>
    workspace: <resolved policy/path>
    config: <non-secret config pointer / declared variables>
    state: <session/state lifecycle pointer>
    cache: <path/lifecycle>
    temp: <path/lifecycle>
    secrets:
      - ref: <logical SecretReference>
        materialize: </run/secrets/... or platform-equivalent>
    broker: <Host authority/broker pointer or N/A>

  dsh:
    ...

  claude-code:
    ...
```

规则：
- `secrets.ref` 只写逻辑 reference / custody / materialization metadata，不写 raw value；
- image/config/owner 优先写 immutable pointer 或 canonical owner pointer，不复制完整配置正文；
- Agent-specific runtime section 可以不同，但不能建立第二套 Host truth；
- 没有实际启用的 Agent 就不保留空壳；
- runtime session/history 可以是 State，但不得冒充 Durable Work truth。

## 6. Placement rationale

只记录不显然、容易被下一位 Agent 重新踩错的判断：root 为什么放这里；哪些 volume 属于同一物理设备；哪些 store 必须跟 workspace 同 filesystem；哪些统一配置会破坏 locality；哪些目录保持 vendor default。

## 7. Do not duplicate / do not migrate

列出已经存在的 shared tool、必须保留的 vendor runtime、live package store、state/secret boundary。

## 8. Durable pointers

```text
governance: <ai-use/current governance pointer>
host desired profile: <pointer>
resolved instance evidence: <pointer>
project/control-plane entry: <pointer>
specialized follow-ups: <pointer(s)>
```

## 9. Drift triggers

disk/mount/drive-letter 变化、新增/移除高速 storage、filesystem/locality 能力变化、material capacity pressure、Host role 变化、WSL/container/runtime storage 模式变化、current root 不存在/不可写、desired profile material revision。

```text
RE_RESOLUTION != AUTOMATIC_MIGRATION
```

## 10. Cleanup / rebuild expectations

说明 Cache/Temp 如何判断可删；released workspace 如何证明 durable；image/container 如何重建；哪些 state 必须 preserve；secret/device identity 如何重新 enrol/恢复而不保存 raw secret。

## 11. Host-specific exceptions

仅保留会改变 Agent 行为的少数例外；不要把 **HOST_AGENT.md** 写成机器百科全书，也不要为了“只维护一个文件”把 Assets、Work、Secret、vendor database 或完整系统配置复制进来。
