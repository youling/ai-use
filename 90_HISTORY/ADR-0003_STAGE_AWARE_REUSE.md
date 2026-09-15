# ADR-0003：Stage-aware Reuse（阶段化复用）

状态：Accepted  
来源 Issue：#62

## Context

“不要重复造轮子”在不同项目阶段不能机械解释成“优先导入现成代码”。

Greenfield 阶段，直接复用成熟 OSS/library/service/protocol 往往能显著降低建造成本；但 AI Coding 使项目更快进入稳定架构甚至生产，同时 native implementation 的代码生产成本显著下降。与此同时，integration、concept count、state reconciliation、migration、testing、recovery、observability 与长期运维成本并没有同比下降。

当项目已经形成自己的 canonical state/lifecycle/authority/identity/contract 后，再引入同类外部 runtime/framework/subsystem，可能在已有轨道旁创建第二套 state machine、queue、DB、session、recovery 或 authority。此时虽然复用了代码，却增加了总系统复杂度。

## Decision

1. 采用 **Stage-aware Reuse**：项目阶段改变时，reuse 默认策略随之改变。
2. Greenfield / Pre-architecture 默认 `REUSE_ARTIFACT_BEFORE_BUILD`。
3. Forming 阶段默认 `REUSE_COMPONENT_BEHIND_EXISTING_SEAM`。
4. Mature 阶段默认 `REUSE_PATTERN_BEFORE_IMPORTING_ARTIFACT`。
5. Production Core 默认 `LEARN_EXTERNAL -> MAP_TO_LOCAL_ARCHITECTURE -> NATIVE_IMPLEMENT`。
6. Mature / Production Core 中，新发现的同类 OSS/framework 默认先视为 `prior art / reference implementation`；优先复用 idea、algorithm、protocol、pattern、failure model、testing strategy 与 implementation technique，而不是直接导入 runtime/code。
7. Mature / Production Core 若要直接引入新的外部 artifact/runtime/framework/subsystem，必须通过 `External Wheel Admission Gate`：
   - 填已有 seam，不创建第二套 state/lifecycle/authority/identity/DB/queue/recovery/observability；
   - 可由现有 adapter/contract 完整包住，上层 canonical semantics 不迁就外部实现；
   - 降低的是 total system complexity，而不只是 LOC；
   - 可替换，不把 external implementation 变成 local authority/SSOT；
   - 长期 integration/migration/testing/operations 成本低于 native implementation。
8. 关键项无法证明时，默认 `REUSE_KNOWLEDGE_NATIVE_IMPLEMENT` 或 `DEFER / REJECT`。
9. 项目阶段按 durable architecture maturity 判断，不按开发时长硬编码。
10. 公共底座不适用“成熟后默认手搓”推论。高度标准化、互操作性与长期审计价值明显高于本地重写收益的成熟基础实现，继续优先复用；尤其不得因 AI Coding 容易而自行重写高风险安全基础设施。
11. Canonical home 为 `docs/ARCHITECT_RECONNAISSANCE.md`；`READING_MAP.md` 负责把 Project/Global Architect 在 mature-project external reuse/import 场景路由到该规则。L0 不扩写。

核心句：

> **项目早期优先复用轮子；项目成熟后优先复用知识。**

> **External maturity != Local architectural fit.**

## Alternatives

### A. 始终坚持“有轮子就直接复用”

未采用。它只优化初期代码量，不约束第二 state/lifecycle/authority 与长期复杂度，成熟系统中容易形成平行轨道。

### B. 成熟后全面禁止第三方代码

未采用。会误伤成熟公共基础库、标准协议实现与安全基础设施，也把本原则错误变成 NIH（Not Invented Here）。

### C. 固定用项目运行天数判定成熟度

未采用。AI Coding 下项目速度差异极大，日历时间不能代表 architecture maturity。成熟度应由 current durable architecture/production evidence 判断。

## Consequences

正向：

- 避免为了“复用轮子”在成熟系统里重复 state/lifecycle/authority；
- 外部调研继续保留价值，但从 dependency hunting 转向 prior-art learning；
- AI Coding 的低实现成本可以用于保持 local architecture 单轨，而不是扩张 glue layer；
- Project/Global Architect 对外部依赖引入拥有明确 admission burden。

代价：

- Mature/Production Core 中可能写更多本地代码；
- Architect/Research 需要理解外部实现机制，而不是只判断“能不能装”；
- 对少数确实适合直接引入的成熟组件，需要额外写清 local fit 与 replaceability 证据。

## Supersedes / Superseded by

不 supersede 既有 reconnaissance；本 ADR 收紧并阶段化其 `REUSE / ADAPT / BUILD` 语义。后续若改变阶段化复用原则，应新增 ADR 或明确 supersede，不改写本历史。