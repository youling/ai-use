# HOST_AGENT.md 可复制模板

先读 `../30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md`。本模板是 **resolved Host Contract shape**，不是 desired profile、资产档案或 secret store。无适用项就删掉，不保留空壳。

> 默认 materialization：`<OS-native Documents folder>/HOST_AGENT.md`。
> canonical resolved copy / owner pointer：`<deployment-local pointer>`

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

- Durable Work/Knowledge：`<pointer>`
- 本机只是 materialized execution environment；不要把本地 cache/temp/session 当 SSOT。
- Secret 只用 reference，不读取/写入 raw value。
- Vendor-owned runtime/state 不因存在共享工具就自动去重。
- 路径是 current resolution，不是永恒配置；先做低成本 drift probe。
- 有 material drift 才重新解析；重新解析不等于自动迁移。

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

## 5. Placement rationale

只记录不显然、容易被下一位 Agent 重新踩错的判断：root 为什么放这里；哪些 volume 属于同一物理设备；哪些 store 必须跟 workspace 同 filesystem；哪些统一配置会破坏 locality；哪些目录保持 vendor default。

## 6. Do not duplicate / do not migrate

列出已经存在的 shared tool、必须保留的 vendor runtime、live package store、state/secret boundary。

## 7. Durable pointers

```text
governance: <ai-use/current governance pointer>
host desired profile: <pointer>
resolved instance evidence: <pointer>
project/control-plane entry: <pointer>
specialized follow-ups: <pointer(s)>
```

## 8. Drift triggers

disk/mount/drive-letter 变化、新增/移除高速 storage、filesystem/locality 能力变化、material capacity pressure、Host role 变化、WSL/container/runtime storage 模式变化、current root 不存在/不可写、desired profile material revision。

```text
RE_RESOLUTION != AUTOMATIC_MIGRATION
```

## 9. Cleanup / rebuild expectations

说明 Cache/Temp 如何判断可删；released workspace 如何证明 durable；image/container 如何重建；哪些 state 必须 preserve；secret/device identity 如何重新 enrol/恢复而不保存 raw secret。

## 10. Host-specific exceptions

仅保留会改变 Agent 行为的少数例外；不要把 **HOST_AGENT.md** 写成机器百科全书。
