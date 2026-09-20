# Architect Handoff Check — Copyable Shape

**版本：1.0.0**

先按 [Recovery & Handoff §1–3](../30_PROTOCOLS/RECOVERY_HANDOFF.md#1-恢复分类) 选择恢复类别；检查与生效条件全部由该协议定义。此表用于记录接收 evidence，无值与不适用项按实际填写，不从模板推导新 gate。

```text
ARCHITECT_HANDOFF_CHECK
---
recovery_kind: <canonical value>
work_or_role: <current durable coordinate>
authority_evidence: <current pointer>
bootstrap_report: <pointer>
outgoing_pointer: <pointer / unavailable / not applicable>
current_state: <current Work / refs / active graph pointers>
frozen_boundaries: <current pointers>
primary_evidence: <current role / ownership evidence>
drift: <observed differences / none>
capability_evidence: <applicable evidence pointer / not applicable>
result: <conclusion under canonical protocol>
blockers: <exact gate / none>
next: <current authorized action / exact stop>
```

事务形态见 [architect_handoff_transaction.md](architect_handoff_transaction.md)。旧 Fast Restore 入口只保留 [compatibility forward](../docs/SESSION_LIFECYCLE.md#5-architect-fast-restore-template)。

<!-- Compatibility anchors; current semantics are linked above. -->
<a id="architect-handoff-check--总架构师交接验收"></a>
<a id="固定检查项"></a>
<a id="在交接流程中的位置"></a>
<a id="填空模板"></a>
<a id="完成后"></a>
<a id="规范源"></a>
<a id="触发文本"></a>
