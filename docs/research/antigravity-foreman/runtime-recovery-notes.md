# Antigravity 原生工头的第二轮运行与恢复

2026-10-13 · CLI 1.3.4 · NON-NORMATIVE RESEARCH。这是同日后续运行的去敏观察，不覆盖初次合成试跑，也不新建派单/权限/模型选择规则。实例、私有项目、实际写域、原始会话和运行回执由实例 owner 保存，公共仓仅记录可复用方法与证明边界。

## 新增实证

原生父会话实际创建了三个不同 conversation/branch worktree 的 child：两个证据作者与一个 fresh 独立挑战者。宿主核对三者第一项显式规范读取均为完整当前 AGENTS.md（101/101 行），随后按 namespace/reading map 读取相关合同。冻结输入 hash 未漂移；三个写域分别保存产物。这里只补足 kernel-first-read 与物理隔离的观察，不宣称所有 governed BOOT、OS ACL、共享设置或对抗式权限都已认证。

作者实际输出了文档/机器矩阵，fresh 挑战者从原始合同挑战三个可能错误的关系。宿主语义审查仍发现了 capability 编号错用、来源/设备身份混淆、将历史样本当当前样本、将逻辑接口当已部署接口等错误。机器 schema/引用/hash 检查通过不证明这些关系成立。历史版本被保留为失败或部分输入，纠正后的材料明确 source scope、clock、grade、falsifier 和 consumer need；发布/规范采纳仍由原有 Architect gate 决定。

## 运行失败和边界

| 实际观察 | 本次处理及可复用判别 |
| --- | --- |
| 配额界面显示充足，但模型请求返回 503 No capacity available | 配额和后端容量分别记录；不从 remaining quota 推导请求可用或持续运行。 |
| Google API 经已配置本地代理出现 connection reset | 记录为传输失败；本轮没有修改全局代理或登录设置。其它工具的成功路线不证明该模型链路已恢复。 |
| 一次长调用返回 SUCCESS/exit0，但 response 为空；有界 resume 仍没有完成语义 | 检查真实工件、child 状态和 Work finish predicate；空成功不是 acceptance，更不是后台服务已经启动。 |
| thinking 型号与显式 effort 组合被本地参数校验拒绝 | 先依本机 help/model inventory 判断该型号是否接受 effort；有的型号需省略独立 effort。不要把某一个型号的组合规则泛化全部型号。 |
| 省略 effort 后 init 宣告请求的另一型号，但最终错误仍指向原模型 | effective switch 保持 NOT_PROVEN；requested model、init observation、实际最终路由/错误分别记账。 |
| 父读取项目外某个 findings 资源被权限层拒绝 | 保留拒绝，未复制这个资源到其它位置重试。恢复只消费另行已获准的原始合同/产物及宿主审查事实，不规避该资源拒绝。 |
| 官方 connector 当时不可用，另一工具默认代理路线也失败 | 已授权宿主使用经验证的进程级传输环境处理 durable publication；不修改全局设置，不用路线恢复赋予额外身份或派单/merge 权限。 |

在原生最终综合/第二阶段挑战未成功后，宿主改用独立物理写域完成允许输入上的纠错；低风险文档的最后审查由 Architect DIRECT 完成。原来的 fresh 挑战仍仅证明第一阶段范围，没有伪装成最终候选已通过原生 fresh 验收，也没有为了同一 Work 反复创建新的 fresh verifier。涉及行为修复的另一项任务保留了明确要求的独立测试/源码审查；采用 DIRECT 或换 adapter 不减少原合同的独立证据要求。

## 可复制的恢复顺序

1. 从 current durable Work、原 CLAIM、输入 ref/hash、产物和 child 状态恢复，而不是从父的“成功”字样恢复。
2. 先确认失败属于传输、参数、容量、权限还是语义 finding；只有 discriminator/机制有变化时才尝试相应恢复，保留原失败。
3. 若换 adapter，在原有 Work/owner 下冻结输入和候选，给出独立物理目录、branch、唯一写域；原始拒绝的资源不能靠复制绕过。
4. 分清 author 自证、宿主实际执行、fresh 源码/回执审查和 Architect acceptance。合成/元数据 PASS 不升级真实 source、部署或业务能力。
5. 发布只含可审材料、精确 head、终态与 readback。原生未完成记 PARTIAL；host-corrected 交付的结论单独记。resume 的累计 usage 不相加当费用，USD、子账单、独立配置根和长期可靠性保持 UNKNOWN。

没有客户原文、凭据、私有 repo/path/会话 ID 或原始思考过程进入本公共材料。这里的工程经验是 observed-derived，不改变现有 Foreman/Agent Interface/Recovery/Durable Trace 权威。
