# Human SSOT Depositor Ingress — Portable Capture Contract

**Classification: L2 Targeted Reference**
**Protocol Version: 1.0.0**
**Source:** `youling/ai-use#38`

本协议定义一种**后置、source-bound、append-only** 的 Human SSOT Capture 角色。它只解决“把当前来源可靠沉淀为一份可恢复证据”，不负责读取、理解或维护 Human 的 current canonical state。

核心边界：

```text
Depositor / Capture
  = current source -> new Deposit evidence

Curator / Human-memory collaborator
  = targeted read -> reconcile / derive / maintain current Human state

DEPOSITOR != CURATOR
```

---

## 1. Applicability

当 Human 在一次普通 Chat / Agent 工作之后，明确要求“把这段交流沉淀/投递到 Human SSOT”时，默认进入 Depositor 场景。

普通 source conversation 在投递前不需要为了未来可能沉淀而预加载 Human SSOT。Depositor 的执行依赖应保持最小：

```text
current accessible source
+ current Depositor protocol / execution prompt
+ optional authorized create-only transport
```

如果 Human 明确要求读取既有 Human state、整合多份 Deposit、去重、维护 Candidate/Canonical State，则已经进入 Curator/processing scene，不再是普通 Depositor。

---

## 2. No-read / create-only default

普通 Depositor MUST NOT 为了完成本次投递而读取：

- existing Human canonical state；
- historical deposits / records / candidates；
- private Human profile / memory graph；
- deployment database / daemon / private schema；
- unrelated project/asset current state。

原因不是这些内容不可用，而是 source-bound capture 需要避免旧 Human state 对“本次来源到底说了什么”产生注意力/解释偏置，同时缩小 private-data exposure。

写入默认是：

```text
CREATE new unique Deposit
NOT update shared canonical file
NOT dedupe/reconcile existing deposits
NOT promote candidate/current state
```

如果目标 transport 只能通过读取既有内容才能安全更新共享文件，则该 transport 不符合普通 Depositor 的 create-only 模式；应输出 portable artifact，或交给后续 Curator/Importer。

---

## 3. Source boundary

默认 `SOURCE` = 承载当前 Depositor 触发消息之前，当前会话中 Agent 实际可访问的交流内容。Human 明确指定段落、文件或时间范围时，以明确范围为准。

永远排除：

- 当前 Depositor 触发消息；
- Depositor Prompt / Protocol 自身；
- 关于 Depositor 的版本、测试、Git/PR、调试、设计理由；
- transport/path/auth 等控制说明本身（除非 Human 明确把其中一段指定为 source data）。

看不到真实 source 时：

```text
SOURCE_CONTEXT_UNAVAILABLE
```

source 存在但没有值得长期恢复的新信息时：

```text
NO_DEPOSIT_NEEDED
```

这两个结果都优于制造一份空洞或猜测性 Deposit。

---

## 4. Evidence-conservative summarization

Deposit 是**来源证据的压缩投影**，不是事实表、人格模型或推理结论库。

只记录 SOURCE 明确支持的内容：

- 不知道：省略；
- 不确定：保留不确定；
- 未表达的因果、动机、关系、稳定偏好/人格、能力、未来趋势：不补；
- 不因为两个话题相邻就推断关联；
- 时间精度只到来源支持的程度；
- 可以压缩、重排、合并明确等价重复，但不能拼出 source 从未表达的新观点。

普通 Depositor **不主动生成 `AI_INFERRED` Candidate**。

如果 source conversation 中 AI 已经提出某个分析，且对恢复交流有 material value，可以记录：

> AI 在该次交流中提出了 X。

不得把 X 改写成 Human 的事实/观点。

优先级：

```text
source-faithful narrative
 > preserved Human wording
 > explicit uncertainty
 > omission
 > invented coherence  # forbidden
```

---

## 5. Deposit shape

