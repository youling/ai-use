# HOST_AGENT.md 可复制模板

先读 `../30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md`。本模板是 **Agent-facing resolved Host Contract shape**：服务 AI Agent / Human-AI 协作所需的 Host 上下文发现，不是全机配置数据库、desired profile、资产档案、Work SSOT 或 secret store。无适用项就删掉，不保留空壳。

> 默认 materialization：`<OS-native Documents folder>/HOST_AGENT.md`。
> canonical resolved copy / owner pointer：`<private instance owner durable pointer>`（本部署为 `youling/ai-hub`）；本机 Documents 文件是可恢复的 materialized copy。

## Initial V1 — minimum reference shape

Human current direction: initial **HOST_AGENT.md** should stay deliberately small. V1 standardizes the common Agent directories/context already agreed and shows the current OpenCode canary projection as a concrete example. OpenCode is **not** a universal public dependency: deployments include only actually enabled Agent runtime blocks, and new Agent classes extend the file later without redesigning the common section.

```yaml
host_agent_version: 1.0.0
observed_at: <timestamp>

durable:
  work: <GitHub / owner durable pointer>
  governance: <ai-use/current pointer>
  host_agent_canonical: <private instance owner durable pointer; this deployment: ai-hub>

paths:
  workspace:
    path: <resolved workspace root/policy>
    owner: HOST_MANAGED
    relocatable: true
  config:
    path: <non-secret config + declared-variable area>
    owner: HOST_MANAGED
    relocatable: true
  state:
    path: <Agent/application state area>
    owner: <HOST_MANAGED | VENDOR_OWNED | OWNER_DEFINED>
    relocatable: <true only when current owner/migration contract permits>
  cache:
    path: <rebuildable cache area>
    owner: HOST_MANAGED
    relocatable: true
  temp:
    path: <attempt-local temp area>
    owner: HOST_MANAGED
    relocatable: true
  exchange:
    in: <Host -> container bounded input>
    out: <container -> Host bounded output>
  secrets:
    catalog_ref: <logical pointer to the Human-owned key/secret catalog>
    runtime_root: </run/secrets or platform-equivalent>
    refs:
      github_machine:
        ref: <logical secret reference>
        class: <owner-defined credential class, e.g. GITHUB_MACHINE_IDENTITY>
        custody: <owner-defined custody class, e.g. HOST_SECRET_STORE>
        materialize: <owner-defined runtime projection, e.g. SHORT_LIVED_RUNTIME_CREDENTIAL>
      model_provider:
        ref: <logical secret reference>
        class: <owner-defined credential class, e.g. MODEL_PROVIDER_AUTH>
        custody: <owner-defined custody class, e.g. HOST_SECRET_STORE>
        materialize: <owner-defined runtime projection, e.g. RUNTIME_SECRET_FILE>

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
      credential_ref: <logical provider secret reference>
      materialize: </run/secrets/opencode/...>
```

### V1 rules

- `paths.*` is the common Agent collaboration context; do not copy the whole machine configuration into it.
- A path may move only when its current owner/class permits it. `HOST_MANAGED + relocatable=true` grants the placement Agent autonomous relocation authority when material drift/benefit is evidenced.
- `Secrets`, device identity, Human-unique data, vendor-owned state and UNKNOWN ownership are not autonomously relocatable merely because storage pressure exists.
- `paths.secrets.catalog_ref` points to the Human-owned secret/key catalog; no key/token/private-key value enters **HOST_AGENT.md**.
- Secret entries in V1 carry reference/classification/materialization metadata only. `class / custody / materialize` values are resolved by the current secret/deployment owner; this template does **not** create a credential taxonomy SSOT. `GITHUB_MACHINE_IDENTITY` and `MODEL_PROVIDER_AUTH` are current examples, not public enums.
- `agents.opencode.*` is the current canary/example launch/runtime projection. Include it only where OpenCode is actually enabled; do not pre-create DSH/Claude Code/other runtime fields.
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
- 对明确标记 `HOST_MANAGED + relocatable=true` 的目录，material drift 下 Agent 可自主迁移；其它 ownership 仍 fail closed。
- 迁移成功后先回写 private-instance durable canonical，再重新 materialize 本机 **HOST_AGENT.md**；旧位置只有在 no-unique-state proof 后才 GC。
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
      - ref: <logical secret reference>
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
RE_RESOLUTION != BLIND_MIGRATION
HOST_MANAGED + relocatable=true + MATERIAL_DRIFT
  => AUTONOMOUS_RELOCATION_ALLOWED
```

迁移顺序：`probe -> classify -> resolve target -> quiesce(if needed) -> copy/move -> verify -> switch -> durable writeback -> local rematerialize -> old-path GC after proof`。

## 10. Cleanup / rebuild expectations

说明 Cache/Temp 如何判断可删；released workspace 如何证明 durable；image/container 如何重建；哪些 state 必须 preserve；secret/device identity 如何重新 enrol/恢复而不保存 raw secret。

## 11. Host-specific exceptions

仅保留会改变 Agent 行为的少数例外；不要把 **HOST_AGENT.md** 写成机器百科全书，也不要为了“只维护一个文件”把 Assets、Work、Secret、vendor database 或完整系统配置复制进来。
