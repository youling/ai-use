# Antigravity CLI 工头模式研究

**Artifact Version: 1.1.0 · NON-NORMATIVE RESEARCH**

Rationale / acceptance: [ai-use #148](https://github.com/youling/ai-use/issues/148)。本目录保存 2026-10-13 对官方 Antigravity CLI 1.3.4 的运行实证与可重跑合成材料。它不建立新权限、默认模型、派单协议、Work 状态或调度服务。角色、派单和持续推进仍由现有 [Foreman](../../../20_ROLES/FOREMAN.md)、[Agent Interface](../../AGENT_INTERFACE.md)、[Recovery](../../../30_PROTOCOLS/RECOVERY_HANDOFF.md)、[Durable Trace](../../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) 拥有。

## 结论与证明范围

**QUALIFIED_SYNTHETIC_ONLY**：已完成宿主架构师 → 原生工头 → 两个原生 child → 宿主独立执行固定测试 → 工头综合。请求及 init 回读 Gemini 3.8 Flash High、effort high，经原生 Google 登录成功调用。实际产生两个不同分支 Git worktree；建造者改合成读取器、验证者从合同独立写 12 项 stdlib 测试。宿主跑同一套测试，原始错误实现 10 failures + 1 error，修正版 12/12 通过，执行期间文件 hash 稳定。父候选未被子写入改变。

同一父 conversation_id 接续三轮，并向原 verifier ID 发消息，核对其真实 PLANNER_RESPONSE 中的接续标记；提示或 SYSTEM_MESSAGE 中出现标记不计成功。历史原生会话事实由实例 owner 留存；公共仓只保留去敏角色计数和范围，不复制 private topology、客户数据、credential/global settings 或原始思考过程。

这只支持有界合成任务运行。没有证明真实业务能力、生产事务/并发、长期无人值守、收费金额/配额、独立配置根或对抗式权限安全。本次初始 child 未证明第一项显式规范读就是 AGENTS.md，自动规则注入也未审计；因此不能把运行实证当完整 governed BOOT 认证。正式采用须先对每个执行上下文补齐当前规范、精确合同、owner/ref/权限和读入证明。

## 观察与工程含义

| 实际观察 | 可复用做法与限制 |
| --- | --- |
| 已安装目录没有进入宿主当前进程 PATH | 用明确的 CLI 绝对路径；无需修改全局 PATH。 |
| 本机 models --json 返回 flag undefined；plain models 可用 | 先看本机 help，不把版本外文档当当前能力。 |
| effort-bearing slug 与 --effort 不一致时调用失败 | 成对选择已列出的型号与 effort，记录 init 实际值。 |
| init.tools 有 wait_5_seconds，但自定义 executor 拒绝该组件 | init inventory 不是可直接复制的 Agent tool 注册表；先做最小构造探针。 |
| native branch 生成真实独立 worktree | mutable child 用独立 branch/物理目录，记录真实 parentage 与写域；目录隔离不是全局对象隔离。 |
| SUCCESS + 空 response；另一次 SUCCESS + denied_actions | 验收须看真实工件、子状态、终态语义和宿主测试；exit0 不能直接算完成。 |
| headless 父报告写入被拒绝 | 保留拒绝，不重试该目标或绕过；后续父移除写组件，用 finish 返回结构化结果，由授权宿主发布。 |
| resume 保持 conversation ID；后端曾停止后台任务 | 以原 ID 发新消息可有界接续，仍需真实 child 回执；不推断它一直在线。 |
| result usage/num_turns 等可能累积 | 不直接累加各轮 resume 的累计数计费；未知费用保持 UNKNOWN。 |
| Windows worktree 应用换行规则 | Git commit/blob 身份和实际工件 SHA256 分开记录；精确字节材料显式控制 gitattributes。 |
| shared settings 在试验中发生 provider 漂移 | 当时经 Human 授权、写前 hash 检查，仅移除 modelProvider 并保留其它字段语义；这不是通用改配置授权。独立配置根未取得实证。 |
| 子显式 BOOT 第一读缺少证明 | 下一轮要求 first tool 读 current AGENTS，再按 NAMESPACE/READING_MAP targeted routing，并核对实际工具轨迹。 |

以上列为 observed-derived engineering guidance，不能替代当前 owner 的实际 gate。出现失败但输入/机制/判别目的未变化时，不机械同形重试。

## 合成重跑

`synthetic/` 内是冻结的纯合成代码及独立测试，哈希与原宿主执行材料相同。读取器合同：checkpoint 按 account/generation/shard 分区，按新 seq 接受；旧发送时间不能挡住新落地；分区间同 message_id 保留；分区内精确重投去重；按确定顺序输出；只推进实际接受记录的 checkpoint；不修改调用方输入。该合同是玩具 oracle，不是某真实来源或消费者 schema。

在本目录执行：

```text
python reproduce.py
```

脚本检查固定文件 hash，再在临时目录执行相同测试，对照 baseline 红和 builder 绿。预期重跑脚本 exit0，表示两个对照都与冻结判别一致；baseline 子测试仍为 exit1。它不启动模型、不访问网络、不读用户配置。`evidence.json` 是原试跑的事实摘要，新一次输出只代表固定测试的再次执行，不伪装原生父子会话重跑。

`examples/agents/` 为当时最小 Agent 定义，non-normative，必须置于新隔离 Git 项目的 `.agents/agents/` 并提供 current AGENTS 与自己的 synthetic TASK 才可用。实验后的 qn 工作输入、私有拓扑与实时 owner 状态不进入此目录。示例中父禁止写报告对应实际 headless 拒绝；使用它不产生其它路径或 action 的授权。

## 后续运行观察：首规范读与测试判别

2026-10-13 后续离线应用中，宿主检查了三个真实 native branch child 的第一份工具回执：均为完整 AGENTS.md，100/100 行、7472 bytes，后续按路由读取 BOOT 与 target contract。它补上的是显式 kernel-first 读取证明，不把初始试跑“未证明”改写为历史成功，也不自动证明完整 lifecycle、ACL 或配置隔离。该应用的代码、实例拓扑、当前 Work 与业务结论保留在其私有 owner；此处只沉淀运行方法。

宿主执行还发现几类可复用判别问题：schema 已存在时重新建库、随机字段未冻结导致顺序对照不可比、合法 ID 文法/分页大小含义误解、等价时间戳按字符串比较、以及猜测 raw locator 或错误返回名称。测试红项先区分 fixture / contract interpretation / candidate defect，由原 child 修自己的测试并保留原红快照；不能只改期望拿到绿，也不能把代码能运行或报告自称覆盖当独立验收。

成功检测缺陷的反例测试本身可以是绿色；这证明反例被复现，不能推导业务 gate 已解决。测试名含“并发/constant memory/process crash”也不证明活动事务中的并发、实测 RSS 或每个原子写入窗口。单个受控 worker 在文件写完后的 sleep 窗口被终止，只证明该样本的后续恢复路径。无符号链接权限必须显式 SKIP / INCOMPARABLE，不能 return 伪计 PASS。

调用超时也应随实际资料量调整：早期 4m 调用结束时父 SUCCESS/response 空而 child 未完成；后续将单次边界调为 12m，保持原 parent/child ID 接续，没有新增重复 writer。超时值是本次工程选择，不能成为公共固定配额或全天在线承诺。

## 经验账本的后续增补

每次有语义变化时，保留版本、认证路线、requested/observed model+effort、真实 parent/child、物理写域与共享对象、commit/blob/byte hash、工具/拒绝、宿主回执、结论和 UNKNOWN。实例 ID/path/实时 Work 状态留 owner；公共目录只收去敏可复制方法、合成材料和范围。新结论需要新证据，不覆盖旧失败，不因额度充足推导权限或无限可靠性。

官方资料：[headless](https://antigravity.google/docs/cli/headless/)、[subagents](https://antigravity.google/docs/subagents?tab=cli)、[permissions](https://antigravity.google/docs/permissions/)、[独立配置根议题](https://github.com/google-antigravity/antigravity-cli/issues/155)。这些是上游资料，本文结论以本机 1.3.4 的实际观察为范围。
