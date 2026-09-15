# Architect Reconnaissance — Canonical L2 Reference

**Classification: L2 Targeted Reference.** 仅在 Fresh/takeover Architect、material new-domain、major capability / architecture pivot、成熟项目拟引入新的外部 framework/runtime/subsystem，或快速变化外部生态可能改变方案时读取。普通 Hot Resume、小 bug、确定性维护默认不触发。

source ruling: `youling/ai-hub#50` comment `5451269968`  
stage-aware reuse: `youling/ai-use#62` / ADR-0003

## 1. 目的与位置

Progressive Context Boot 解决“内部 durable context 当前是什么、我有没有权做”；Architect Reconnaissance 解决“今天外部世界是什么、现有路径今天还是否值得继续”。

固定顺序：

```text
BOOT-1 ADDRESS
BOOT-2 APPLICABLE RULES
BOOT-3 EXECUTION GATE
=> EXECUTION_ALLOWED

ARCH-0 RECONNAISSANCE
  A External Current-State Scan
  B Project / Repo Reconciliation
  C Stage-aware Reuse Decision
=> ARCHITECT_READY
```

`EXECUTION_ALLOWED` 与 `ARCHITECT_READY` 不得合并：前者是 authority/currentness gate，后者是 material architecture readiness。

## 2. 何时必须触发

MUST 触发：

- Fresh / takeover Project Architect 或 Global Architect 接管一个需要实质架构判断的项目/领域；
- material new-domain、major capability 选择或 major architecture pivot；
- 已有 durable core / 生产使用的项目，准备直接引入新的外部 framework/runtime/subsystem 或重型依赖；
- provider/API/toolchain/OSS/protocol 生态快速变化，可能改变架构方向；
- current durable path 出现明显 stale / superseded signal。

默认不触发：ordinary Hot Resume、小 bug、确定性维护、已冻结方案下的窄实现，或已有同 scope 且 live revalidate 后仍 current 的 reconnaissance。不设固定 freshness TTL，也不按项目运行天数机械判定成熟度。

## 3. ARCH-0A — External Current-State Scan

**先建立 current external frame，再读项目实现做方案判断。**

来源优先级：official docs/API/spec -> upstream/maintained GitHub repo -> maintained OSS/primary technical sources -> 必要时高质量社区实践。

Targeted 回答：

- 当前主流 capability / pattern 是什么；
- 是否已有可直接 `REUSE` / `ADAPT` 的 library/service/protocol/tool；
- 真正值得带走的是 artifact/runtime，稳定 protocol/interface，还是 algorithm/pattern/implementation technique；
- 是否有新增、deprecated、license/platform constraint 或 API/toolchain 变化会改变架构选择；
- 哪些旧 durable assumption 必须标记 `stale` / `uncertain`。

快速变化事实不得仅凭模型记忆判定 current。外部来源只是 evidence，不是 authority。

**调研目标不是最大化依赖数量。** Greenfield 可以广泛寻找可复用 artifact；成熟项目调研外部代码时，默认也要把它当 `prior art / reference implementation` 阅读，提取 problem framing、状态机、算法、retry/fencing、failure handling、protocol、测试策略等知识，而不是自动升级为 dependency candidate。

## 4. ARCH-0B — Project / Repo Reconciliation

完成 ARCH-0A 后，再读取目标项目 current durable code/docs/Issues/PRs/active graph，并逐项分类：

- `KEEP`：现有实现仍合理；
- `REUSE_ARTIFACT`：直接复用外部 artifact/runtime；
- `ADAPT_BEHIND_SEAM`：外部组件可被 existing local contract/adapter 完整包住；
- `REUSE_KNOWLEDGE_NATIVE_IMPLEMENT`：复用外部知识/算法/pattern/实现方式，在当前 local architecture 内原生实现；
- `BUILD`：project-local 独特约束使本地实现更合理；
- `SUPERSEDED / DEPRECATE`：历史路径停止投入；
- `DEFER / REJECT`：暂缓或拒绝；
- `UNKNOWN`：证据不足，需 targeted Research。

