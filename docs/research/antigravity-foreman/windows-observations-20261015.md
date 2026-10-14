# Windows 多工头运行：有效路径与失败边界

**Artifact Version: 1.0.0 · NON-NORMATIVE RESEARCH**  
观察日期：2026-10-15（Asia/Shanghai；首轮终态综合截至 2026-10-14 17:25 UTC，恢复施工有限跟进截至 17:45 UTC）。后续终态不在本文范围。

本轮由一个已授权宿主协调上下文管理三个 Antigravity CLI 父会话及其第一层原生 children。两条方向产出实际独立分支工件；另一条保留工作区失败和部分源码审阅。它证明这种宿主协调方式可用于有界 source/synthetic 工作，未证明长期无人值守或通用工作区修复。宿主席位无需与每个 worker 一对一对应；本次三个只是实际调度结果，数量随 READY 工作、资源、provider 结果和 owner 冲突变化。

来源为实例 owner 已精确回读的 dispatch、阶段报告、三项终态、架构师有限综合与纠补，另有宿主限定范围的工具/Git 交叉核验。私有坐标、会话 ID、物理路径及原始思考日志留在 owner；本文只保留去敏观察。不是新的治理合同，现有 [Foreman](../../../20_ROLES/FOREMAN.md)、[Agent Interface](../../AGENT_INTERFACE.md) 与 [Recovery](../../../30_PROTOCOLS/RECOVERY_HANDOFF.md) 仍拥有对应语义。此前额度/模型/换行记录见 [运行恢复笔记](runtime-recovery-notes.md)。

## 实际结果与证据限度

| 方向 | 本轮观察 | 不能据此推导 |
| --- | --- | --- |
| A：源码复核与新反例 | 两个真实独立 branch child，源码报告及 7 项新方法落盘。宿主执行原 15 方法：候选 15 PASS，对照 15 方法出现 28 失败断言；修订后的新 7 方法：候选 7 PASS，对照 7 方法出现 9 失败断言。新测试 r0 的 fixture ERROR 保留。 | 方法数与失败断言数不是同一分母。报告里的 save 失败恢复收窄为 memory-only rollback，未证明 replace 后磁盘回滚或所有 IO 故障。 |
| B：接入审阅 | 父完成有界源码归因；原 branch child 只见 23 次主要规则/运输读取，没有源码报告，不能称子施工完成。宿主在两个冻结 store 上各跑 53 方法，短路径均 51 PASS / 2 symlink SKIP。 | known53 绿不否定独立发现的嵌套 schema alias。首轮原 helper 未修；浅复制内层 dict 仍会共享列表，建议不是实现。 |
| C：来源图谱审阅 | 三个真实 branch child 产出工件。宿主的声明/schema 检查及 8、9 方法合成控制通过；原 child 按有限审查纠补报告，旧终态保留。 | 元数据/玩具 PASS 不证明现实来源关系。proposal 不等于实现；共享 envelope seam 与来源身份分离可同时成立；15 个负样本不证明通用 join 永远不可能。 |

本轮测试由宿主确定性执行，不能记成原生 child 已运行 shell。具名 source、测试和字节指纹分别绑定，source reading、宿主执行、独立挑战及架构采纳各自记账。原生 finish 加完整 GitHub 报告/终态回读，可以形成可消费的 **PARTIAL**；空 SUCCESS、exit0 或 role 标签均不足以关闭父级验收。

## 工作区恢复：单 Git 成功的范围

多 `--add-dir` 输入中有 plain/readonly 非 Git root 时，批量 branch 派发部分创建了一个真 branch，随后报 `VCS type Unknown`。整个批量返回失败不代表零 child；应逐一检查真实返回和物理候选写域。父随后采用 shared/inherit 回退的两个 child 不合格，被取消并停止写入。

把治理与输入目录 Git 化后，两个 metadata root 分支成功，但可写候选仍指向父目录。看到“有两个 branch”仍不能批准 candidate writer。该失败保留；不能把 role 名、URI 数量或 parent 自报当作源码隔离证明。

下一项已获授权的修复采用独立短路径 **single Git workspace + `--new-project` + zero extra roots**。首规范读完整 L0，之后按目标规则读 implementation；实际独立 builder branch 已恢复，宿主工具回执和 Git diff 交叉确认 helper 的两处深复制写入。修改后既有回归在两个冻结 store 上各 51 PASS / 2 SKIP，相关源字节无漂移；**新反例和独立 challenge 尚未完成**。该样本支持 branch/writer eligibility 恢复，不能称缺陷已完整修复或所有多 root 问题已解决。

private seed 的实际 Git HEAD 与原 source base 不同，原 helper 字节未改时也不能把两个 HEAD 写成相同。恢复记录应分别保留 source base/blob/byte fingerprint 与 actual seed HEAD，再检查每个 child 的真实 branch、父子关系和写域。

## 另外两类可复制判别

- B 的长路径 r0 每个 store 是 39 PASS / 12 `WinError 206` ERROR / 2 SKIP。获准短路径运输后，源码与测试字节不变，得到上述 51 PASS / 2 SKIP；原 ERROR 不改写成语义红控。这个运输修复针对路径机制，不适用于被权限层拒绝的对象。
- 第四项候选工作启动 BOOT 后，最新 durable 补记指定了另一个 runtime owner，因此本宿主停止自己的启动；无 CLAIM、无 child、无实质写入。**未 CLAIM 不等于无 owner**。currentness 要读最新正文及 owner 约束，只记 comment IDs 会漏掉这一变化。

规则读取同样需要证据：first L0 和完整必要 target reads 可核对，但 23 次规则读取不等于 implementation 工作。minimum sufficient routing 已满足就进入授权步骤；不能把读取次数设成验收，也不能无限扩读来掩盖未产工件。

## UNKNOWN 与拒绝边界

父请求/init 观察为 Gemini 3.8 Flash High，effort high 是请求；child 请求 inherit，effective model 未独立暴露，保持 UNKNOWN。宿主当前 executable hash 只绑定该次采样；installed version UNKNOWN，help changelog 的 1.3.5 不能证明安装版本或早先 exe 未变。free/paid 费用、长期容量与配置隔离没有本轮证明。

read/write denied 按精确资源保留，不复制或换路径再访问。合法原生 finish、另行已获准工件及宿主安全测试事实可作有界交接；不能说父读过被拒资源。客户正文、图像/OCR/音频、凭据和历史解密常量不进入公共笔记。真实业务、PG、native identity、断电/IO 故障未运行即 NOT_RUN；本轮 source/synthetic 成果不提升生产等级。
