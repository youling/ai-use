# INCIDENT-0002 — Installer CI PASS / first-user BOSS still blocked

## Summary

**Observed window:** 2026-10-08 → 2026-10-09  
**Work:** [ai-use #127](https://github.com/youling/ai-use/issues/127) (Windows WSLC Textual installer); [#132](https://github.com/youling/ai-use/issues/132), [#135](https://github.com/youling/ai-use/issues/135), [#137](https://github.com/youling/ai-use/issues/137)  
**Fault class:** real-user first-run integration gap; evidence overclaim risk; historical user-state not exercised  
**Incident case status:** RECOVERY_IN_PROGRESS / LIVE_USER_CANARY_NOT_PASSED. Any later acceptance must be reported from current Work/evidence, not inferred from this case.

真实用户尝试安装公开 OCI OpenCode Foreman Runtime。基础系统检查通过、公共源码测试通过，甚至交付了可双击的真实 Windows EXE，但用户在**第一步点击下一步**时连续遇到阻断。问题不等于“EXE 没编译出来”：主要失效发生在 native probe、历史状态读入、目录规划之间，测试误将较弱证据写成较强用户就绪结论。

## Observed facts / what is actually known

| 轮次 | 有效证据 | 现场问题 | 状态 |
| --- | --- | --- | --- |
| V1/V2 启动 | BOSS 上确认 Python、WSL/WSLC、存储基本检查 | 初版 Textual 显示原始 Python 字典、helper/Work 内部字段，小白用户不易配置 | V2 UX 后续修复，凭据桥接仍属独立门禁 |
| PR #133 V2 | 合成 Textual 页面与 Windows/Linux CI PASS，四阶段和独立能力状态落地 | 真实 BOSS 第一屏下一步出现 `[OPERATION]` | 代码审查指出 volume-root 安全用途混淆 |
| #135 / PR #136 | `plan().volume_for` 原来把 Windows volume anchor 传给禁止安装目的地根目录的 `safe_path`；最小修复/Windows CI 后合并 | 随后 BOSS 实际返回 `[ROOT_OVERLAP]`，不是已经能进入第二屏 | 根目录用途问题在源码层收口，现场其它阻断尚存 |
| #137 / PR #138 首批 EXE | 真实 frozen EXE 被构建运行；提供未签名预览版、checksum、8 项 CI 成功报告 | Human 在 BOSS 实测，预检 4/4 PASS 后第一步返回 `[EXISTING_ROOT_METADATA_INVALID]` | PR #138 Architect Review **HOLD**，未合并（记录时） |
| #138 后续施工 | 现有 Codex 工头持续在原 PR 修复真实 frozen/native probe，收敛 V1/旧状态/Windows 资源和签名探测 | 目标 BOSS 用户再次进入第二屏、真实安全安装尚未验收 | latest head/CI 持续变化，应 live-fetch，不用本事件文字当 current SHA |

**直接源码证据（而非对 BOSS 字段的猜测）**：`exe_main.py::frozen_self_test()` 的 frozen EXE self-test 调用 `SyntheticWindowsAdapter` 并固定 `existing_roots={}`，以此证明的只是合成环境 TUI `1→2`；而另一条真实 `readonly_native_bundle_scan()` 只调用 `WindowsAdapter.probe()`，没有贯穿 `SetupEngine.probe → plan` 的旧版配置处理。因而原 CI 全绿并不包含用户被阻断的路径。证据见 [PR #138](https://github.com/youling/ai-use/pull/138) 的 Architect review id `5461562877`、[#137 comment](https://github.com/youling/ai-use/issues/137#issuecomment-6067062968)。

**不能由当前证据断定：** BOSS 的哪一项真实 `HOST_AGENT` 字段导致 `EXISTING_ROOT_METADATA_INVALID`、旧文档是否已损坏、是否真的存在目录冲突、或 Codex 最新未复测候选已经解决 BOSS 现场问题。不得依赖猜测强行消除异常。

## Impact

- Human 每轮下载 ZIP/EXE、切换工作站/BOSS、点击第一页，成为施工团队低价值的手工集成测试器；
- 工程周期损失集中在“CI 测的环境状态≠用户机器的历史状态”；
- 若为了通过而移除 `ROOT_OVERLAP`、未知 owner、reparse 或 Host apply 门禁，可能从 UX 问题升级为真实数据安全问题；目前没有证据显示发生未经授权写入；
- 发布说明和 PR 的 `PASS` 粒度容易误导——真实二进制能启动，不说明旧数据兼容。

## Diagnosis and confidence

- **已通过代码确认：** 第一批 Windows `safe_path` 同时承担写入目的地验证与读盘符 inventory anchor 两种不兼容用途；适用隔离后修源码。
- **已通过代码确认：** EXE 的真正第一屏合成验收绕过了 `existing_roots` 的生产路径，因此不足以证明含用户历史配置的安装能够正常继续。
- **仅有明确症状，根因未现场证实：** BOSS 具体 `ROOT_OVERLAP` 的两个角色和 `EXISTING_ROOT_METADATA_INVALID` 的字段种类。需要受保护的本地只读角色/类别诊断，不得上传原始路径/账号/密钥。
- **与失败无关的真实事实：** Python/WSL/WSLC/容量预检通过，不意味着注册元数据、历史文件、签名、冷启动、网络化 Agent 或模型凭据已验收。

## Recovery / mitigation (safe and bounded)

1. Human 设备停止重复试未审新候选；保持原生 OpenCode、凭据、历史 `HOST_AGENT` 与工作区不变，禁止移除/强行覆盖。
2. 每次现场阻断记录 `version / stage / finite reason code / redacted role-category`；把事实、推断、未知分开，放回 owner GitHub Work。
3. Builder 用公共合成有效 V1/历史变化/坏 metadata/OneDrive/路径大小写/未知 owner 构建回放；出现现场原因码时**先补一个能失败的 regression**，再修逻辑，不让抑制异常冒充修复。
4. Frozen EXE 的 E2 与完整原生 E3 证明必须分开；E3 使用用户可下载的 exact EXE，走 Windows native adapter → engine probe → existing context → plan → TUI。Fixture 限定于受控 OS 边界而非整个核心适配器替身。
5. 精确 head 全部相关 CI 成功 + artifact 原字节 hash + runtime/existing-state 反例通过后，Architect Review 才考虑代码合并；随后独立征求 Human 进行**一次有明确验证价值的只读 BOSS canary**。
6. 本地容器安装、GitHub/模型凭据、真实 Host apply、私有持久恢复是独立权限门禁。不能从 E3 成功自动声明 E4/E5 成功。

## Validation / known limits

**Validated:** 真实用户截图明确证明多个版本无法完成首次 Next；源测试/新 EXE 的 synthetic/native-path 替身界限在代码中可直接核查；PR #136 精确 Windows CI 曾通过，但现场仍发现下一类阻断。  
**Not validated:** BOSS 最终通过的 exe SHA、真实 Host apply、原有 OpenCode 与新容器共存运行、任何实际 OAuth/keyring/model/fresh GitHub recovery。

## Reusable playbook and canonical pointers

对于任何 Agent 开发的新安装器，先打开 [User First-Run Evidence Ladder](../USER_FIRST_RUN_EVIDENCE_LADDER.md)，核对当前交付承诺属于 E0–E5 哪级；再沿用户实际入口列出**真实依赖链 + 最小旧状态矩阵**。真实用户连续失败后，先让 Agent 在 CI 和隔离 Windows 主机中证实生产路径，而非继续要求 Human 反复下载尝试。

- [ai-use #127](https://github.com/youling/ai-use/issues/127) — 原始安装器 owner / real BOSS gate
- [ai-use #132](https://github.com/youling/ai-use/issues/132) · [PR #133](https://github.com/youling/ai-use/pull/133) — V2 UX/离线 staged source
- [ai-use #135](https://github.com/youling/ai-use/issues/135) · [PR #136](https://github.com/youling/ai-use/pull/136) — read-only volume anchor repair
- [ai-use #137](https://github.com/youling/ai-use/issues/137) · [PR #138](https://github.com/youling/ai-use/pull/138) — 真实 EXE/历史目录 repair, active owner
- [ai-use #139](https://github.com/youling/ai-use/issues/139) — 沉淀指南与事件本身
- [CONSTITUTION §5–8](../../CONSTITUTION.md) — evidence、verification 与 Incident canonical semantics

此文件是事件 donor evidence，不是新权力、第二 Work state，也不覆盖后续真实现场验收。
