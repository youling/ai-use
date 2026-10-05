# Adaptive Reasoning Effort — 实践指南

**Classification: L2 non-normative guide**  
**Source:** `youling/ai-use#113`

本指南帮助 Human / Architect 把 provider 暴露的 reasoning effort 当作**可升降计算强度**使用。Normative owner 仍是：

- Fresh / takeover cold start：[Architect Reconnaissance](../docs/ARCHITECT_RECONNAISSANCE.md)；
- steady execution / escalation / de-escalation：[Agent Interface](../docs/AGENT_INTERFACE.md)；
- constraint-quality challenge：current source direction `#106`；
- async Foreman / concurrency guidance：current source direction `#111`。

本文件不建立 scheduler、model router、task DB 或新 lifecycle。

---

## 1. 三个 provider-agnostic profile

### `DEEP_BOOTSTRAP`

适用：Fresh / takeover Architect、material new domain / architecture pivot、durable truth 冲突需要重建 current frame、外部生态变化足以影响 architecture。

目标：扩大搜索与反事实覆盖，形成第一轮可靠 world model，并把结论 durable 化。

### `STEADY_BALANCED`

适用：cold start 已闭合、日常 Architect 协调、常规 Issue / PR 裁决、已有架构内增量设计、Work dispatch / synthesis、已知问题的普通 repair。

目标：足够深，但不把最大 search space 常驻化。优先消费 current durable truth，而不是每轮重新推导已经闭合的事实。

### `DEEP_ESCALATION`

只在 material discriminator 出现时临时升级，例如重复失败、durable contradiction、高风险 unknown、无法调和的独立 evidence、需要以新证据重新打开旧 ruling。

终点：

```text
root cause / ruling established
 -> durable writeback
 -> return to STEADY_BALANCED
```

---

## 2. Provider / product mapping

Core governance **不绑定**具体 UI 名称，例如：

```text
medium
high
very high
xhigh
pro
thinking
reasoning
```

Deployment / Human / adapter 只需把当前产品能提供的档位映射到三个语义 profile。

推荐映射原则：

```text
DEEP_BOOTSTRAP
  -> 当前可用且经济上合理的较深 reasoning tier

STEADY_BALANCED
  -> 非最低质量、也非机械最大值的日常稳定档

DEEP_ESCALATION
  -> 临时提高到足以处理 material uncertainty 的档位
```

如果 provider 没有可调档位，继续使用当前模型；本规则不会制造 capability blocker。

如果只能观测到“模型/模式”而看不到实际内部 effort，也只记录已请求/已知设置，不猜内部 reasoning token、context usage 或隐藏实现。

---

## 3. Open-ended Human exploration

Human 在临时对话里尚未冻结 acceptance、目标是尽可能发现遗漏维度时，可以主动选择深推理：

```text
OPEN_ENDED_EXPLORATION
  -> DEEP MAY BE PREFERRED
```

这与稳定工程执行不同：

```text
FROZEN_ENGINEERING_EXECUTION
  -> STEADY_BALANCED BY DEFAULT
```

探索得到的 material 决策应写回 durable source；后续工程执行不需要为了保留“探索气氛”永久维持 deep。

---

## 4. 升级前先问什么

准备从 steady 升 deep 时，优先回答：

```yaml
signal: <什么 material evidence 触发升级>
current_unknown: <当前真正没闭合的判别点>
why_ordinary_repair_is_insufficient: <为什么不是普通 repair>
expected_exit: <什么 durable result 允许降档>
```

不要求每次都写成正式 artifact；只有当升级本身影响 durable execution / routing / cost policy 时才需要 durable 记录。

---

## 5. 不要把更多想法自动变成约束

深推理常会产生更多备选路径与风险候选。它们默认仍是 hypothesis / recommendation / candidate risk，而不是 Human requirement / hard architecture constraint。

典型错误：

- “最好最多 16 slots”没有 measured boundary，却写进 architecture；
- “最多 2 Foremen + 2 children”只是模型偏好，却变成全项目默认；
- 第一次失败就假定并发太高、timeout 太短或资源不足；
- 为了减少自身不确定性，先禁止还没证明有问题的能力。

这些问题按 current constraint-quality owner 处理；本指南不复制其 amend / escalation authority。

---

## 6. 合法硬边界仍然有效

Adaptive reasoning 不等于无限资源或无限并发。以下边界仍按各自 owner 生效：Human current goal / authority、security / privacy / secret、destructive / irreversible gate、provider hard limit、live machine resource exhaustion、conflicting write domain、dependency / acceptance、measured failure / saturation、legal / compliance。

如果 provider 明确有 hard concurrency/effort limit，或机器已测得 saturation，它们是 evidence-backed boundary，不属于“过度保守”。

---

## 7. 观测与复盘

需要分析 adaptive effort 是否有效时，可记录轻量 evidence：

```text
requested_profile
provider/model/mode (if known)
trigger
task phase
material result
repair/retry count (if useful)
de_escalation_point
```

不要把 hidden chain-of-thought、reasoning token 或不可观测 provider internals 当作必需 telemetry。

评估重点是可见工程结果：是否更快建立 current world model、是否减少错误 architecture assumptions、是否在稳态避免无收益重新开放、escalation 是否解决真实 blocker、durable closure 后是否及时降档。

---

## 8. Regression examples

| 场景 | 推荐语义 |
| --- | --- |
| Fresh Architect 接管陌生项目 | `DEEP_BOOTSTRAP` |
| Cold start 已完成，继续日常协调 | `STEADY_BALANCED` |
| 普通实现第一次失败 | ordinary repair，通常不升级 |
| 同类方案多轮失败且 durable facts 冲突 | `DEEP_ESCALATION` |
| 根因已写入 durable ruling | 降回 `STEADY_BALANCED` |
| Human 临时开放式头脑风暴 | 可主动 deep |
| provider 没有 effort 档位 | 不阻塞；使用现有能力 |
| 改 effort 后想扩大 deploy 权限 | 拒绝；`reasoning_effort != authority` |

核心句：

> **Deep reasoning 用于建立世界模型和破局；durable state 用于保存认知；steady state 不需要永久常驻最大搜索深度。**
