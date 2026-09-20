# 双词派单模板

**版本：1.0.0**

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
