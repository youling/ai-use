# Capability Self Check — Evidence Shape

**版本：1.0.0**

必要能力检查的适用性、检查内容与结论边界见 [Bootstrap §4](../10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md#4-targeted-capability-preflight)。本模板只提供请求和报告形态。

```text
CAPABILITY_SELF_CHECK
---
scope: <current work pointer / node identity>
depth: <requested inspection scope>
```

```text
CAPABILITY_SELF_CHECK_REPORT
---
identity: <node_id>/<agent_type>/<session_id>
runtime: <observed model/version>
tools: <observed tools and relevant versions>
auth: <observed authentication state, no credentials>
access: <target coordinate and observed access>
environment: <observed OS / network / owned workspace>
limits: <observed limitations / unknown>
authority_note: <current authority pointer>
status: <conclusion under Bootstrap protocol>
blockers: <exact missing required capability / none>
```

<!-- Compatibility anchors; current semantics are linked above. -->
<a id="capability--authority"></a>
<a id="capability-self-check--agent-节点能力盘点"></a>
<a id="与-bootstrap-check-的分工"></a>
<a id="固定盘点项"></a>
<a id="填空模板"></a>
<a id="完成后"></a>
<a id="规范源"></a>
<a id="触发文本"></a>