必须显式找 architecture delta：外部 current frame 与 repo 当前实现哪里一致、哪里漂移，以及引入外部 artifact 会不会创建第二套语义轨道。

反模式：因“已有 OSS”机械禁止自研；因 star 多/项目成熟就默认 local fit；用“少写多少 LOC”代替 total system complexity；为了接外部轮子，在已有 state/lifecycle/authority/identity/DB/queue/recovery 旁再铺一套并行轨道；把 transient provider fact 写成永久 governance。

## 5. ARCH-0C — Stage-aware Reuse

核心原则：

> **项目早期优先复用轮子；项目成熟后优先复用知识。**

> **早期让优秀外部轮子帮助铺轨；轨道形成以后，外部轮子必须适应本项目轨距，而不是为了装上新轮子再铺一条铁路。**

AI Coding 降低了 native implementation 的代码生产成本，但 integration、concept count、state reconciliation、migration、testing、recovery、observability 与长期运维成本并未同比下降。成熟项目的 reuse 目标必须从“少写代码”切换为“降低总系统复杂度”。

### 5.1 阶段按架构成熟度判断

- `GREENFIELD / PRE_ARCHITECTURE`：核心模型与 seam 尚未形成；
- `FORMING`：已有主要 contract/模块，但边界仍快速收敛；
- `MATURE`：核心 state/lifecycle/authority/identity/contract 已稳定，已有多个消费者、回归或恢复经验；
- `PRODUCTION_CORE`：关键路径已进入真实生产/业务/设备执行，替换会产生明显迁移与运行风险。

成熟度信号包括 canonical schema/state machine、稳定 ownership/authority、被多个模块消费的 contract、真实 production workflow、回归测试、Incident/recovery 历史与长期兼容责任。由 Architect 基于 current durable evidence 裁决，不设按天数的自动阈值。

### 5.2 阶段化默认

```text
GREENFIELD / PRE_ARCHITECTURE
=> REUSE_ARTIFACT_BEFORE_BUILD

FORMING
=> REUSE_COMPONENT_BEHIND_EXISTING_SEAM

MATURE
=> REUSE_PATTERN_BEFORE_IMPORTING_ARTIFACT

PRODUCTION_CORE
=> LEARN_EXTERNAL -> MAP_TO_LOCAL_ARCHITECTURE -> NATIVE_IMPLEMENT
```

进入 `MATURE / PRODUCTION_CORE` 后，新发现的同类 OSS/framework 默认先视为 **prior art / reference implementation**。默认复用 idea、algorithm、protocol、pattern、failure model、testing strategy、implementation technique；与本项目核心语义/控制平面强耦合的能力，默认在现有 seam 内 native implement。

**直接复制/引入代码、runtime 或完整 subsystem 不再是默认动作，必须通过 External Wheel Admission Gate。** 这不是第三方代码禁令，而是改变 mature core 的默认举证责任。

### 5.3 External Wheel Admission Gate

`MATURE / PRODUCTION_CORE` 若仍要直接引入新的外部 artifact/runtime/framework/subsystem，Architect 必须在 durable decision 中证明：

1. `Existing seam fit`：填已有 seam，不创建第二套 state/lifecycle/authority/identity/DB/queue/recovery/observability；
2. `Containment`：可由现有 adapter/contract 包住，上层 canonical semantics 不迁就外部实现；
3. `Total complexity`：降低的是 total system complexity，不只是 LOC / 初期编码时间；
4. `Replaceability`：停更/API 漂移/移除时可替换，不把 external implementation 变成 local authority/SSOT；
5. `Lifecycle economics`：相对 native implementation，长期 integration/migration/testing/operations 成本确实更低。

