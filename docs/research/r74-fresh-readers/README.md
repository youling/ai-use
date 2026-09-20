# R74 isolated fresh-reader evidence

Artifact Version: 1.0.0

这是 [#74](https://github.com/youling/ai-use/issues/74) 的非规范性合成阅读实验。它检验 R1/R2 的当前入口与恢复语义能否被无此前任务对话的 reader 找到；不是生产项目执行、Global Architect Review 或 Lab establishment。

## 输入与独立性

- Baseline：`e6de9acdafbc3b9d12802ecf8de25f444074553b`。
- Candidate：`d38cb8aa6c74cc6a5b5f4a49ea39c3f51cf9674d`，tree `5d811690041acf9c5d2aa652ddcce1cccfad174b`。
- [预定方法和五张场景卡](evaluation-plan.json)：每格一个独立 reader，从 AGENTS.md 起步；不继承 Builder、审计、其他 reader 的对话/答案。只读冻结文档，不访问私有实例。
- current Work Order、access、target state、bounded authority 是明确的 synthetic fixture 输入；旧 context/handoff 不可用。模型判断恢复路径，不执行真实 Bootstrap 写回、项目修改、部署或 merge。

父上下文负责实验协调与结果对账，保留 #69 历史；它不伪称 fresh，也不代替最终 Global review。Builder 与各 reader 使用无父对话继承的独立上下文。研究类 baseline 在额度中断后续跑同一 reader lineage，仍只算一个样本。

发布时 logs 与七份 result 逐字保留；两份 result 的 CRLF 转 LF，以匹配 Git 文本存储。decision candidate 的 source_snapshot 字段将本地 transport 路径替换为 inert placeholder，观察、判断、计量不改。measurements 记录这些变换、原始及发布文件摘要；不发布任务 scratch 或机器路径。

## 复现读取和计量

从含上述 Git 对象的 clone 导出对应 SHA 的只读 snapshot，或创建隔离 detached worktree。每个 reader 的 log 使用不同路径；冻结后不修改 snapshot。执行同一场景卡，所有 repository content 读取经过[标准库读取器](../../../tools/fresh_reader_io.py)：

```text
python -X utf8 tools/fresh_reader_io.py --root <snapshot_dir> --log <reader_log.jsonl> read AGENTS.md
python -X utf8 tools/fresh_reader_io.py --root <snapshot_dir> --log <reader_log.jsonl> read <path> --start <line> --end <line>
python -X utf8 tools/fresh_reader_io.py --root <snapshot_dir> --log <reader_log.jsonl> list <prefix>
python -X utf8 tools/fresh_reader_io.py --root <snapshot_dir> --log <reader_log.jsonl> summary
```

读取器记录相对 path、行区间、完整文件 SHA-256、输出的 UTF-8 bytes 和时点；拒绝 snapshot 外的路径。`bytes_read_including_repeats` 包含重复请求；`unique_source_bytes_read` 对同一文件的源行去重。目录列表单列为 metadata bytes。错误范围不输出正文，不计入成功读数。

数值不包括 prompt、tool envelopes、推理或模型答案，不是 tokens/耗时。若工具 envelope 截断，读取器只能证明请求输出了多少源字节，不能证明模型实际看到了全部；对应 observation 明示截断及重读，不把这类量伪称精确认知成本。每类只有一个模型观察，差值只能说明该组场景中的方向；不是统计可靠性或一般成功率。

## 判读原则

原始 result 中 `false_blockers` 有些表示被 reader 拒绝的潜在错误门，不表示它实际被阻塞。汇总按 `can_continue`、具体解释与 source 引用逐项对账。真正适用的 Bootstrap writeback、ARCH-0、L2 ADR、required Review 不计为错误额外步骤；可选调查读取也不自动计为 mandatory hop。

每类核对五个 source-home 主题：Bootstrap、continuation/completion、recovery/context、change lifecycle，以及该类专有的 architecture/data/mutation/trace 主题。该计数验证能否找到当前 source，不代替全面语义审查；兼容路径须能说明实际 current home。

R3/R4 尚未实施。关于 GitHub 复用的回答只能在已读来源证据范围内成立，不能把 source proposal/audit canary 当已接受治理或生产权限。最终 build report 与 published-head checks 另在 #74 锚定；本目录的实验观察不会自行迁移 Work 状态。
