# Diagram-as-Code 与架构拓扑导航

**Classification: L2 Targeted Reference**  
**Protocol Version: 0.5.0**

**Source Issues:** `youling/ai-use#53`, `youling/ai-use#55`, `youling/ai-use#57`, `youling/ai-use#67`

本协议定义：什么时候值得维护架构图、图拥有什么 authority、图放在哪里、动态图如何处理 currentness，以及 Agent 怎样把图当作导航而不是第二 SSOT。

核心句：

> **图不是 SSOT；图是 SSOT 的索引、投影与导航。**

布局口诀：

> **总图放入口，细图贴对象；入口在 README，图源在附近。**

复杂度口诀：

> **规模不是删信息的理由；规模变大，优先增加层级、区域与下钻。**

---

## 1. 为什么需要 Diagram-as-Code

当项目规模变大，纯 prose 会出现两个成本：

1. Human 很难一眼看出 ownership、依赖、当前 gate；
2. Fresh Architect / Agent 容易只读局部仓库，然后重新实现邻接项目已经拥有的通用能力。

Diagram-as-Code 的目标不是“把文档画漂亮”，而是把复杂结构压缩成**机器可读、Human 可视、Git 可 diff、可回到 source pointer 的导航层**。

---

## 2. 什么时候需要图

以下任一条件成立时，Project Architect / Global Architect 应明确判断是否需要 diagram/navigation view；若同时命中多项，默认应维护：

- 跨 **3 个或以上独立 owner / domain / repo**；
- authority / ownership / SSOT 边界难以仅靠短表说明；
- 存在非线性 lifecycle、retry、rollback、approval、多个 gate；
- 存在复杂 dataflow / evidence lineage / request sequence；
- Fresh Agent 已出现或高度可能出现重复造轮、错误 owner、错误 mandatory-hop；
- Human 需要快速判断“各方向发展到哪里 / 卡在哪里 / 下一 Gate”；
- 架构改动需要在 PR review 中快速比较 before / after。

普通单文件、小工具、线性 CRUD、小范围 bugfix **不因为本协议强制配图**。

---

## 3. 先选表达结构，不要所有东西都画成拓扑

| 问题 | 首选图形语法 |
| --- | --- |
| 系统 / repo / ownership / capability / dependency | `architecture` / topology |
| 工作流 / 审批 / runbook / branching | `workflow` |
| Agent / API / service 的调用先后 | `sequence` |
| Evidence / data / transformation pipeline | `dataflow` |
| lifecycle / wait / retry / terminal state | `lifecycle` / state machine |
| 数值趋势 / 分布 /比较 | chart；不属于本协议的 topology 默认面 |
| 时间演化 /事件 | timeline；不要硬塞成 architecture graph |

总拓扑可以作为导航骨架，但局部视图应使用最适合的信息结构。

### 3.1 阶段性进展图示与领域边界复盘

**Human 裁决：对实质性架构工作，阶段总结应图示化，让架构师不得不说明“这个系统由哪些责任域组成、哪些关系已经成立、阶段之间到底改变了什么”。** 绘图是推理与质量控制，不是装饰性汇报或可替代验收的自动证明。

**触发**：Project/Global Architect 在重要领域/模块划分、跨系统集成、接口/依赖决策、阶段实质交付、架构 Review/接续时，**MUST** 在该阶段现有 GitHub Work / PR / durable checkpoint 中给出可追溯的阶段图示结果。选择 `CREATE | UPDATE | REUSE_CURRENT`：

- `CREATE`：此前没有能表达该阶段问题的有效图源，画最小当前视图；
- `UPDATE`：已有图源，但本阶段改变了 domain、owner、数据流、依赖或 gate，更新图源并能看出差异；
- `REUSE_CURRENT`：架构/拓扑仍成立，不为每次总结重复绘图；引用当前仍有效的源图，并用简短、来源支持的 delta / gate 说明本阶段发生了什么、没发生什么。

**注意**：普通单文件 bugfix、简单线性任务、没有材料性架构变化的例行执行不为本条强制新建图。可以 `NOT_APPLICABLE` 加简短理由；不把所有 Foreman 的常规 checkpoint 都变成一份工程架构演示文稿。阶段 summary 仍可按当前 Durable Trace 事件的 `durable_refs` 引用图源/状态摘要，**不增加新事件或审批状态**。

