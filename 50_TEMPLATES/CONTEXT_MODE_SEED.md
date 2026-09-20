# Context Mode Seed — Copyable Shape

**版本：1.0.0**

字段/值、组合、fresh/independence/delegation 语义见 [Recovery & Handoff §4–5](../30_PROTOCOLS/RECOVERY_HANDOFF.md#4-work-context-与正交维度)；continuation、repair 与完成门见 [Agent Interface §1.6–1.8](../docs/AGENT_INTERFACE.md#16-same-lineage-default-warm_resume)。本页只给形态，字段值按 canonical contract 填写，无值省略。

## Machine shape

```text
context_policy: <canonical value>
mode: <canonical value>
continuation: <canonical value>
independence: <canonical value>
delegation: <canonical value>
parallelism: <canonical value>
```

## Human seed shape

日常入口：[DISPATCH_PAIR.md](DISPATCH_PAIR.md)。寻址与可选执行意图约束见 [Agent Interface §3](../docs/AGENT_INTERFACE.md#3-default-minimal-agent-seed)。

```text
私仓工单：<owner>/<repo>#<issue>[/<dispatch-comment>]
项目：<project>
情景：<lineage / context intent>
上下文参考：<optional pointers>
执行意图：<optional semantic intent>
```

## 旧入口

旧 machine seam 已迁入协议；旧 provider 命令观察不再作为 live guidance。[冻结 v0.1.0 正文](https://github.com/youling/ai-use/blob/e6de9acdafbc3b9d12802ecf8de25f444074553b/50_TEMPLATES/CONTEXT_MODE_SEED.md) 仅供历史追溯。

<!-- Compatibility anchors; current semantics are linked above. -->
<a id="completion-boundary指针式"></a>
<a id="delegation-缝合subagent"></a>
<a id="durable-before-fragile检查点触发"></a>
<a id="human-facing-位置"></a>
<a id="premature_yield可执行判据"></a>
<a id="provider-适配示例informative--non-normative--freshness-marked"></a>
<a id="上下文模式种子词context-mode-seed"></a>
<a id="使用边界"></a>
<a id="同-lineage-默认与-fresh-触发可复制判据"></a>
<a id="安全与独立性冻结"></a>
<a id="正交语义machine-seam"></a>
