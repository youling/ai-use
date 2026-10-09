# 40_GUIDES

表达、诊断与恢复 guidance 层。

多方向探索、大资料分区或并行施工需要减少架构师逐子对话协调时，按需读取 [异步主工头协作](ASYNC_FOREMEN.md)。它应用既有派单、恢复与 durable trace 协议，不另立状态或授权。

人类可见输出默认简体中文，见 [Language Policy](../00_KERNEL/LANGUAGE_POLICY.md)。

secret/output invariant 见 [AGENTS.md §5](../AGENTS.md#5-evidence-bound-mutation)；public cold-start 回归见 [PUBLIC_COLD_START_CHECKLIST.md](PUBLIC_COLD_START_CHECKLIST.md)。

对于面向用户的安装器、容器、Agent 首次使用交付，按需查看 [首次使用真实性验证：证据梯级与用户历史状态矩阵](USER_FIRST_RUN_EVIDENCE_LADDER.md)，将单元/合成/真实二进制/原生只读/用户现场/完整认证分别验收。它是实践指南，不是新的权限来源。

真实异常 / failure mode / recovery case 统一进入 [INCIDENTS/](INCIDENTS/README.md)。Incident 只提供 evidence + diagnostic/recovery guidance，不成为第二套 authority 或 protocol。

按任务阶段调节模型推理强度：见 [Adaptive Reasoning Effort](ADAPTIVE_REASONING_EFFORT.md)。它只提供 provider-agnostic 实践映射；Fresh/takeover 与 steady/escalation 的 normative owner 仍在 Reconnaissance / Agent Interface。

需要周期观察项目、发现待审/疑似失联/真实 Human Gate，或生成每日恢复摘要时，按需读取 [Architect Watch & Daily Brief](ARCHITECT_WATCH_AND_BRIEF.md)。health class 与 brief 都是派生 read model，不是第二 Work state。