使用**小固定 envelope + 稀疏内容**。空章节省略，不为模板凑字段。

推荐逻辑形态：

```markdown
# Deposit

## Source
<source type / scope / pointer，只有已知时记录>

## What happened
<source-supported durable summary>

## Decisions
<optional>

## Changes / Insights
<optional；仅 source 明确支持>

## Open loops
<optional>

## Important quotes
<optional，少量>

## Provenance
- depositor_prompt: <version>
- producer/model/runtime: <known only>
- source_coverage: <known only>
- capture_status: <optional; direct | recovered | partial | uncertain>
```

`Daily Record`、`Memory Candidate`、`Canonical Human State` 都不是 Deposit 的必填层，也不是本角色的 convergence target。它们属于后续 Curator/processing。

---

## 6. Transport

Transport 只改变 Deposit 去哪里，不改变 Deposit 语义。

优先顺序：

1. Human 明确要求显式输出 / 测试 / 不回写 -> 直接输出完整 Deposit；
2. 存在**明确授权的 create-only target/transport** -> 创建新的 unique Deposit，返回 durable pointer；
3. 无 GitHub/Git/create target、或写入授权/目标不明确 -> 直接输出完整 Markdown/plain-text Deposit，供 Human 保存或后续 Importer 导入。

不得因为“有 GitHub 写 capability”就自行浏览 private Human SSOT 寻找写入位置；capability 不产生 destination/authority。

Portable fallback 与直接写入使用同一逻辑 schema，不建立第二格式。Importer 只做 transport normalization：保留原 source/provenance/`recorded_at`（若存在），另记 `ingested_at`，不得把导入时间冒充 source event time。

---

## 7. Corrections / history

Deposit 是 append-dominant source evidence。发现误记、遗漏或后续来源纠正时，默认创建新的 correction/supersession artifact 指向旧 Deposit，不原地改写历史使旧证据消失。

```text
DEPOSIT != CANONICAL CURRENT STATE
CORRECTION != HISTORY REWRITE
```

具体 private Human SSOT 的文件路径、ID/schema、索引、curation/compaction 由 deployment owner 定义，公共 ai-use 不冻结。

---

## 8. Curator boundary

Curator 可以在明确授权下：

- targeted read existing Human SSOT；
- dedupe/reconcile multiple deposits；
- 形成 records / candidates / current projections；
- 维护 Canonical Human State；
- 请求 Human 对 material conflict/meaning 做确认。

Curator 的读取/维护 authority **不会**因为一个 Agent刚完成 Depositor capture 自动获得。

`human/README.md` 提供 broader Human collaboration guidance；本协议只拥有 Depositor ingress。

---

## 9. Security

Depositor 不写入 password、API key、token、private key、MFA recovery code、完整 secret-bearing env。

对其它高敏感内容，只保存当前 source 与 Human 目标所需的最小信息；能以 authorized private pointer恢复时优先 pointer，避免无目的复制。

---

## 10. Recovery extractor compatibility

未来 source chat 因 context/provider failure 强行结束时，可以由 separately authorized Recovery Extractor 生成相同 Deposit contract，并标：

```text
capture_status: recovered | partial | uncertain
```

这不是普通 Depositor 的依赖，也不授权它读取其它 Human state来“补全”缺失来源。

---

## 11. Invariants

```text
DEPOSITOR != CURATOR
DEPOSITOR_READ_EXISTING_HUMAN_SSOT = NO_BY_DEFAULT
DEPOSITOR_WRITE = CREATE_ONLY_BY_DEFAULT
DEPOSIT = SOURCE_EVIDENCE
DEPOSIT != FACT_TABLE
DAILY_RECORD = OPTIONAL_DOWNSTREAM_PROJECTION
UNKNOWN > INVENTED_COHERENCE
AI_INFERRED_DEFAULT = NO
NO_GIT != NO_DEPOSIT
CAPABILITY != AUTHORITY
```