**适用时的最低内容**（可以是同一张图与旁边的几句说明，避免第二份复制文档）：

1. **是什么**：图的阅读任务、所属 owner/domain、canonical source 与实际图源位置；
2. **怎么分**：责任/领域边界、状态归属、接口，以及方向明确的关键依赖/数据流。关系边应能区分 confirmed、candidate、blocked/unknown；
3. **进展了什么**：指明相对于上阶段的新增/移除/变更节点与关系、受影响的 Work/PR/exact revision、哪些是真实验证、哪些只是一份方案；
4. **还差什么**：未验证边界、真实依赖、阻断及下一步最短可执行动作；
5. **当前吗**：`DERIVED` 状态、`source_pointer`、`verified_at`/窗口及 freshness；过期图不能写成当前成功，未知数据必须标 `UNKNOWN`。

**不是每个问题都用模块拓扑回答。** 领域/依赖选择 architecture 或 dependency view；一次请求链看 sequence；证据和转化链看 dataflow；状态转换看 lifecycle；纯时间推进看 timeline/状态 overlay。复杂阶段可用一个总图入口、多个局部下钻，不把业务模块、运行节点、PR、Issue 混成同一层的“模块”。

**先诊断图暴露的工程问题，再排版：** 如果画不清领域边界、谁写状态、接口在哪、哪个箭头逆向依赖、候选事实何时变成已验收事实，应回到 [软件架构与工程实践](SOFTWARE_ARCHITECTURE_PRACTICE.md) 复核职责划分和变化边界。图能画出来并不保证分解正确；渲染成功也不代表代码、权限或跨域契约已经通过。不能为保持图的整洁隐去冲突、失败、双写或未解决依赖。

当本阶段还没有足够来源可支持完整图时，展示**有边界的局部结构并显式标 `UNKNOWN`**，或引用上一次 current 图并声明本阶段证据缺口；不能因为工具不支持精美绘制就伪造完成，也不能无限制阻塞其他合法施工。低依赖首选 Mermaid/文本 DSL，格式与存放位置沿用本协议 §4–§5。

