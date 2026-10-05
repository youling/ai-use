# Human Host Environment — 人类主控设备标准环境

**Classification: L2 Targeted Reference**
**Protocol Version: 1.0.0**

**Source:** `youling/ai-use#104`, `youling/ai-use#107`.

本协议定义 Human 主控设备（工作站、桌面机、笔记本、Human-controlled Linux desktop 等）的跨平台环境语义。它不规定所有机器必须使用同一盘符或路径，而是规定 Agent 应如何理解、探测、解析、维护一台 Human Host。

核心句：

> **治理给原则，Agent 看现场；语义布局标准化，物理布局按 Host 解析。**

```text
READ SEMANTIC INVARIANTS
  -> PROBE CURRENT HOST
  -> REASON ABOUT TOPOLOGY / CAPACITY / IO / LOCALITY / ROLE
  -> RESOLVE PHYSICAL MAPPING
  -> MATERIALIZE / UPDATE HOST_AGENT.md
  -> VERIFY
```

---

## 1. Applicability

本协议适用于 Human 日常直接使用的 Windows / macOS / Linux 主控设备、新 Human Host bootstrap、本地 AI/开发环境归整、Host cleanup/drift reconciliation，以及需要决定代码、工具、配置、缓存、Agent temp 等物理落点的任务。

它**不要求**普通 headless managed node / server 创建 Human Documents 目录或 **HOST_AGENT.md**。这类节点继续使用 Fleet/node/platform profile 与 owner-local bootstrap。普通 repo-only 工作如果本机环境已经 resolved 且没有 material Host concern，不因本协议强制重新盘点整台电脑。

## 2. Ownership boundary

```text
ai-use
= cross-platform Human Host semantics + discovery contract

platform/profile owner (e.g. Fleet)
= OS-specific desired profile / scanner / reconcile implementation

private instance owner
= resolved Host facts / evidence / local HOST_AGENT materialization
```

本协议不创建第二 Host registry、第二 Assets、第二 Fleet profile。若 deployment 有 Assets：`Assets = stable physical asset facts`；`HOST_AGENT.md = current operational observation + resolved environment projection`。购买日期、保修、完整硬件历史等不因为“Host information”进入 **HOST_AGENT.md**；只保留影响当前执行/布局判断的事实，并带 currentness。

## 3. Seven semantic domains

| Domain | 含义 | 默认纪律 |
| --- | --- | --- |
| **Execution** | OS/runtime/CLI/vendor binaries | host-managed shared tools 可复用；vendor runtime 不强拆 |
| **Workspace** | repo / worktree / active work | durable truth 外置；mutable attempt 必须隔离 |
| **Config** | 可移植、非 secret 的配置 | declarative / discoverable；不与 secret 混放 |
| **State** | session/history/DB/layout/undo 等持久状态 | 默认 preserve；不能把它当 cache |
| **Cache** | 可重建、可复用的性能状态 | 可 GC；删除影响性能而非正确性 |
| **Temp** | attempt/session 临时 scratch/runtime objects | 短命、可回收、按 attempt 隔离 |
| **Secrets** | token/key/password/device-bound credential | 单独 custody；不进普通 config/cache/Host Contract |

外部 durable Work / Knowledge 仍由 Git/GitHub 或 owner 指定的 durable source 持有，**不是第八个本地文件夹域**。

常见 Host-managed roots：`CODE_ROOT` / `WORK_ROOT` / `TOOLS_ROOT` / `CONFIG_ROOT` / `CACHE_ROOT` / `AGENT_TEMP_ROOT`。`State` 与 `Secrets` 是正式语义域，但不得为了整齐强行收敛到一个全局 root；许多 vendor/device-bound state 应留在 native store。

## 4. Principle-first, probe-driven placement

默认假设 Human 主控端 Agent 具备足够推理能力。协议固定**判定原则**，不固定 universal path table。Agent 解析物理布局时至少考虑 physical disk/volume/mount 拓扑、SSD/NVMe/HDD/network storage、filesystem 能力、capacity pressure、IO concurrency、hardlink/reflink/CAS/package-store locality、container/image/session storage、Host role、failure domain、migration/rebuild cost，以及现有路径是否已经合理。

```text
SEMANTIC_PROFILE = STANDARD
PHYSICAL_MAPPING = HOST_LOCAL_DECISION
ONE_LAYOUT_FITS_ALL = NO
```

禁止因为参考示例写过 `C:\...` / `D:\...` / `~/...` 就复制到另一台机器。重新解析布局不等于搬迁：`RE_RESOLUTION != AUTOMATIC_MIGRATION`。只有容量、IO/failure-domain、filesystem locality、生命周期边界或路径有效性存在 material benefit/correctness reason 时才迁移；“看起来更整齐”不是收益证明。

## 5. HOST_AGENT.md — Human Host stable discovery surface

Human Host 默认 materialize 一份：

```text
<OS-native Documents folder>/HOST_AGENT.md
```

这里的 Documents 是**逻辑 Known Folder**，不是硬编码路径。Windows 使用当前用户的 Documents Known Folder（可能被 OneDrive/策略重定向）；macOS 通常为 `~/Documents`；Linux desktop 优先 `XDG_DOCUMENTS_DIR`；headless/server 不要求伪造 Human Documents surface。

