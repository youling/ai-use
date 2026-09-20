# R74 fresh-reader results

Artifact Version: 1.0.0

五类前后读者均能从 synthetic current Work Order/state 恢复，未采纳旧交接产物或新 Human prompt 的错误门。候选读者全部直接定位 Recovery protocol；基线读者靠 Session §10、Interface 与 Trace 的兼容关系解析 recovery。这个实验没有证明基线恢复失败，也没有证明所有项目阅读成本下降。

方法与限制见 [README](README.md) 和[冻结场景卡](evaluation-plan.json)；原始观察与精确 file/range/hash 记录由 [measurements](measurements.json) 索引。正确性和错误门的人工判读逐项列于 [scoring](scoring.json)。

## 配对计量

B = baseline，C = candidate。bytes 是 instrument 输出的源 UTF-8 字节，含重读；unique 对同文件源行去重，不含目录 metadata。若工具截断，不能推断模型完整摄入了这些字节。

| 类别 | 文件 B→C | read ops B→C | bytes B→C | 差值 | unique bytes B→C |
| --- | ---: | ---: | ---: | ---: | ---: |
| infrastructure/platform | 10→10 | 12→13 | 109,319→111,055 | +1.59% | 105,775→97,625 |
| fact/archive | 11→11 | 13→13 | 126,814→103,615 | -18.29% | 120,530→100,062 |
| product | 9→9 | 12→10 | 105,856→77,640 | -26.66% | 104,471→77,617 |
| research/evidence | 10→10 | 12→14 | 106,854→95,599 | -10.53% | 106,854→95,599 |
| decision/runtime | 11→11 | 14→11 | 150,474→102,562 | -31.84% | 120,530→102,562 |
| 合计（文件数为各 reader 之和） | 51→51 | 63→61 | 599,317→490,471 | -18.16% | 558,160→473,465 |

五类文档数量未减少。候选合计 emitted bytes 下降 18.16%，unique source bytes 下降 15.17%；这些只是本组读取行为的配对描述。Infrastructure emitted bytes 增加 1,736（1.59%），unique source bytes 减少 8,150（7.70%），补读/选段行为影响显著，不能把全部差值归因于正文压缩或声称每类提升。

Baseline metadata bytes 为 927（research 926、decision 1），candidate 为 0；未并入上表正文指标。不同 reader 的 range 选择和语言输出不是严格受控的认知实验；每格仅一个随机模型观察，不报告统计显著性或外推成功率。

## 语义观察与实际门槛

| 类别 | canonical topics B→C | adopted wrong/extra hops B→C | adopted false blockers B→C | 无旧聊天可恢复 B→C |
| --- | ---: | ---: | ---: | --- |
| infrastructure/platform | 5/5→5/5 | 0→0 | 0→0 | 是→是 |
| fact/archive | 5/5→5/5 | 0→0 | 0→0 | 是→是 |
| product | 5/5→5/5 | 0→0 | 0→0 | 是→是 |
| research/evidence | 5/5→5/5 | 0→0 | 0→0 | 是→是 |
| decision/runtime | 5/5→5/5 | 0→0 | 0→0 | 是→是 |

五个主题是 Bootstrap、continuation/completion、recovery/context、Change Lifecycle，以及每类的 architecture/data/mutation/trace 主题。总计 25/25→25/25；baseline 的 recovery 答案可识别当时多个互补 home，candidate 均找到新协议。不能把此分数扩展成全部语义或 authority 审查。

baseline 的 false_blockers 数组有些列的是已拒绝的潜在错误门。评分核对解释与 can_continue，不按数组长度计失败。Bootstrap §3C 写回、ARCH-0 material trigger、L2 ADR 与既定独立 Review 有来源支持；研究的 frozen-design exception、product 小 bug 的 DIRECT eligibility 同样保留。

各类均把 GitHub native relationships / Issue / PR / reviews / checks 或 native access preference 当来源可证明的政策，不推定某 event executor、archive engine、两工具 API 已实测可用；owner-local design 不变成公共实例事实。均区分 branch evidence、currentness 和 production acceptance。

## 截断、错误与独立性

| 类别 | B 截断 / range errors | C 截断 / range errors |
| --- | --- | --- |
| infrastructure | 有，补读 / 2 | 有，补读 / 1 |
| archive | 有，补读 / 1 | 有，补读 / 2 |
| product | 有，补读 / 1 | 无 / 2 |
| research | 无 / 4 | 无 / 1 |
| decision | 无 / 3 | 无 / 0 |

失败范围未输出正文，未计入成功 read ops；观察原文记载补读与限制。研究 baseline 遇额度中断，在用户恢复额度后续跑原 isolated context，不算第二个样本。没有因结果有利/不利而替换任何 reader；候选源码冻结后没有改动以影响该组读者。父协调者保留历史，只做对账，不自称 fresh 或 Global reviewer。

## 发现、残留歧义和 Review 边界

- Baseline 的旧 Session 历史 STOP/全 workspace scan、Trace 缺少 absent-checkpoint 分支和 template semantic ownership 分散增加解释负担。R1 将旧入口转 forward，Recovery 明确 crash 路径，Trace 加 current-state fallback；五个候选读者均未要求返回旧 playbook。
- Infrastructure candidate 仍指出 L0 的 NAMESPACE + READING_MAP 与 Bootstrap scene-based NAMESPACE 的轻微张力；未形成错误阻塞。L0 原样保留，该张力与 +1.59% emitted-byte 回归一起提交 Global Review，不借机扩张改动。
- Material schema/currentness 是否 L2、ARCH-0 是否已由同 scope 证据满足，需要真实 owner-local diff/contract。readers 的条件分支不是本实验缺失事实的权威裁决。研究/产品类不被自动套入 production 或新架构审批。
- 本组未执行项目 Bootstrap 写回、业务代码、部署或真实生产测试；currentness/access 是明确 fixture。结果不是 Capability Lab establishment、生产安全保证或独立 Global semantic acceptance。
