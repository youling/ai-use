# Incident Catalog

**Classification: L2 Diagnostic / Recovery Guide.**

本目录保存 ai-use 在真实协作中遇到的**异常 / failure mode / recovery case**。它的价值不是把事故变成新的宪法，而是让后来的 Human / Architect / Agent 在遇到相似症状时，能先找到已有证据、恢复路径与已验证边界，而不是从聊天记忆重新发明处置办法。

## 使用边界

Incident case 是：

- 真实异常的 durable evidence / case study；
- 可复用的诊断与恢复 guidance；
- 后续协议优化的 donor evidence。

Incident case 不是：

- authority source；
- Work / scheduler SSOT；
- provider capability registry；
- 一次观测就永久成立的全局结论；
- 替代 canonical protocol 的第二套规则。

若 case 与 current protocol 冲突，以 current canonical protocol 为准，并把 case 标为 superseded / partially applicable；不要改写历史让事故看起来没有发生。

## 记录格式

每个 case 至少区分：

1. **Observed facts** —— 当时实际观察到什么；
2. **Diagnosis / confidence** —— 根因是否有直接证据，还是 Human/Agent 推断；
3. **Impact** —— 哪类工作被破坏；
4. **Recovery / mitigation** —— 实际采取了什么；
5. **Validation** —— 哪部分已在真实任务中验证；
6. **Limits / unknowns** —— 仍然不能证明什么；
7. **Durable pointers** —— Issue / PR / exact head / log / report；
8. **Reusable playbook** —— fresh reader 可以直接执行的最小步骤。

不要保存 secret、原始大日志、chain-of-thought 或不必要的私有 deployment 细节。

## Index

| ID | Case | Fault class | Status | Reusable response |
| --- | --- | --- | --- | --- |
| INCIDENT-0001 | [Provider rate-limit degraded execution](INCIDENT-0001_PROVIDER_RATE_LIMIT_DEGRADED_EXECUTION.md) | provider/session availability / rate limit | mitigation validated; root-cause resolution unknown | durable Work pointer + micro-step graph + checkpoint/resume |

## 何时新增 case

值得进入本目录的异常通常满足至少一项：

- 真实中断暴露了治理/恢复假设；
- Human/Agent/设备/provider failure 导致 Work 不能按正常长链继续；
- 处置方法具有跨项目复用价值；
- ordinary error 被自动修复，但恢复路径本身值得复用；
- 同类问题未来若再发生，重新调查的成本明显高于维护一份 case。

普通单次 typo、局部 test failure、无复用价值的小错误不需要进入 incident catalog。
