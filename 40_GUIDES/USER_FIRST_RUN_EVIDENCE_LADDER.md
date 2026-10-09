# User First-Run Evidence Ladder — 从“CI 绿灯”到“用户真正可用”

**Classification:** L2 Diagnostic / Recovery Guide
**Source issue:** [#139](https://github.com/youling/ai-use/issues/139)
**Evidence donor:** [INCIDENT-0002](INCIDENTS/INCIDENT-0002_SETUP_FIRST_RUN_REAL_WORLD_GAP.md)
**Applicability:** installer、OCI/Agent runtime bootstrap、Windows/Linux setup、GUI/CLI onboarding、旧数据迁移、首次部署、跨设备冷启动。
**Authority:** 本文是适用场景的验证实践指南；不新增发布/合并/Host 授权。canonical verification/Incident owner 是 [CONSTITUTION §5–8](../CONSTITUTION.md)，继续执行 [Agent Interface 的完成边界](../docs/AGENT_INTERFACE.md)。项目具体 acceptance/authority 以 current Work 与 owner contract 为准。

## 1. 验证的对象是交付承诺，不是“运行了多少测试”

同一个版本可以同时存在如下事实：Python 单测通过、合成环境第一屏可点击、真实冻结 EXE 正常启动、真实 Windows 旧目录规划失败。各项都可能为真；严禁因前一项为真推出后一项也为真。

| Evidence level | 验证对象 | 可以声明 | 不能据此声明 |
| --- | --- | --- | --- |
| E0 — Source | unit/property/contract + negative fixtures | 某一 source behavior 在限定输入下通过 | Windows 安装器可用 |
| E1 — Synthetic integration | 同一引擎多组件，在模拟 OS/状态运行 | 指定 synthetic state 的核心流程通过 | 真实 OS/文件系统差异已覆盖 |
| E2 — Artifact execution | 从 **交付的 exact EXE/镜像**实际启动、提取/校验资源、交互、退出 | 特定机器/runner 上二进制能运行 | 用户已有目录/凭据可安全使用 |
| E3 — Native read-only journey | 真实 packaged entry、真实 OS metadata/adapter → `probe → plan → TUI Next`；用隔离、合成的旧配置注入到**边界输入**，不能替换待测核心逻辑 | 指定 Windows/Linux 原生只读首次使用流程通过 | 指定用户的 BOSS 或其它宿主已通过 |
| E4 — Owner-machine canary | Human 明确同意、真实目标机器、受限只读预检 / 真实原有状态 | 该机器、该版本、该阶段现场验证通过 | Host apply 或模型认证已授权 |
| E5 — Host effect & connected use | 独立精确 Host 授权后的真实安装、归属/隔离/回滚、GitHub/model auth、fresh recovery 分项 | **按实际 proof** 分项完成 | 一项授权或 PASS 自动代表其它能力 |

每次验收结论至少能回答：`artifact_sha / source_exact_head / environment_class / input_state_class / entrypoint / actual_steps / assertions / negative_cases / proof_pointer / unresolved_gates`。历史构建绿灯不得替代新 HEAD。不能把 E1/E2 写成 E3/E4；任何还未验证的能力必须标为 `NOT_VERIFIED` 或等价清晰状态。

### 正反例

- ✅ “`AgentRuntimeSetup.exe` 在 Windows runner 实际启动成功，测试 SyntheticWindowsAdapter 的 1→2 通过；BOSS 存在历史目录的 1→2 尚未测试。”
- ❌ “Windows EXE CI 通过，因此 BOSS 可以正常安装。”
- ✅ “`-CheckOnly` 仅验证内嵌内容 hash；真实 WSLC、原生目录规划、GitHub 凭据另行验收。”
- ❌ “固定镜像已经拉取，所以 GitHub 恢复/模型调用也 READY。”

## 2. 必须贯穿生产依赖链，允许替身，但替身应在明确边界

面对真实安装器，将关键执行路径表达为可审查的阶段：

```text
发布产物 EXE/CLI
  -> provenance / signature / host-authority gate
  -> shipping OS adapter / Windows Known Folder / volume probe
  -> shipping SetupEngine.probe
  -> existing-context classified read (version/schema/owner)
  -> shipping SetupEngine.plan
  -> Textual NEXT to placement / actionable blocker
  -> (separate Human gate) Host apply
  -> (separate actual proof) OCI / credentials / model / durable recovery
```

测试可以在非用户机器以 **隔离测试账户、合成 Documents 及合成历史文件**替换 OS 边界的数据；但若验收要求走完整路径，就不能在中途替换整个 `WindowsAdapter.probe` 为固定 `existing_roots={}`，再把结果称为 `NATIVE_READ_ONLY_PLANNING_PASS`。部分模拟是必要的，但应明确标出替身位置、被跳过的阶段和结论适用范围。

对于打包产品，应测试 **真正交付二进制**，而非开发机 Python 脚本替代。验证资源定位、发行内容完整性、Windows 路径语义、PowerShell/系统 API、退出码、双击可见错误与清理，不能只看 EXE 文件存在或哈希正确。无签名包的内容完整性≠发布者可信，不能假造签名/Host authority。

### 2.1 Builder Host Self-Canary — 施工者先亲自试用交付物

当任务依赖真实宿主机（安装器、容器/Agent 首次安装、Host 环境纳管、GUI/CLI 包装、已有本地状态迁移）时，Builder/Foreman 应在**自身实际获准使用的执行设备**上先进行一次**真实用户路径的授权前自金丝雀**，再提交 Human 做目标设备 canary。这是现有 E2/E3 对施工者的适用约束，不自动晋升 E4/E5，也不要求普通纯仓库编码任务扫描整台电脑。

- **先探当前宿主机，再选布局。** 使用真实 OS/volume/WSL/WSLC/文件系统、Known Folder、已存在目录的非敏感分类、vendor/native 软件与端口、空间/权限状态。当前工作站观测只能证明**当前工作站**；由每台新设备上的 Codex 重新 probe 并检查历史 Host projection 的漂移。复用七域语义与选址算法，不硬编码上一台机器的盘符、硬件、缓存路径、账户或凭据引用。没有合法访问能力则标 `SELF_CANARY_NOT_AVAILABLE`，不能凭假想事实宣布 PASS。
- **用最终交付原字节执行。** 基于 exact HEAD 构建 EXE/容器，验证 hash/provenance，在施工者的真实本机启动**同一可交付字节**，顺序操作电脑检查、位置规划、账户发现/可跳过的安全连接界面、最终变更审阅。包括旧配置/目录、真实操作系统路径/重定向；不能把 shipping `WindowsAdapter → SetupEngine.probe → existing-context → plan → Textual` 链路替换为 `existing_roots={}`，再声称施工者真实自金丝雀。可额外使用受控 synthetic fixtures 扩大设备和旧版本状态覆盖，但必须分别标注。
- **停在授权边界而非凭直觉认为“没按 Apply 就只读”。** 逐步核对 probe、缓存、日志、释放临时文件、浏览器登录和准备阶段是否已发生副作用；只有当前 authority 明确允许的只读操作和限域临时状态可以自动执行。保留原生程序、真实账号、用户唯一数据、旧配置和未知 owner；禁用自动凭据读取/付费调用/实际 Host apply。若前置步骤本身会修改持久状态，应先隔离成受控 fixture 或停在该动作前，并将 `SELF_CANARY_BLOCKED_BY_AUTHORITY` 如实交付。临时环境须说明所有权、边界、清理结果。
- **在交付中报告证据与缺口。** `source_head`、`shipping_artifact_sha256`、`builder_host_class`、`host_probe_observed_at`、`builder_native_first_run_steps`、`blocked_reason_code`、`host_effects`、`owner_machine_canary` 应各有明确状态，避免暴露真实目录、主机身份、登录账号、原始 HOST_AGENT 内容或密钥。施工者工作站 PASS ≠ BOSS PASS；没有 TUI/GUI 交互工具时，描述可验证的 CLI/非交互证据及未验证的界面步骤，不能假称点击过。
- **限制向 Human 发出“再下载试试”。** 真实首次使用已连续失败时，必须先使新故障变成合成旧状态/原生生产链的回归反例，经过 exact-head 完整 CI、真正冻结产物自金丝雀与独立审查后，才请求用户执行下一次精确版本的最小现场验证。

这不创建新的 Host Profile、SSOT、发布权限或审核角色。宿主机语义仍归 [Human Host Environment](../30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md)；authority / verification 继续归 [CONSTITUTION](../CONSTITUTION.md) 与当前项目 owner。实际案例见 [#137](https://github.com/youling/ai-use/issues/137) 和 [#141](https://github.com/youling/ai-use/issues/141)。

## 3. 首次使用输入矩阵：测试用户历史，而非只测试开发者空机器

下面是 Installer/Agent/Container 产品的推荐最小环境基线，按项目 applicability 调整，不要求所有项目机械覆盖每项：

| 维度 | 必须有的正例 | 有代表性的反例 |
| --- | --- | --- |
| 使用历史 | 全新、已有有效 V1/V2 | 历史 schema、半写入/残留状态、类型不兼容 |
| 路径/所有权 | 新的隔离安装根、已归属的旧根 | 同一路径、父子包含、未知 owner、junction/reparse、大小写斜杠变体 |
| Windows/存储 | 真实 `C:\` volume anchor；SSD 规划；Known Folder | D/E 混合 HDD/SSD、磁盘空间不足、OneDrive Documents、网络盘与 root 拒绝 |
| 现有软件 | 原生 OpenCode 保留、离线只读 | 端口冲突、活跃工作区、已登录但不可投影的身份 |
| 身份/网络 | 各组件缺失时仍可安全本地预览 | 伪登录、过期/撤销 token、未授权付费调用、断网 |
| 持久化/恢复 | 当前版本 context/marker/journal | 损坏配置、stale hash、冲突 ownership、中断恢复与回滚 |

**Legacy fixture 是一等公民。** 只在 fresh root 跑绿灯不能覆盖“原生程序已经用很多年”的机器。每个发现过的现场原因码，应归入上述矩阵，并固定为不含真实用户信息的最小重放 fixture。若仍不知道哪个真实字段触发错误，明确写 `ROOT_CAUSE_UNKNOWN`；不能编造一个看似类似的 synthetic fixture 就宣布闭环。

## 4. 错误必须可行动，并使用户数据继续安全

诊断输出默认最多包含：

```text
phase
stable reason_code
affected logical roles (workspace / config / exchange ...)
source class (new_default / existing_context / user_override)
relation or schema category
safe next action
scope: READ_ONLY | HOST_APPLY_NOT_AUTHORIZED
```

默认**不要输出**真实磁盘完整路径、旧 [HOST_AGENT.md](../50_TEMPLATES/HOST_AGENT_CONTRACT.md) 原文、token、账号、旧软件私有状态、stack 和任意 upstream exception。只有 owner 在受信任本地界面显式展开、且敏感值经二次脱敏，才允许额外显示必要细节。不能通过自动删除、重设权限、移动原生 state、关闭安全校验来绕过异常。

典型正常结论：`PREFLIGHT_BLOCKED/EXISTING_ROOT_METADATA_INVALID` + `role=exchange` + `reason=UNRECOGNIZED_SHAPE` + “保留已有配置，进入只读隔离目录审阅 / 请求所有者修复”，而不是 “OPERATION” 或整屏 Python dict。

## 5. 候选放行、失败升级与避免 Human 反复试错

对于真实用户导向的安装器，发出“请下载下一个版本”建议之前，应完成：

- 冻结 source exact HEAD，并确认针对该 HEAD **所有项目要求的 checks 均成功**；失败或 pending 不被上一版绿灯替代。
- 下载/回读 CI 交付的 **同一字节 EXE/镜像**，验证 checksum、构建 provenance；必须区分 source tests、artifact run、native read-only pipeline、用户现场 canary。
- 运行旧版有效/旧版异常状态矩阵的正反例。现场故障对应至少一条固化回归；不能用 `existing_roots={}` 覆盖已有配置问题。
- 审核独立权限边界：预览≠真实安装，二进制内容验证≠发布者签名，GitHub 和模型认证≠基础容器已就绪。
- Architect 独立 exact-head Review 后，才可按权限 merge；原用户实例的新版本 canary 仍需要 Human 选择是否测试，并记录真实结果。

**候选节流建议**：同一用户设备连续两次遇到阻断首次使用的真实问题后，默认先暂停继续让 Human 下载试错。Builder/Foreman 应先补 native integration、历史状态 fixture、完整根因诊断和独立证据；只有测试盲区被明确缩小后才恢复向 Human 请求少量有效的最终测试。这是测试策略，不是新增宿主机权限。

## 6. 机器可读验收证明（示例，字段非新协议）

```yaml
source_head: "<exact commit>"
artifact_sha256: "<published EXE exact bytes>"
check_set: "full required CI cohort"
ci: PASS
artifact_exec: PASS
synthetic_host_wizard: PASS
native_readonly_planning: PASS
owner_machine_canary: NOT_VERIFIED
host_apply: NOT_AUTHORIZED
github_connected: NOT_VERIFIED
model_ready: NOT_VERIFIED
fresh_recovery: NOT_VERIFIED
known_limits:
  - "No live existing-user metadata evidence"
next_gate: "Human-selected BOSS read-only canary"
```

每个 `PASS` 均应有可复现证据指针。一个局部 FAIL 不应被聚合状态“总体通过”掩盖。数据在 PR / Work review 证据内维护，不新建与 Git/GitHub 竞争的 registry。

## 7. 为什么沉淀在这里

这份 Guide 把 [CONSTITUTION 的 evidence > self-report](../CONSTITUTION.md) 原则映射到 Installer/Runtime 可验证的工程动作；[INCIDENT-0002](INCIDENTS/INCIDENT-0002_SETUP_FIRST_RUN_REAL_WORLD_GAP.md) 保存其真实证据。它不修改 L0、不增设双验证角色，也不让 Reviewer 自行授予 Host apply。

当前实施例：[#127](https://github.com/youling/ai-use/issues/127)、[#137](https://github.com/youling/ai-use/issues/137)、[PR #138](https://github.com/youling/ai-use/pull/138)。今后 GhostFleet 新终端一键纳管、NAS/Host 初始化、其它产品的首次使用都可以复用“证据梯级 + 用户历史状态矩阵 + 真实入口”方法，需结合各项目 owner 的安全与验收范围。
