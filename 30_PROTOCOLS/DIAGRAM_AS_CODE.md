# Diagram-as-Code 与架构拓扑导航

**Classification: L2 Targeted Reference**  
**Protocol Version: 0.2.0**  
**Source Issues:** `youling/ai-use#53`, `youling/ai-use#55`

本协议定义：什么时候值得维护架构图、图拥有什么 authority、图放在哪里、动态图如何处理 currentness，以及 Agent 怎样把图当作导航而不是第二 SSOT。

核心句：

> **图不是 SSOT；图是 SSOT 的索引、投影与导航。**

布局口诀：

> **总图放入口，细图贴对象；入口在 README，图源在附近。**

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

## 6. 四类 currentness 标记

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

## 7. 图作为 Agent Routing Index

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

## 8. Diagram lifecycle = Artifact lifecycle

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

## 9. Renderer / compiler 是工具，不是 authority

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

机械 validate 与语义 Review 分工：

```text
renderer validator
= schema / geometry / readability / deterministic output

Architect Review
= ownership / authority / currentness / semantic correctness
```

若没有真实 browser/perceptual evidence，不得把 deterministic render PASS 写成“Human 视觉已验收”。

---

## 10. 建议的 drill-down 层级

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

---

## 11. 最小维护契约

新增/维护重要 diagram 时至少回答：

```text
图在回答什么问题？
图源在哪里？
根/局部 README 的入口在哪里？
canonical source 在哪里？
图是 CANONICAL / DERIVED / HISTORICAL / STALE_OR_UNKNOWN 中哪一类？
哪些 node/edge 是 hard dependency，哪些只是 support/reuse candidate？
动态内容如何判断 freshness？
坏图如何重建/回滚？
```

需要可复制形态时读：

`50_TEMPLATES/DIAGRAM_AS_CODE.md`

模板只是形态；本协议才是语义。
