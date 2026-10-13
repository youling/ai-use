# Antigravity 模型路线与额度账本补记

2026-10-14（Asia/Shanghai）· CLI 1.3.4 · NON-NORMATIVE RESEARCH。

本次按 Human 要求补记最近工头调用的模型与额度经验。它延续本目录的有界研究，未启动新模型调用。原始日志、会话、账号和私有任务拓扑留在实例 owner；这里保留去敏事实与可复制判别。[机器摘要](model-quota-observations.json)不承担计费、配额 API 或调度合同。

## 为什么 Gemini 以外的额度也出现用量

**宿主曾显式选择 Antigravity 内的 Claude Opus 4.6 Thinking，且后续 fresh 工头完成了两轮实际启动检查。** 因此这段执行不是全程 Gemini。原经验材料提到 thinking 型号，但没有将具体型号、切换目的和对应额度组讲清楚；本次补齐这一记录。

宿主核对了相关四组运行日志中的 24 次父会话调用，requested/init 记录涉及 `gemini-3.8-flash-medium`、`gemini-3.8-flash-high` 与 `claude-opus-4-6-thinking`。这个有限审计范围内未见 GPT 或 Claude Sonnet 的父请求/init 记录；不能将这个结果推广到整个账号、其它应用或所有子对话的后台辅助调用。

Human 提供的设置截图把 Gemini Models 与 Claude and GPT models 分为两个组；各组下面都有 Weekly 与 Five Hour 两种限制。后两项是同组的两种时间窗口，截图也没有把 Claude 与 GPT 分账。因此“Claude/GPT 组已有周用量”不能直接证明“Claude 和 GPT 各自都调用过”，更不能读出本任务的精确扣量。截图中两个五小时窗口为 100%，与周窗口已有用量并不矛盾；截图没有提供逐请求计费或完整前后时间序列。

## 本轮可核对的关键序列

| 运行片段 | 请求 / init | 实际可证结果 | 不能推导的结论 |
| --- | --- | --- | --- |
| 最小探针与初次合成工头 | Gemini medium / high | Gemini init 与合成工件、宿主测试分别有回执 | 不代表真实业务、长期服务或全账号只使用 Gemini |
| 既有 Gemini 父会话的修正尝试 | Opus thinking；第一次带独立 high effort 被拒，第二次省略 effort 得到 Opus init | 第二次最终 ERROR 仍标识 Gemini high、503 No capacity available | Opus init 不证明整条会话或旧 child 已成功迁移；该段累计 usage 不能全算 Opus 用量 |
| 后续 fresh 工头 | Opus thinking，省略独立 effort | 两轮 BOOT 返回 SUCCESS，并实际执行读取；第三轮创建两个 branch child，Model 为 inherit，随后 Individual quota reached / ERROR | 这证明调用过 Opus 路线，不证明工件实现或验证完成，也不证明每个 child 的后台模型和计费明细 |
| 同一 fresh 父会话的有界恢复 | Gemini high init | 管理与向既有 child 发消息成功，但原 child 未产出实现或测试，最终仍 ERROR / Individual quota reached | 父切换不证明旧 child 同步切换；CLI exit0 不等于任务成功 |

使用 Opus 的目的分别是尝试修正已有材料，以及换用 fresh 工头诊断/执行新的有界验证。选择发生在宿主调用层，不是日志已经证明的“Gemini 用完后系统自动回退”。这也不是 OpenCode Go、独立 Anthropic API 或独立 OpenAI API 的计费证明。确切金额、逐模型扣量、子账单和所有后台辅助模型仍为 UNKNOWN。

## 模型额度与 AI credits 分开判断

官方 [Plans](https://antigravity.google/docs/plans/) 区分 baseline model quota 与超额使用 AI credits；超过模型基线时，是否使用 credits 受 AI Credit Overages 设置控制。官方 [CLI credits](https://antigravity.google/docs/cli/credits/) 给出 CLI 的 `useG1Credits` 设置和额度查看入口。

本次截图中的 Enable AI Credit Overages 开关显示关闭。这是截图时刻的界面观察，不是整个历史期间都关闭的证据，也不是账单为零的证明。宿主没有在本轮调整开关、全局登录或任何付费设置；当前 CLI 配置没有显式 `useG1Credits` 字段，默认行为与 CLI/GUI 是否共享该项仍需按当前版本核对。配置缺字段不能写成 false。截图包含个人账号信息，原图不进入公共研究仓。

官方 [Model quotas](https://antigravity.google/docs/cli/commands/usage) 说明 `/usage`（别名 `/quota`）会刷新后端配置和额度状态；`/credits` 查看 credits。GUI 截图、本次请求的 Individual quota 错误、后端容量与逐模型账单分别保存，互相不能代替。官方当前页面或另一版本的模型列表也不能覆盖本机 1.3.4 的 help、参数校验与真实 init 回执。

## 后续工头运行可复用的检查点

以下是从观察导出的工程建议，不改写当前 Human 模型偏好或公共派单权限。

1. 每次运行记录 requested model/effort、init model、终态错误中的模型标签及模型切换理由；仅保存必要元数据，不公开原始思考过程、客户数据或凭据。
2. child 的模型选择与继承方式单独记录。新父 init、默认 model 或 `inherit` 声明都不足以证明已有 child 的有效模型已迁移。
3. 需要优化额度时，先刷新 `/usage` 与 `/credits`，保留时间和窗口。配额充裕仍可能遇到 503 容量问题，窗口 100% 也不覆盖另一个窗口或具体请求的错误。
4. 同会话 resume 的 usage/num_turns 可能累计，且跨模型切换后仍携带历史值；不能将所有 result 简单相加，也不能按最后一次 init 将累计 token 归给一种模型。
5. 保留 CLI exit、result status、child 终态和真实工件四层结果。只有启动读规则的 child 不算验证执行；原生 PARTIAL 与宿主后来独立完成的交付分开记。
6. 继续使用独立物理目录/branch，先读 current AGENTS 与合同。Git blob 身份、实际字节 hash 和 LF/CRLF 差异分别核对；目录隔离并不隔离共享设置或配额。
7. paid overage 的当前设置和授权应单独核对，额度余量不创建付费设置变更授权。本次未触发新的探针或同形重试来核算费用。

原 [运行恢复笔记](runtime-recovery-notes.md) 的资源拒绝、空 SUCCESS、kernel-first 证明、换行运输与原生 PARTIAL 仍保留；本次只增加模型与额度归因边界，不扩大 QUALIFIED_SYNTHETIC_ONLY。
