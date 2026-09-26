# INCIDENT-0001 — Provider rate-limit degraded execution

## Summary

**Observed window:** 2026-09-26 → 2026-09-27
**Primary work:** youling/ai-use#98 governance audit
**Experiment:** youling/ai-use#99
**Fault class:** provider/session availability / rate-limit degradation
**Case status:** MITIGATION_VALIDATED / ROOT_CAUSE_RESOLUTION_UNKNOWN

在一次 Global Architect 长链治理施工中，Agent 表现退化为“每收到一次 Human 新消息，只能推进一个很小步骤”，无法保持正常的 CONTINUE_WITHIN_AUTHORITY 长链执行。Human 使用 Codex/Astra 做外部分析后判断执行环境遭遇 HTTP 429 rate limiting。

本 case 保留两个层次：

- **Observed fact**：长链自主执行明显退化，需要高频刺激才能继续；
- **Root-cause report**：Human 报告 Codex/Astra 指向 HTTP 429。当前 ai-use case 没有保存 provider 原始 429 response，因此不把它写成独立机器证实的永久平台结论。

## Why this matters

这次异常直接命中了 ai-use 的三类默认故障：

~~~text
Human can fail
AI/session can fail
execution environment can fail
~~~

如果任务状态只存在聊天里，则 provider 限流、会话截断或设备切换都会把 Human 重新变成：

- message bus；
- scheduler；
- context restorer；
- “继续、继续、继续”的人工时钟。

这正是 ai-use 希望避免的系统性脆弱点。

## Failure symptom

典型表现：

~~~text
long authorized Work exists
        ↓
Agent knows there is more READY work
        ↓
no real Human Gate
        ↓
execution repeatedly yields after a tiny step
        ↓
Human must send another message to wake progress
~~~

注意：这个 symptom 不专属于 HTTP 429。provider throttling、session/runtime degradation、context transport failure 等也可能产生相似表面行为。先恢复 Work，再判断根因。

## First response that worked

核心思路不是让 Human 替 AI 规划，也不是让外挂成为新的“大脑”。

职责保持：

~~~text
AI                = plan / reason / decide next legal step
Git/GitHub        = durable Work / checkpoint / recovery source
Human/driver      = stimulus / transport only
~~~

把长任务转换成 durable micro-step graph：

~~~text
Goal
  ↓
Durable Work
  ↓
S1.1 → S1.2 → S1.3 → ...
  ↓
each step:
objective
inputs/evidence
expected output
acceptance
next pointer
~~~

Human 或未来 execution driver 只需要投递最小 stimulus：

~~~text
continue: <owner>/<repo>#<issue>@<step>
~~~

Agent 收到后：

~~~text
live-read Work pointer
 -> read latest valid checkpoint
 -> execute bounded step
 -> durable writeback
 -> continue if still within authority
~~~

它不要求 Human 重新解释项目背景。

## Recovery playbook

### 1. 先停止依赖聊天连续性

不要继续用：

~~~text
推进
继续
再来
~~~

作为唯一调度状态。

先建立一个 durable Work pointer，例如：

~~~text
youling/ai-use#98
~~~

### 2. 把剩余长任务拆成可恢复微步骤

每个 step 至少写：

- objective；
- evidence/input；
- expected output；
- acceptance；
- next pointer。

粒度原则：

> 单步足够小，能够在一次受限执行窗口内完成；又足够大，能产生有事实价值的 durable checkpoint。

### 3. 每完成一个有事实价值的阶段就 durable writeback

复用 [Durable Trace Principle](../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md)：

- 不写 heartbeat；
- 不保存 chain-of-thought；
- 保存做到哪、证据在哪、下一步是什么。

### 4. Human / driver 只发送指针 + step

推荐：

~~~text
continue: youling/ai-use#98@S1.1
~~~

而不是复制整个 Work Order。

### 5. ordinary failure 自行修复

