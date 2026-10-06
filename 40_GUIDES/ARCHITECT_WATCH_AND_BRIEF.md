# Architect Watch & Daily Brief

**Classification: L2 Targeted Guidance / derived read model.**
**Normative wake/authority owner:** [Agent Interface §1.4.3](../docs/AGENT_INTERFACE.md#143-architect-watch--reconciliation-wake)

本指南用于 deployment 已具备 scheduler / automation / event wake 时，帮助 Architect 周期观察 durable Work、发现需要裁决的 delta，并向 Human 提供简洁日报。它不定义 scheduler 实现，不创建 task DB、Work state 或 executor lifecycle。

## 1. Watch 是一次重建，不是常驻意识

每次 wake 都从 current durable source 重新开始：

```text
current L0 / role
 -> owned active Work graph
 -> Issue/PR/remote refs/current ruling
 -> existing CLAIM/CHECKPOINT/TERMINAL evidence
 -> deployment observation when available
 -> derived health
 -> authorized action or silent exit
```

不要把上一次模型会话、brief、定时器内部缓存或 provider self-report 当 current truth。事件只负责“叫醒”，不负责授权。

## 2. Derived health classes

以下名称是可选 read-model vocabulary，**不是 canonical Work states**：

| Class | 含义 | 默认动作 |
| --- | --- | --- |
| `WAITING_FOR_PICKUP` | current dispatch 存在，但尚无 matching durable claim/evidence | 观察 pickup threshold；不得自动另派 |
| `EXECUTING_HEALTHY` | 有 current claim，且存在近期有意义 durable activity / remote movement | 通常静默 |
| `EXECUTION_SUSPECT` | 超过 deployment threshold 或 evidence 停滞，但尚不能证明失败 | reconcile ownership/generation/refs；不自动 takeover |
| `READY_FOR_ARCHITECT_REVIEW` | terminal/delivery/PR evidence 已形成，等待 Architect 裁决 | live-read exact target 后 Review |
| `BLOCKED` | current durable Work 已记录真实依赖/权限/安全 blocker | 路由给 exact owner；无关 work 继续 |
| `HUMAN_REQUIRED` | current Human/higher-authority gate 确实存在 | 通知 Human，带 exact pointer |
| `RECOVERY_CANDIDATE` | suspect/lost evidence 足以进入恢复评估 | 先核 current generation/resource/remote refs，再决定 recovery |
| `HEAD_OR_STATE_DRIFT` | checkpoint/brief 与 current GitHub facts 不一致 | 以 live durable truth 为准，停止基于旧快照行动 |
| `UNKNOWN` | 证据不足 | 保持未知，不补造健康结论 |

同一 Work 可随证据变化重新分类。分类不应 durable 写成第二状态机；需要留痕的是实际裁决、恢复、Review、Blocker 等事实价值行为。

## 3. Staleness

public governance 不规定统一分钟数/小时数。deployment 可按任务类型配置 `pickup_after` / `stale_after` 或等价阈值。

阈值只能帮助发现异常：

```text
threshold exceeded
!= executor failed
!= authority transferred
!= safe to start duplicate work
```

Meaningful activity 优先看 durable checkpoint、remote head movement、PR update、terminal result、真实 BLOCKED/HUMAN_REQUIRED。单纯 heartbeat 不应长期掩盖停滞。

恢复前至少核对：
- current dispatch / claim lineage；
- remote branch / PR / exact head；
- generation/fencing（适用时）；
- shared external resource ownership；
- unknown-effect operation 是否已发生；
- provider rate-limit/backoff 是否仍应等待。

## 4. Daily Brief

Brief 是 Human 的恢复辅助，不是“今天所有事情的全文抄录”。建议一份包含：

```text
as_of: <server/local evidence window>
scope: <architect/project>
sources: <current durable roots>
changes_since_previous: <material deltas only>
executing_healthy: <count + pointers>
suspect_or_recovery: <count + pointers>
ready_for_review: <count + pointers>
blocked_or_human_required: <count + pointers>
completed_or_merged: <material deltas>
head_or_state_drift: <if any>
highest_value_next: <1..N, only when current priority is durable>
freshness: <what was live-read, what remains unknown>
```

原则：
- delta / exception first，不复制 Issue 正文；
- 每个 material statement 有 exact pointer；
- 没有 current priority 证据时不要替 Human 发明排序；
- mutually exclusive READY choices 且 priority 不足时明确 `HUMAN_PRIORITY_REQUIRED`；
- brief 可以过期，任何 mutation 前重新读取 exact Work；
- healthy/no-action 可以不通知；日报 cadence 是 deployment preference。

## 5. Donor findings

#91 吸收历史 #99 的可复用实验结论：
- durable semantic micro-step 可以支持 fresh recovery；
- micro-step 是恢复/调度单位，不等于 one-prompt boundary；
- driver 只应在真实 yield/stall 后刺激，而不是持续刷 wake；
- provider backoff / rate limit / unknown-effect reconciliation 不能被 scheduler 绕过。

这些只是设计证据，不绑定某个 provider、daemon、cron、Actions 或常驻模型。

## 6. Deployment boundary

deployment/control plane owns：
- scheduler/provider；
- cadence；
- Architect/project registration；
- stale defaults；
- notification route；
- automation/task identifiers；
- node/backend selection。

public ai-use 只拥有可复用 wake/reconciliation 语义和 derived projection discipline。

```text
WATCH = RECONCILIATION_LOOP
DAILY_BRIEF = DERIVED_MEMORY_PROJECTION
WATCH_CLASS != WORK_STATE
SCHEDULER_CAPABILITY != AUTHORITY
```
