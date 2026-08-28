# Architect Reconnaissance — Canonical L2 Reference

**Classification: L2 Targeted Reference.** 仅在 Fresh/takeover Architect、material new-domain、major capability / architecture pivot，或快速变化外部生态可能改变方案时读取。普通 Hot Resume、小 bug、确定性维护默认不触发。

source ruling: `youling/ai-hub#50` comment `5451269968`

## 1. 目的与位置

Progressive Context Boot 解决“内部 durable context 当前是什么、我有没有权做”；Architect Reconnaissance 解决“今天外部世界是什么、现有路径今天还是否值得继续”。

固定顺序：

```text
BOOT-1 ADDRESS
BOOT-2 APPLICABLE RULES
BOOT-3 EXECUTION GATE
=> EXECUTION_ALLOWED

ARCH-0 RECONNAISSANCE
  A External Current-State Scan
  B Project / Repo Reconciliation
  C Architecture Delta & Reuse Decision
=> ARCHITECT_READY
```

`EXECUTION_ALLOWED` 与 `ARCHITECT_READY` 不得合并：前者是 authority/currentness gate，后者是 material architecture readiness。

## 2. 何时必须触发

MUST 触发：

- Fresh / takeover Project Architect 或 Global Architect 接管一个需要实质架构判断的项目/领域；
- material new-domain、major capability 选择或 major architecture pivot；
- provider/API/toolchain/OSS/protocol 生态快速变化，可能改变架构方向；
- current durable path 出现明显 stale / superseded signal。

默认不触发：

- ordinary Hot Resume；
- 小 bug、确定性维护、已冻结方案下的窄实现；
- 已有覆盖相同 scope、来源仍 current，且 live revalidate 后继续有效的 reconnaissance。此时引用旧报告并写最小 delta 即可。

不设固定 freshness TTL，也不做按小时/天数 heartbeat。

## 3. ARCH-0A — External Current-State Scan

**先建立 current external frame，再读项目实现做方案判断。**

来源优先级：

1. official docs / official API / protocol specification；
2. upstream / maintained GitHub repository；
3. maintained OSS / primary technical sources；
4. 必要时高质量社区实践。

Targeted 回答：

- 这类问题当前生态的主流 capability / pattern 是什么；
- 是否已有可直接 `REUSE` / `ADAPT` 的 library/service/protocol/tool；
- 是否有近期新增、deprecated、license/platform constraint 或 API/toolchain 变化，会改变当前架构选择；
- 哪些模型记忆、旧 durable assumption 或项目历史判断必须标记 `stale` / `uncertain`。

快速变化事实不得仅凭模型记忆判定 current。外部来源只是 evidence，不是 authority；搜索摘要、社区帖子、benchmark、供应商营销页都必须按证据强度使用。

## 4. ARCH-0B — Project / Repo Reconciliation

完成 ARCH-0A 后，再读取目标项目 current durable code/docs/Issues/PRs/active graph，并逐项分类：

- `KEEP / REUSE`：现有实现仍合理，可继续；
- `ADAPT`：围绕 upstream/existing capability 做薄适配；
- `SUPERSEDED / DEPRECATE`：历史路径已不应继续投入；
- `BUILD`：存在明确 project-local 独特约束，自研有合理收益；
- `UNKNOWN`：证据不足，需要 targeted Research Agent 深挖。

必须显式找 architecture delta：外部 current frame 与 repo 当前实现/文档/Work Graph 哪里一致、哪里漂移。

反模式：

- 先被 repo 现有实现锚定，再上网只寻找支持旧路线的资料；
- 因“已有 OSS”机械禁止自研；
- 因“项目以前这样做”把历史事实误当 current 最优；
- 把 provider/model-specific transient fact 写成永久 governance rule。

## 5. ARCH-0C — Durable output

输出低频、简洁的 `ARCHITECT_RECONNAISSANCE_REPORT`。它是 architecture input / alignment artifact，不是 authority source，也不是文献综述。

最低 schema：

```text
ARCHITECT_RECONNAISSANCE_REPORT
---
as_of: <current date/time or evidence window>
scope: <architecture/domain scope>
external_current_state: <current capability/pattern summary + durable/source refs>
reuse_candidates: <candidate + REUSE/ADAPT rationale>
architecture_delta: <external frame vs current repo>
decisions: REUSE | ADAPT | BUILD | DEFER | REJECT
do_not_build / deprecated_paths: <explicit paths to avoid>
open_questions: <remaining uncertainty>
targeted_research_needed: <none | narrow questions>
first_architecture_direction: <first material architecture/work direction>
```

报告应能让 fresh/resume Architect 快速知道“今天为什么这样选”，但不得复制 secrets、private topology 或无关网页内容。

## 6. Reuse / freshness

可复用旧 reconnaissance 的条件：

- scope 实质相同；
- 关键 source 仍 current；
- live revalidation 没发现 material external change；
- repo/current architecture 没出现会推翻旧结论的新 drift。

满足时，不重做全套 research，只写最小 delta。若关键 provider/API/toolchain/OSS 已变化或旧 source 无法证明 current，则刷新受影响部分。

## 7. 与 Research Agent 的关系

Architect reconnaissance 负责大方向 current-state alignment、reuse/build boundary 和研究问题切分；不要求 Architect 自己把所有技术细节研究到底。

```text
Architect reconnaissance
-> freeze narrow discriminator/question
-> Fresh Research Agent
-> durable findings/evidence
-> Architect reconcile/update architecture
```

Research Agent 不因 findings 获得 Architect authority。Architect 也不得把 Research self-report 当最终 architecture decision；需以 current evidence + project constraints 自己 reconcile。

## 8. Must preserve

- GitHub durable SSOT / Progressive Context Boot；
- `Capability != Authority` 与 Human sovereignty；
- external current evidence != authority；
- 不做 full-Internet crawl / literature-review ceremony；
- 不设 fixed freshness TTL / heartbeat；
- 不创建 search DB/vector store/knowledge graph；
- 不把 web/search output 自动视为可信事实；
- 不因有开源方案机械禁止 BUILD；
- secrets / private topology 不进入 public research query / durable public docs；
- 不改变 Runner lifecycle、merge/deploy/destructive authority。
