# Architect Handoff Transaction — Copyable Shapes

**版本：1.0.0**

事件含义、适用性、前置门与 durable writeback 只由 [Recovery & Handoff §2–3](../30_PROTOCOLS/RECOVERY_HANDOFF.md#2-共同恢复门与-currentness) 定义。下面保留 REQUEST / ACCEPTED 的中文字段形态；旧 artifact 的 provenance 不变。

## ARCHITECT_HANDOFF_REQUEST

供 current planned-transfer contract 使用。

```yaml
版本: "1.0.0"
事件:
  类型: ARCHITECT_HANDOFF_REQUEST
发起方:
  身份: <synthetic-or-deployment-local-identity>
  pointer: <current-authority-pointer>
接收方:
  身份: <synthetic-or-deployment-local-identity>
交接范围:
  role: <role>
  workspace: <owned-workspace-pointer>
  authority_scope: <current-scope-pointer>
依据:
  durable_sources: [<current-pointer>]
生效条件: <current-contract-pointer>
备注: <optional>
```

## ARCHITECT_HANDOFF_ACCEPTED

适用前提与 crash recovery 的不同记录路径见协议；本模板不要求 crash 伪造 REQUEST。

```yaml
版本: "1.0.0"
事件:
  类型: ARCHITECT_HANDOFF_ACCEPTED
接收方: <identity>
验证:
  bootstrap_report: <pointer>
  capability_check: <applicable-pointer-or-not-applicable>
  handoff_check: <pointer>
恢复来源: [<current-durable-pointer>]
当前状态: <current-state-pointers>
限制: <limits>
阻塞: <exact-gate-or-none>
时间: <observed-time>
```

## Recovery report shape

可与 Bootstrap Report 合并，字段语义见协议。

```text
recovery_kind: <canonical value>
authority_evidence: <current pointer>
recovery_sources: <Git/GitHub pointers>
old_context: <available / unavailable>
checkpoint: <valid pointer / unavailable>
primary_evidence: <current pointer>
bootstrap_report: <durable pointer>
drift: <observed differences / none>
next: <current authorized action / exact gate>
```

<!-- Compatibility anchors; current semantics are linked above. -->
<a id="architect-handoff-transaction--总架构师交接事务"></a>
<a id="capability--authority"></a>
<a id="回写要求"></a>
<a id="在-handoff-流程中的位置"></a>
<a id="规范源"></a>
