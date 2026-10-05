# ADR-0010 — Human Host Environment：语义标准、现场解析与 HOST_AGENT 发现

- **Status:** Accepted direction / materialization in #107
- **Issue:** `youling/ai-use#107`
- **Sources:** `#104` Windows Human Host canary；多台真实 Human Host cleanup/profile dogfood
- **Decision level:** L2

## Context

Human 主控设备逐渐成为多个 AI 产品、Agent、CLI 与容器共享的执行面。固定盘符/目录会在不同机器、不同 OS、不同磁盘拓扑上迅速失效；完全不规定又会重复产生工具、cache、temp、workspace 和 secret 混杂。真实 canary 证明，同一语义在不同 Human Host 上可能得到完全不同的最优物理布局。

## Decision

采用：cross-platform semantic profile → Smart Agent probes current Host → Host-local physical resolution → resolved **HOST_AGENT.md**。固定七个生命周期语义域 `Execution / Workspace / Config / State / Cache / Temp / Secrets`，固定常用 Host-managed semantic roots，但不固定 universal physical paths。

Human Host 的稳定发现面为逻辑 OS-native Documents folder 下的 **HOST_AGENT.md**。它是 resolved operational projection，不是 desired-profile SSOT、Assets 或 secret store。Fresh Agent 必须把 saved observation 与 current Host 做低成本 drift 对比；material drift 可触发 re-resolution，但不得自动触发迁移。

## Why not a universal directory tree

同一盘符可能是 NVMe、HDD、网络盘或不存在；不同 volume 可能属于同一物理设备；package store 可能依赖 hardlink/reflink locality；vendor state 也可能不支持 relocation。固定目录树会把“整齐”误当“正确”。

## Why Documents/HOST_AGENT.md

这是 Human 与 Agent 都容易发现的稳定逻辑入口，并可跨 Windows/macOS/Linux desktop 映射到 OS-native Documents surface；它与底层磁盘拓扑解耦。

## Ownership consequences

ai-use 只拥有通用语义与 discovery contract；platform/profile owner 拥有 OS-specific scanner/reconcile；private instance owner 保存 current observation/resolved mapping；Assets（如存在）继续拥有长期物理事实；secret vault/native store 继续拥有 raw secret。

## Rejected alternatives

1. 统一规定固定路径；2. 所有 state/secret 统一搬入 Host root；3. 每个 AI 客户端复制一份 Host rules；4. 新增硬盘后自动迁移；5. 把 Host Contract 当资产档案或 durable Work SSOT。

## Consequences

优点：新设备可由 Fresh Agent 自主落地；Host 更换磁盘/角色后可以重新解析；语义一致而物理布局适应现场；减少多 AI 客户端重复文明；Host Contract 可作为 local engineering preflight 的稳定输入。代价：Agent 必须具备基本探测/推理能力；platform owner 仍需提供可靠 scanner/adapters；instance observation 需要 currentness/drift discipline。

## Counterexample

一台机器新增高速 SSD。旧式固定模板会直接要求迁移 cache/workspace；本决策只允许触发 re-resolution。若现有布局已满足容量与 locality，则保持原位；只有 material benefit 得到 evidence 支持才迁移。