关键项无法证明时，默认 `REUSE_KNOWLEDGE_NATIVE_IMPLEMENT` 或 `DEFER / REJECT`。不得为了“复用轮子”本身破坏已有 canonical track。

### 5.4 公共底座例外

不得滑向“什么都手搓”。高度标准化、互操作性/长期审计价值明显高于本地重写收益的公共底座，若存在成熟维护实现，默认继续复用，例如密码学/TLS、数据库驱动、标准协议栈、成熟 parser/codec/compression、安全认证基础库。尤其不得因“AI 能写”自行重写高风险安全基础设施。

本 Gate 主要约束项目核心领域语义、控制平面、状态机、authority/lifecycle、持久化真值、执行编排等与 local architecture 强耦合的外部实现。

## 6. ARCH-0D — Durable output

输出低频、简洁的 `ARCHITECT_RECONNAISSANCE_REPORT`。它是 architecture input / alignment artifact，不是 authority source，也不是文献综述。

最低 schema：

```text
ARCHITECT_RECONNAISSANCE_REPORT
---
as_of: <evidence window>
scope: <architecture/domain scope>
project_stage: GREENFIELD | FORMING | MATURE | PRODUCTION_CORE
reuse_mode: <stage-aware default + rationale>
external_current_state: <capability/pattern summary + refs>
reuse_candidates: <candidate + decision rationale>
external_wheel_admission: <not_applicable | PASS + evidence | FAIL + reason>
architecture_delta: <external frame vs current repo>
decisions: KEEP | REUSE_ARTIFACT | ADAPT_BEHIND_SEAM | REUSE_KNOWLEDGE_NATIVE_IMPLEMENT | BUILD | SUPERSEDE | DEFER | REJECT
parallel_track_risk: <none | second state/lifecycle/authority/etc. risk>
do_not_build / deprecated_paths: <paths to avoid>
open_questions: <remaining uncertainty>
targeted_research_needed: <none | narrow questions>
first_architecture_direction: <first material work direction>
```

## 7. Reuse / freshness

旧 reconnaissance 可复用的条件：scope 实质相同、关键 source 仍 current、live revalidation 无 material external change、repo architecture 无推翻旧结论的新 drift，且 project stage/reuse mode 没发生足以改变 admission burden 的变化。

阶段变化本身是 architecture delta。Greenfield 阶段曾经合理的 `REUSE_ARTIFACT` 决策，不会自动成为成熟阶段继续引入相似新依赖的先例。

## 8. 与 Research Agent 的关系

Architect reconnaissance 负责 current-state alignment、stage-aware reuse/build boundary 和研究问题切分；不要求 Architect 自己研究到底。

```text
Architect reconnaissance
-> freeze narrow discriminator/question
-> Fresh Research Agent
-> durable findings/evidence
-> Architect reconcile/update architecture
```

Research Agent 不因 findings 获得 Architect authority。成熟项目的 Research Agent 可以深入阅读外部代码，但输出优先为机制、算法、pattern、failure model、protocol、可移植技术点与引用位置；除非 Work Order 明确要求 External Wheel Admission Gate，否则不得把“发现可用代码”直接升级为“应导入依赖”。

## 9. Must preserve

- GitHub durable SSOT / Progressive Context Boot；
- `Capability != Authority` 与 Human sovereignty；
- external current evidence != authority；
- **External maturity != Local architectural fit**；
- mature core 默认 Knowledge Reuse，artifact/runtime import 需要 architecture admission；
- 不做 full-Internet crawl / literature-review ceremony；
- 不设 fixed freshness TTL / heartbeat；
- 不创建 search DB/vector store/knowledge graph；
- 不把 web/search output 自动视为可信事实；
- 不因有开源方案机械禁止 BUILD；
- 不因 AI Coding 容易而机械禁止成熟公共基础库；
- secrets/private topology 不进入 public research query / durable public docs；
- 不改变 Runner lifecycle、merge/deploy/destructive authority。
