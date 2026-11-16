# 原生工头后续观察：隔离字节、语义复验与终态分离

2026-10-14 Asia/Shanghai · Antigravity CLI 1.3.4 · NON-NORMATIVE RESEARCH。Rationale：[ai-use #157](https://github.com/youling/ai-use/issues/157)，延续已合并 [PR #156](https://github.com/youling/ai-use/pull/156) 与本目录经验。本笔记只消费实际后续运行记录，没有新增模型/业务探针。私有实例、项目、账号、路径、数据、会话和原始思考留实例 owner。

## 已观察的改善

有界父工头先完成 BOOT_ONLY，再由宿主确认实际首规范读及冻结输入；两个真实 native branch child 各读取本工作树完整 kernel、限定独立输出写域。创建 child 前在 task-local packet 固定 gitattributes 为 "* -text"，宿主逐文件核对两个工作树的运输 SHA256，未发现 byte drift。它补充的是这组输入的字节实证，不证明 OS ACL、共享配置根或其它 task 的运输都相同。

requested/init 为 Gemini 高型号，child Model 请求 inherit。子后台有效模型不能从自述或父 init 独立认证，继续单列 UNKNOWN；没有在该运行中主动指定另一型号来回退。累计 usage 与美元、credits/子账单依旧分开，不推算费用或只凭 GUI 余额认定可用。

## 代码、测试与叙述分别审查

原生 child 实际写出脚本、测试与报告；宿主先冻结完整候选，再运行 stdlib 测试。首轮红测有两处测试 oracle 误读：一处猜测错误字符串，一处混淆运行汇总状态和失败等级。原 child 阅读真实合同/代码后修复，保留失败候选与日志；安全扣留、原件校验和错误事实断言未删除。测试通过不意味着相关工业或真实来源能力通过。

另一份报告在算术控制全部绿色时，仍把“后段选定制品一致”扩大成“更早阶段不可能变化”，以及把清单内部相符扩大成初始来源有效。宿主语义审查拒绝这两种推断，原 child 修复叙述与机器标签，并加入针对推断边界的控制。这不是多模型同意即接受，也不因“测试多”降低独立证据要求。模型自行填写 wallclock 还可能是猜测；纯元数据分类器改为未采集时钟，宿主另记实际运行时间。

## 原生最终状态仍有失败

多轮已有父 conversation 接续都产生了可审 child 工件和宿主可用信息，但 CLI exit0 与 result ERROR/stream interrupted 并存。已有 child 可以在下一有界、改变判别目的的消息后继续修复；这不能被表述为原失败已不存在、外层 SUCCESS 或长期后台稳定。原失败、actual candidate hash、宿主执行和 Architect 接受分层记账，不新建重复 child/fresh verifier来替代同 Work 的 lineage。

最后用本机 help 已声明的 --json-schema 做极小结构化 closeout。该型号/版本路线把 schema 转为 function parameters 时，integer/boolean enum 请求返回 INVALID_ARGUMENT/code400，错误指出 enum cannot be empty。去掉这些非字符串 enum 并在相同 conversation 再传修改后的 schema 后，结果仍回读旧 schema/同类错误，同时带有目标 structured_output。**旧 schema 是否实际替换 NOT_PROVEN；有结构体不等于外层 result 成功。** 不继续同形重试，不推广为所有版本的完整 JSON Schema 支持或不支持结论。

工程建议是：有必要用 schema 时，在最小有界探针上确认该版本/型号支持的字段；将实际请求、回读 schema、参数错误、外层终态及 structured payload 都保存。恢复原会话时，模型或 schema 的新启动参数不能替代已绑定上下文的实际回执。这里不建立新的默认模型/派单规则。

## 宿主运输与诊断边界

本机 Git 的既有全局 URL rewrite/SSH proxy 路线发生不兼容。宿主保留失败，只对新执行子进程使用已认证 HTTPS helper 与临时配置环境，取得精确且干净的源码副本；没有修改全局 Git/代理设置或绕过身份权限。

一条普通文件异常曾把私有 source locator 自动带入宿主诊断输出。后续改为只输出匿名条目/路径形状/错误类，并只在获准本地保存真实映射。没有客户行或凭据进入该诊断，原路径未进入公共材料。教训是敏感边界也覆盖 exception/traceback，不能只审成功 JSON；需要在本机确定性投影边界捕获并限量输出，且不把失误改写成全程零私有路径输出。

本次仍 QUALIFIED_SYNTHETIC_ONLY / observed-derived。没有生产部署、真实消费数据库/断电/长期服务保证、独立配置根或收费金额认证；源问题和身份/权限由原 owner 决定，运行工具不会创建额外 authority。