Client/tool-specific `AGENTS.md`、global instruction 或 bootstrap adapter 可以放一个**薄 pointer**告诉 Agent 先读取 **HOST_AGENT.md**，但不得复制整份正文并独立演化。

```text
HOST_AGENT.md = resolved current Host projection
HOST_AGENT.md != desired-profile SSOT
HOST_AGENT.md != secret store
HOST_AGENT.md != hardware asset registry
```

## 6. What HOST_AGENT.md must preserve

**HOST_AGENT.md** 不能只是目录表；还必须保存足以解释和重新裁决 placement 的 current Host observation：Host identity/role/current pointers、`observed_at`、storage topology、filesystem/locality/runtime capability、七域 mapping、resolved roots、placement rationale、vendor/state/secret boundaries、do-not-duplicate rules、drift triggers、cleanup/rebuild expectations。

只保存布局/执行需要的 observation。优先使用 `asset_ref` / `host_ref` pointer，而不是复制完整资产档案。动态事实（容量、mount、runtime storage、current role）必须带 `observed_at` 或等价 currentness。

## 7. Drift and self-update

Fresh Agent 读取现有 **HOST_AGENT.md** 后，先做低成本 drift probe，不能把旧 mapping 当永久真理。Material drift 包括 disk added/removed/replaced、drive/mount 改变、filesystem/locality 能力变化、material capacity pressure、Host role 变化、container/execution substrate 变化、root 不存在/不可写、desired profile material revision。

无 material drift：保持现有 mapping。命中 drift：re-probe → re-resolve mapping → only-if-justified migrate → verify → update canonical resolved Host Contract → re-materialize **Documents/HOST_AGENT.md**。硬件变化只触发重新评估权，不授予自动迁移/删除权。

## 8. Cleanup / normalization lifecycle

```text
INVENTORY
 -> CLASSIFY
 -> PROVE DURABILITY / REBUILDABILITY
 -> NORMALIZE
 -> MIGRATE ONLY WHEN BENEFICIAL
 -> GC RELEASED/REBUILDABLE STATE
 -> VERIFY
 -> DRIFT BASELINE
```

默认清理姿态：`DURABILITY_PROVEN + REBUILD_PATH_KNOWN + not secret/unique/current vendor runtime => CLEANUP_ELIGIBLE`。State、Secrets、vendor-owned current runtime、dirty/unpushed/owner-unknown work、UNKNOWN、device-bound identity、未证明可重建的 database/profile/volume 默认不自动删除。空间 delta 不是单对象删除证明；优先 per-object target-state evidence。

## 9. Secret boundary

**HOST_AGENT.md** 只记录 secret reference / custody class，例如 `credential_ref = <logical reference>`、`custody = external vault / native device store / device-bound`。不得保存 token、password、private key、cookie、recovery secret 等 raw value。Portable account secrets 可以由独立 Secret SSOT 管理；设备身份凭据可以保持 per-device。**Secret portability != authority portability**。

## 10. Interaction with Local Engineering Gate

本协议拥有长期 Host environment semantics；`10_BOOT/LOCAL_ENGINEERING_GATE.md` 只负责当前 Work capability/readiness preflight。

```text
Human Host Environment / HOST_AGENT
        ↓
Local Engineering Gate
        ↓
isolated Work Attempt
        ↓
durable writeback
        ↓
release / GC
```

Gate 不应重新发明目录或长期 Host profile；它消费已解析 Host Contract，并仅检查当前任务需要的能力。

## 11. Fresh Human Host bootstrap

```text
read ai-use L0 + targeted Human Host protocol
 -> resolve Host identity / owner profile
 -> probe current device
 -> classify seven domains
 -> resolve physical mapping
 -> install/materialize only missing required capabilities
 -> create/update HOST_AGENT.md
 -> verify
 -> establish drift baseline
 -> begin ordinary Work
```

已存在正确布局的设备优先保留，不为了统一外观做无收益迁移。

## 12. Anti-patterns

拒绝：复制另一台 canary 的路径；为目录整齐搬 vendor state；用 Cache 语义处理 State；把 Temp/Cache 当 durable Work；将 secret value 写进 Host Contract；每个 AI 客户端维护独立 Host 规则正文；新增磁盘就自动搬家；不 probe 当前机器就沿用旧 **HOST_AGENT.md**；把 Host Contract 变成 Assets/Fleet 第二 SSOT；为 headless server 强造 Human Documents 目录。

## 13. Minimum acceptance

Human Host 已 resolved 的最低条件：Host identity/role/profile owner 可定位；七域边界可解释；semantic roots 已按现场 evidence 解析；**HOST_AGENT.md** 在 OS-native Documents surface 可发现；placement rationale 与关键 observation 可恢复；secret/state/vendor boundaries 明确；无明显第二套 host-managed roots；drift/cleanup expectations 已记录；Fresh Agent 不依赖历史聊天即可开始 targeted work。

可复制形态见 `50_TEMPLATES/HOST_AGENT_CONTRACT.md`。