可复制的图示复盘形态与反例见 [Diagram-as-Code 模板](../50_TEMPLATES/DIAGRAM_AS_CODE.md#阶段性架构复盘图示)。

---

## 4. Source 与 Authority

重要架构图必须保留机器可读、Git 可 diff 的 source。

允许：

```text
Mermaid source
Typed JSON IR
Graphviz/DOT
其它稳定文本 DSL
```

PNG / JPG / screenshot 可以作为：

```text
presentation
visual evidence
review attachment
```

但不能是唯一长期 source。

默认 authority：

```text
repo-local contract / registry / current Issue / canonical doc
        = CANONICAL

diagram source / topology / status overlay
        = DERIVED

HTML / SVG / PNG render
        = DERIVED PRESENTATION
```

如果图与 canonical source 冲突：

1. canonical source 优先；
2. 记为 diagram/topology drift；
3. 修图；
4. 不得为了让图“继续正确”反向修改事实 authority。

### 4.1 共享派生解释边界

当 index、snapshot、graph/navigation view 与 diagram 描述同一 domain 时，它们 SHOULD 消费同一个 **reviewed normalized interpretation boundary**，或在所声称 domain/query 范围内证明 semantic equivalence。共享边界解释 canonical identity、field、relation 与 derivation；不因它被共享就获得 owner 的 authority，也不要求采用统一数据库或 renderer。

`renderer schema != domain ontology authority`：渲染所需的节点/边字段不能反向规定业务实体与关系的含义。diagram 默认仍为 DERIVED；只有 explicit owner contract 指定的部分才可具有 canonical 身份，不能从 typed schema 或成功 render 推导。

多个派生面不一致时，按 derivation defect 回到 canonical source、source revision 和 interpreter version 排查，修复解释或生成 drift；不能选择最漂亮、最快或成功渲染的一面作为真相。current-read 与旧 snapshot/new target 的证明要求见 [Durable Data Doctrine](../docs/DURABLE_DATA_DOCTRINE.md#8-current-read--derived-freshness)。

---

## 5. 图放在哪里：总图放入口，细图贴对象

图的**入口位置**和**机器图源位置**不是一回事。

### 5.1 普通项目根 README

根 `README.md` 是 Human / Fresh Architect / Fresh Agent 的第一导航面。复杂项目默认把总图或总图入口放在第一屏，推荐顺序：

```text
# 项目名

1–3 句：它是什么 / 拥有什么 / 不拥有什么

[项目架构总览图 / 总图入口]

当前阶段 / 关键入口 / 下一跳

详细正文……
```

因此：

- 不建议把图直接放在项目名之前；先给读者最小定位；
- 不建议把总图藏在长篇 README 末尾；地图必须在详细正文之前；
- README 内联 Mermaid、SVG/PNG 或指向 richer navigator 的链接都可以，但它们仍是 `DERIVED` navigation；
- 根 README 不要求承载所有局部图，只负责“我在哪里、旁边是谁、下一跳去哪”。

### 5.2 图源跟随 semantic owner

机器可读图源不必堆在仓库根目录。默认：

```text
docs/diagrams/**
```

或跟随拥有该语义的子系统：

```text
subsystem/
  README.md
  diagrams/
    ...
```

原则：**谁拥有这个语义，图就跟谁走。**

不要为了集中管理图形建立脱离 domain owner 的中央大杂烩：

```text
/diagrams/fleet.*
/diagrams/kefu.*
/diagrams/juece.*
/diagrams/everything.*
```

也不要仅因为多个项目都有图就新建独立 `shared/common/diagram` 仓。跨项目总图属于 portfolio/control-plane navigation；项目内部图仍留在项目 owner 附近。

### 5.3 复杂子系统逐层下钻

当项目内部已经出现独立复杂子域，局部 `README.md` 应承担局部地图入口：

```text
repo/README.md
  -> 项目总图

repo/subsystem/README.md
  -> 子系统总图

repo/subsystem/feature/README.md
  -> 仅在确有必要时放更细的 workflow / sequence / lifecycle
```

过细实现图不要抬到根 README；它只在相关对象附近存在，并由上一级地图用 pointer 下钻。

### 5.4 ai-hub 特例

`ai-hub` 同时是自己的项目，也是 Youling cross-project control / information exchange surface，因此：

```text
ai-hub 根 README
= Portfolio 世界地图 / 舰桥入口优先

ai-hub 自身 Execution Fabric / Console / Agent Host 等内部结构
= docs/ 或对应模块继续下钻
```

这不让 `ai-hub` 获得其它 repo 的事实 authority；它只承担 portfolio navigation/read-model 的入口职责。

---

## 6. 规模、可读性与语义复杂度必须分开判断

不要把“图很大”“默认屏幕看不清”“语义关系太复杂”混成同一个问题。维护重要 diagram 时至少区分三个尺度：

| 尺度 | 它回答什么 | 常见证据 |
| --- | --- | --- |
| **Render scale** | renderer / browser 能否稳定承载、交互和导出该规模 | benchmark、stress fixture、真实大图测试、内存/渲染/交互证据 |
| **Default-view readability** | Human 第一次打开时能否看清主要结构和文字 | projected text、viewport、overlap、crossing、route/label clearance、真实浏览器视觉证据 |
| **Semantic complexity** | 是否把太多不同层级、不同问题的关系塞进同一张图 | owner/domain 数、关系类型、跨区 edge、阅读任务是否混杂、是否需要 drill-down |

三者彼此相关，但不能互相替代。

### 6.1 Quality gate 失败不等于 renderer capacity 失败

机械 validator 可能因为以下原因拒绝一张图：

```text
text projected too small
edge-through-node
proper crossing
ambiguous shared corridor
label / route clearance
container / legend collision
route rhythm
```

这些默认属于**图形质量 / 默认可读性问题**。除非有明确的容量、性能、崩溃或 benchmark 证据，不得把它们写成：

```text
“节点太多，renderer 扛不住”
“项目太复杂，所以工具无法绘制”
```

同理，一个小节点数的图也可能因为线路设计差、长文案、默认缩放过小而失败；一个大节点数的图也可能通过分区、分层、zoom/radar/focus 等导航机制保持可用。

### 6.2 正确修复顺序：先保语义，再修呈现

当图触发 readability / geometry gate 时，默认按以下顺序处理：

```text
1. 判断：这是语义问题、默认视图问题，还是 renderer capacity 问题？
2. 若混入不同阅读任务：拆成上/下层或独立视图；
3. 若同层仍复杂：按 domain / lane / region / subgraph 分区；
4. 调整 edge route / port / corridor / label placement；
5. 缩短节点 copy，把细节放 inspector / card / pointer；
6. 必要时调整画布与节点尺寸；
7. 最后才考虑删减信息，而且只能删重复 presentation，不得删掉真实关键语义。
```

禁止为了“过 validator”默认采取：

```text
无限缩小字号
把所有节点挤进一屏
删除关键 dependency / ownership edge
把多个不同语义 relation 合并成一条含糊线
让总图复制所有下层细节
```

核心原则：

> **复杂度应被导航结构吸收，而不是被字号和像素压扁。**

### 6.3 分层不是固定节点数阈值

本协议不规定“一张图最多 N 个节点”。节点数本身不能决定是否拆图。

应拆层/拆区的信号是：

- 一张图同时回答多个不同层级的问题；
- Human 必须反复 zoom 才能识别入口级结构；
- 跨区关系大量穿过无关节点或共用 corridor；
- 节点主要空间被解释性小字占据，而非结构本身；
- Reader 需要先理解几十条次要边，才能找到主要 path；
- Fresh Agent 无法从当前图稳定判断“下一跳读哪个 owner/source”。

同一层内部也可以有 region/subgraph；分层与分区可以同时使用。

### 6.4 大图能力必须有 evidence，不能从 feature 名推断

`pan / zoom / radar / focus / semantic lens / reading depth` 等能力说明 renderer 具备大图导航基础设施，但**不自动证明**它已经通过某个节点规模的 benchmark。

因此：

```text
有明确 100 / 1000-node benchmark -> 可以引用该 evidence
只有 pan/zoom/radar 功能 -> 只能说具备大图浏览机制
没有 benchmark -> 不声称已验证某个规模上限
```

`showcase PASS` 只证明当前 artifact 通过对应机械质量门；它既不证明架构语义正确，也不证明 renderer 已通过更大规模 stress test。

### 6.5 Youling dogfood 规则

Youling 在真实 diagram dogfood 中，如果 validator 拦截图，应把失败记录解释为具体诊断类别，而不是笼统写“图太复杂”。例如：

```text
READABILITY_FAIL
ROUTING_FAIL
LABEL_CLEARANCE_FAIL
SEMANTIC_LAYERING_FAIL
RENDER_CAPACITY_FAIL   # 仅在真实容量/性能证据成立时使用
```

若修复方式是增加 Project / Work / Delivery 下钻，则这属于**复杂度治理成功**，不是“为了迁就 renderer 删除系统信息”。

---

## 7. 四类 currentness 标记

动态图 / status overlay 至少能区分：

```text
CANONICAL
DERIVED
HISTORICAL
STALE_OR_UNKNOWN
```

其中动态进度图必须保留：

```text
source_pointer
verified_at / verified window
freshness / stale signal
```

规则：

- 没有本轮 current source read，不能把旧 snapshot 默认为 current；
- source 本身已过期时显式 stale/hold；
- “没读到” != “没有进展”；证据不足就 UNKNOWN；
- 不生成伪精确完成百分比，除非 owner project 自己定义了可审计 milestone metric。

Dynamic status 只是 navigation compression，不能建立新的全局 lifecycle enum 来覆盖各项目状态机。

---

## 8. 图作为 Agent Routing Index

Fresh Architect / Agent 使用图的正确方式：

```text
图上发现相关 node / edge
        ↓
确定 owner / semantic edge type
        ↓
读取 exact source pointer
        ↓
进入 target-local current contract / Issue / registry
```

错误方式：

```text
看到总图
  -> 把整张图当真相
  -> 递归读取所有仓库
```

图的任务是**缩小下一跳**，不是扩大默认上下文。

尤其新增 generic primitive 前，应先通过 topology/navigation 检查潜在 owner，再执行 reuse-before-build：

```text
find owner
-> live-read owner contract
-> compare semantics / invariants
-> pointer / contract / adapter reuse
-> 只有真实缺口才讨论新的 shared capability
```

同样都叫 `graph / relation / belief / state` 不代表同一个 schema。

---

## 9. Diagram lifecycle = Artifact lifecycle

本协议不创建第二套 Git 流程。

统一使用 `30_PROTOCOLS/CHANGE_LIFECYCLE.md`：

### 架构语义随图一起改变

如果 diagram source 的变化实际改变：

- ownership；
- authority；
- schema；
- cross-project contract；
- lifecycle；
- 长期架构边界；

则按对应 L1/L2 与 canonical architecture change **同一个 Issue / PR / ADR** 留痕。不要只改图，不改 authority source；也不要只改 prose，让图长期漂移。

### 低关键 derived 图

状态总览、导航 view、周期 summary 等可以采用 `PERIODIC_DOCS` 批量刷新。

一旦刷新过程发现它不是“同步现状”，而是在重新定义现状，立即升级 L1/L2。

---

## 10. Renderer / compiler 是工具，不是 authority

工具可以负责：

- schema validation；
- route / overlap / readability lint；
- deterministic render；
- interactive navigation；
- before/after delta；
- export HTML/SVG/PNG。

工具不能因为“成功渲染”就证明图中语义正确。

当前 Youling 已验证：

```text
Mermaid
= 低依赖、内联、cold-start 友好

Archify
= typed IR + deterministic validate/deliver 的 richer diagram compiler / navigator
```

`Archify` 是当前已 dogfood 的优先工具之一，不是 ai-use kernel dependency，也不是全项目强制 runtime。使用外部 renderer 时应 pin version/commit；自动更新不得静默改变历史 artifact 编译结果。

机械 validate、语义 Review、规模 benchmark 分工：

```text
renderer validator
= schema / geometry / readability / deterministic output

Architect Review
= ownership / authority / currentness / semantic correctness

scale benchmark / stress evidence
= renderer 在特定规模、环境和交互条件下的容量证据
```

三者不能互相冒充。

若没有真实 browser/perceptual evidence，不得把 deterministic render PASS 写成“Human 视觉已验收”。若没有明确 stress/benchmark evidence，也不得从“支持 zoom/radar”推导出“已验证 N 个节点”。

---

## 11. 建议的 drill-down 层级

复杂 portfolio 可逐层展开：

```text
L0 Portfolio
  repo / owner / capability / major flow
        ↓
L1 Project
  phase / canonical surfaces / adjacent owners
        ↓
L2 Program / Work Graph
  Issue / dependency / gate / owner
        ↓
L3 Delivery
  PR / exact head / review / tests / evidence
        ↓
L4 Implementation
  file / module / class / function / typed interface
```

每层应尽量保存 pointer，而不是复制下一层全文。

同一 domain 的图与 index/query 也应优先提供 bounded drill-down，而不是把每条 record/node 都塞进默认图；完整信息保留在可追溯 source 与下钻面中。

这不是固定深度限制。若某层内部仍然复杂，可以先按 domain / region / lane / subgraph 继续组织；如果阅读任务发生变化，再增加下一层。原则是：

> **先按问题分层，再按同层结构分区。**

---

## 12. 最小维护契约

新增/维护重要 diagram 时至少回答：

```text
图在回答什么问题？
图源在哪里？
根/局部 README 的入口在哪里？
canonical source 在哪里？
图是 CANONICAL / DERIVED / HISTORICAL / STALE_OR_UNKNOWN 中哪一类？
哪些 node/edge 是 hard dependency，哪些只是 support/reuse candidate？
动态内容如何判断 freshness？
当前复杂度属于 render scale / default-view readability / semantic complexity 哪一类？
若图变复杂，下一层 / region / subgraph 在哪里？
validator PASS 能证明什么、不能证明什么？
坏图如何重建/回滚？
```

需要可复制形态时读：

`50_TEMPLATES/DIAGRAM_AS_CODE.md`

模板只是形态；本协议才是语义。
