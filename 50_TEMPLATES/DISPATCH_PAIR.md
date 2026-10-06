# 双词派单模板

**版本：1.1.0**

Human Card / Seed、运行位置、最小化与 transport fallback 的语义由 [Agent Interface §2–3](../docs/AGENT_INTERFACE.md#2-human-dispatch-card) 定义。复制对应形态并替换占位符；可选行无值即省略。所有坐标是 inert placeholders，不指向实际实例。

## 人类派发卡

```text
任务：<task name and durable coordinate>
为什么做：<reason from current Work Order>
你要做什么：<authorized task summary>
运行位置：<current scheduling choice>
本轮终点：<pointer to current acceptance / stop boundary>
```

## 网页端

```text
公仓工单：<owner>/<repo>#<issue>[/<dispatch-comment>]
项目：<project>
情景：<read-only research scenario>
上下文参考：<current evidence pointer>
```

## 云端电脑

```text
私仓工单：<owner>/<repo>#<issue>[/<dispatch-comment>]
项目：<project>
情景：<isolated build scenario>
上下文参考：<current implementation lineage pointer>
```

## 本地

```text
私仓工单：<owner>/<repo>#<issue>[/<dispatch-comment>]
节点：<node_id>
项目：<project>
情景：<local environment scenario>
上下文参考：<current acceptance pointer>
```

## 本地+设备

```text
私仓工单：<owner>/<repo>#<issue>[/<dispatch-comment>]
节点：<node_id>
项目：<project>
情景：<device validation scenario>
上下文参考：<current device work pointer>
```

## 上下文模式（可选）

Machine 字段形态见 [CONTEXT_MODE_SEED.md](CONTEXT_MODE_SEED.md)，值与语义见 [Recovery & Handoff](../30_PROTOCOLS/RECOVERY_HANDOFF.md#4-work-context-与正交维度)。

```text
执行意图：<optional mode/context intent>
```

## 工头任务合同与阶段裁决补充

以下是 [异步主工头指南](../40_GUIDES/ASYNC_FOREMEN.md) 的可选形态，填写在现有 Work / durable dispatch / checkpoint 内；不是短 Seed 的新增必填键。派单和停止语义仍以 [Agent Interface](../docs/AGENT_INTERFACE.md) 为准，子对话 ownership 以 [Recovery & Handoff](../30_PROTOCOLS/RECOVERY_HANDOFF.md#5-durable-before-fragile-与-delegation) 为准。

### Durable dispatch 的任务合同补充

```text
问题：<本轮要消除的未知；输入的 namespace / 版本 / 时间范围>
验收与本轮终点：<existing Work acceptance；有界证据 / 可审阅 PR；继续的真实依赖>
授权范围：<current authority pointer；已授权动作；明确嵌套委派时才开启子对话>
主责与写域：<primary owner；隔离工作区；允许写的对象 / branch>
冲突对象与依赖：<共享账号 / 进程 / 文件 / 浏览器 / 设备；当前 owner / lease；前置>
来源与当前性：<exact source/ref/hash；完整技术单元或字段范围；投影与未读缺口>
拆分与交付：<独立方向；原生子返回形状；语义阶段回写；需升级架构师的确切问题>
```

### 阶段交付

沿用 [Durable Trace](../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md#阶段性-checkpoint) 的现有事件。语义 delta、owner、证据范围可以写入 `completed`，依赖写入 `remaining / blockers`；不另立平行的状态源。

```text
PROGRESS_CHECKPOINT
---
work: <owner/repo#issue@step>
phase: <语义阶段>
recoverability: REMOTE | LOCAL_ONLY
completed: <本阶段新增事实；主责；证据范围；原失败保持>
durable_refs: <exact PR / head / report / proof pointers>
verification: <完整性与语义核验；已做 / 未做 / 不适用>
remaining: <仍未知或未覆盖部分；真实依赖>
blockers: <none 或确切冲突 / gate>
next: <一个具体动作；本轮已达终点则转 canonical terminal writeback>
```

### 架构师消费与裁决

裁决写回现有 Work / PR，以下是人能读的说明字段，不是 machine event 或新的 approval gate。裁决前 live-read terminal pointer、Work 和对应 exact head；完成语义仍遵循 [Agent Interface §1.8](../docs/AGENT_INTERFACE.md#18-completion-boundarydurable-acceptance--terminal-writeback)。

```text
交付依据：<terminal / checkpoint pointer；已核对的 exact head>
接受：<哪些结论、在哪个 namespace / 来源 / 运行 / capability 层成立>
拒绝或限定：<过强结论及其证据范围；不改写原失败>
未知与依赖：<确切缺口；是否改变下一步>
下一步：<责任 owner；沿用原 scope 续接 / 独立新任务 / 等待真实 gate / 有限收尾>
```

已有 finite acceptance 满足后，“等待架构师”可记录为 `next` 的说明；它不替代 `AGENT_TERMINAL_RESULT` / readback，也不免除尚可合法修复的工作。最终 delegated chat 返回继续只包含 exact terminal GitHub pointer。只有获得独立 child Work delegation 的子对话才承担该 Work 的关闭义务；只读证据子对话由主工头综合并关闭主 attempt。

<!-- Compatibility anchors; current semantics are linked above. -->
<a id="agent-seed-最小化规则"></a>
<a id="agent-种子词"></a>
<a id="agent-种子词-1"></a>
<a id="agent-种子词-2"></a>
<a id="agent-种子词-3"></a>
<a id="上下文模式可选-pointer"></a>
<a id="人类派发卡-1"></a>
<a id="人类派发卡-2"></a>
<a id="人类派发卡-3"></a>
<a id="使用边界"></a>