micro-step 模式不是“一步一请示”。

以下仍属于 Agent 可在 authority 内自行处理的 ordinary failure：

- test / CI failure；
- 格式错误；
- stale derived artifact；
- candidate failure；
- 可恢复的 tool error。

只有真正 Human Gate / authority / security / destructive / mutually exclusive priority gate 才停。

### 6. 恢复验证

真正的 recovery test 应尝试：

- 换设备；
- 换 client surface；
- fresh session / old context unavailable；
- 只给 durable pointer，不补旧聊天；

然后看 fresh Agent 是否能从 GitHub 重建：

~~~text
current Work
current step
completed evidence
next legal action
~~~

## What was validated

### M1 — Durable graph materialization

#99 将 #98 从粗粒度 S1–S7 转成细颗粒度 Sx.y step graph。

Pointers:

- https://github.com/youling/ai-use/issues/98#issuecomment-5848303427
- https://github.com/youling/ai-use/issues/99#issuecomment-5848304639

### M2 — Sustained autonomous execution

Human 切换到 **Workstation + ChatGPT Web** 后重新刺激同一对话。

本轮 Agent 从 durable pointer 恢复后：

1. 完成 #98 S1–S7；
2. 关闭 #98；
3. 自动进入审计建议的下一依赖 #96；
4. 创建 PR #100；
5. CI 首轮因 trailing whitespace 失败；
6. Agent 自行读取日志、修复、重新提交；
7. 第二轮 CI 通过；
8. 最终停在真实 merge-authority Human Gate，而不是普通 error 或“等 Human 说继续”。

Evidence:

- #98 final audit: https://github.com/youling/ai-use/issues/98#issuecomment-5848341048
- #96 merge gate: https://github.com/youling/ai-use/issues/96#issuecomment-5848375144
- #99 M2 observation: https://github.com/youling/ai-use/issues/99#issuecomment-5848375333
- PR #100: https://github.com/youling/ai-use/pull/100

这证明：

> durable micro-step / pointer 模式可以在至少一次真实复杂 Work 中支撑自主恢复和 ordinary-failure self-repair。

它不证明：

- Workstation/Web 本身解决了 429；
- 429 已永久消失；
- 每种 provider throttling 都能靠同一粒度恢复；
- 高频 stimulus 可以或应该绕过 provider 的平台限制。

目标始终是**提高 recoverability**，不是规避 provider controls。

## Future execution driver

如果后续多次验证这种 failure mode，可以开发 deployment-local high-frequency driver。

正确职责：

~~~text
read durable Work
 -> send exact pointer / next step stimulus
 -> observe response
 -> require durable checkpoint
 -> repeat until terminal / Human Gate
~~~

Driver 不应：

- 自己持有唯一任务状态；
- 代替 AI 做架构判断；
- 从“能发消息”推导 authority；
- 用 scheduler memory 覆盖 GitHub current truth；
- 无限高频重试同一个失败请求。

换句话说：

> AI 继续负责规划；外挂只负责在不可靠交互面上保持节拍。

## Open questions

仍需 #99 后续实验回答：

1. 最优 micro-step 粒度是多少；
2. 哪些任务不能安全切片；
3. fresh-session only-pointer recovery 的成功率；
4. driver 应如何判断“Agent 正常思考中”与“已 prematurely yielded”；
5. provider 明确返回 retry/backoff 信息时，driver 如何尊重而不是机械刺激；
6. 哪些现象应该升级为 Incident Mode，哪些只是 degraded availability。

## Related canonical guidance

- [Durable Trace Principle](../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md)
- [Recovery & Handoff](../../30_PROTOCOLS/RECOVERY_HANDOFF.md)
- [Agent Interface](../../docs/AGENT_INTERFACE.md)
- [Public Cold Start Checklist](../PUBLIC_COLD_START_CHECKLIST.md)

本 case 是这些协议的真实 failure/recovery evidence，不取代它们。
