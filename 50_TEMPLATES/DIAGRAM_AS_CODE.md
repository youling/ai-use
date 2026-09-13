# Diagram-as-Code 可复制模板

先读 `../30_PROTOCOLS/DIAGRAM_AS_CODE.md`。下面就是样板；没有适用行就删掉，不留空壳。

## README 首屏放置

```text
# 项目名

1–3 句：它是什么 / 拥有什么 / 不拥有什么

[项目架构总览图 / 总图入口]

当前阶段 / 关键入口 / 下一跳

详细正文……
```

布局口诀：**总图放入口，细图贴对象；入口在 README，图源在附近。**

- 根 README 只放项目级总图/入口；
- 图源默认放 `docs/diagrams/**` 或 semantic owner 对应子系统附近；
- 子系统自己的复杂图放其局部 README/目录，不抬到根 README；
- 不建立脱离 owner 的中央 diagrams 大杂烩或独立 shared 图纸仓。

## 静态架构 / ownership 图

```text
图：Portfolio / Project Architecture
类型：architecture
图源：docs/diagrams/architecture.json
入口：README.md 第一屏（1–3 句项目定位之后）
Authority：DERIVED
Canonical source：README / contracts / registry / exact architecture Issue
回答：谁拥有哪类 truth；主要 capability/data flow；相邻 owner 在哪
边语义：实线 = confirmed primary flow；虚线 = support/reuse candidate
验证：machine validate/render + Architect semantic review
```

适合：跨仓 topology、Project Architecture、ownership map。

## 动态项目状态图

```text
图：Portfolio Status
类型：architecture
图源：docs/diagrams/portfolio-status.json
入口：Portfolio / Project README 的导航区
Authority：DERIVED
Source：current repo README / CURRENT_STATE / latest accepted Issue/PR/report
Verified：2026-09-14
Freshness：LIVE_READ
状态压缩：ACTIVE | BLOCKED | STABLE | EXPERIMENTAL | HOLD | UNKNOWN
规则：无 current read 不继续称 current；无 source pointer 就 UNKNOWN；不生成伪精确百分比
```

适合：项目很多、Human/Architect 需要快速知道“发展到哪里 / 卡在哪里 / 下一 Gate”。

## Lifecycle / 状态机

```text
图：Managed Node Lifecycle
类型：lifecycle
图源：docs/diagrams/node-lifecycle.json
入口：拥有该 lifecycle 的子系统 README
Authority：DERIVED
Canonical source：contracts/FLEET.md
回答：合法状态、转换 gate、异常/退出路径
禁止：从图反向创造新 lifecycle state
```

## Sequence / 调用链

```text
图：Wake → Agent Host → Executor
类型：sequence
图源：docs/diagrams/wake-sequence.json
入口：对应 Execution Fabric / runtime 子系统 README
Authority：DERIVED
Canonical source：exact runtime contract + current implementation
回答：谁先调用谁；在哪一步验证 authority/currentness；失败在哪里返回
禁止：把时序图里的参与者自动解释成 ownership hierarchy
```

## Dataflow / Evidence pipeline

```text
图：Eye → Juece Evidence Flow
类型：dataflow
图源：docs/diagrams/evidence-flow.json
入口：producer/consumer contract 附近的 README / architecture index
Authority：DERIVED
Canonical source：producer/consumer contracts
回答：哪些 artifact/reference 穿过边界；谁保持 canonical truth；哪里发生 transformation
禁止：复制 producer raw truth 到 consumer 形成第二 SSOT
```

## PR / Issue 说明句

```text
本图为 DERIVED navigation/read model；canonical source 仍为 <pointer>。
图源可 Git diff；rendered HTML/SVG/PNG 为可重建 presentation artifact。
总图入口位于 <README pointer>；局部图跟随 semantic owner，不建立中央图纸 SSOT。
本次若图与 canonical source 冲突，以 canonical source 为准并修 diagram drift。
```
