# ADR-0011 — Adaptive Reasoning Effort：阶段化升降档而非永久最大推理

- **Status:** Accepted direction / materialization in #113
- **Issue:** `youling/ai-use#113`
- **Decision level:** L2
- **Canonical owners:** `docs/ARCHITECT_RECONNAISSANCE.md`, `docs/AGENT_INTERFACE.md`

## Context

Architect 在 Fresh / takeover / material architecture cold start 中需要恢复 current durable truth、重建世界模型、识别 stale/superseded evidence，并做 architecture delta。此阶段更深推理通常具有高价值。

但在 durable world model 已建立、Git/GitHub 已保存关键认知之后，把最大 reasoning effort 作为 Architect 永久驻场配置会混淆“冷启动搜索成本”与“稳态执行需要”。真实实践中还出现过无 evidence 的 numeric/resource cap、把 possible risk 升级为 current blocker、重新打开已 durable 关闭问题等反模式。

这些反模式的 constraint-quality 与 concurrency owner 已分别存在；本决策只补 reasoning effort 的阶段化运行语义。

## Decision

采用三个 provider-agnostic 语义 profile：

```text
FRESH / TAKEOVER / MATERIAL COLD START
  -> DEEP_BOOTSTRAP

DURABLE WORLD MODEL ESTABLISHED
  -> STEADY_BALANCED

MATERIAL FAILURE / CONTRADICTION / HIGH-RISK UNKNOWN
  -> DEEP_ESCALATION

DURABLE ROOT CAUSE / RULING
  -> DE-ESCALATE TO STEADY_BALANCED
```

Reasoning effort 定义为 compute/search-depth hint：

```text
REASONING_EFFORT != AUTHORITY
REASONING_EFFORT != EVIDENCE
REASONING_EFFORT != TRUTH
REASONING_EFFORT != PERMANENT RISK POSTURE
```

Fresh/takeover trigger 归 Architect Reconnaissance；steady/escalate/de-escalate 归 Agent Interface。Provider/UI 档位映射留在 Guide，不进入 core governance 常量。

## Why not always maximum

最大推理强度并不等于最大工程正确性。稳态工程已经拥有 durable current model 时，每轮重新扩大搜索空间可能增加延迟、无收益反事实、重新打开已闭合问题或把弱信号硬化为约束。

治理只对**可观察行为和 durable outcome**做判断，不声称 provider 内部 reasoning token 必然占用可见 context、或更高 effort 必然导致漂移。

## Why not always balanced

Fresh/takeover、material contradiction、高风险 unknown、根因长期不能闭合等阶段确实需要更大的 search/discrimination budget。完全禁止临时 deep 会损失冷启动与破局能力。

## Ownership

- `ARCHITECT_RECONNAISSANCE`：`DEEP_BOOTSTRAP`；
- `AGENT_INTERFACE`：`STEADY_BALANCED / DEEP_ESCALATION / de-escalation`；
- Guide：provider mapping / Human exploration；
- constraint-quality / hard-cap challenge 不在本 ADR 重定义；
- Foreman concurrency 不在本 ADR 重定义。

没有新的 scheduler、task DB、model router、Work lifecycle 或 authority class。

## L0 decision

不修改 `AGENTS.md`。

理由：缺少 adaptive effort guidance 会降低效率/质量，但不会让 Agent 丧失识别 identity / authority / truth / scope / fail-closed 错误的根不变量，因此不满足 Kernel residency test。

## Compatibility

既有 durable Work、Review、Issue、PR、merge/deploy/security/destructive gate 全部保持原语义。Provider 没有 effort control 时不产生 blocker；已有 provider-specific 档位/模型选择继续作为 deployment-local mapping，不自动变成治理常量。

## Counterexample

一个稳态 Architect 因第一次 test failure 就切到最大 reasoning，并提出“最多 2 个 Foremen”作为永久限制。

本决策将其拆开处理：

1. 第一次普通 failure 仍是 repair input，不足以触发 `DEEP_ESCALATION`；
2. 即使临时 deep，也不产生 constraint authority；
3. 无 measured boundary 的 Foreman cap 继续由 constraint/concurrency owner拒绝硬化。

因此 reasoning effort 不会成为绕过现有 owner 的第二条治理轨道。

## Consequences

优点：冷启动保留深推理能力；稳态降低无收益搜索与延迟；escalation 有 material signal 与退出条件；durable state 真正承担“保存认知”的职责；provider-specific 档位可演化而不污染 core governance。

代价：deployment/runtime 需要自行映射当前 provider 能力；“何时 material enough to escalate”仍需 Architect judgment；reasoning profile 不是 correctness proof，仍必须依赖 current evidence 与 Review。
