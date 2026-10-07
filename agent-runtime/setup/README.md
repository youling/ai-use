# Agent Runtime 首次安装向导 — Windows WSLC V1

这是待独立 Architect exact-head review 的 Windows V1 实现。默认只检查或生成计划；运行 Host apply 还需要明确 Host authority、审阅后的计划及批准。不会通过本工单发布新镜像、升级 WSL、重启机器或操作其他 Host。

从已审查的 `youling/ai-use` checkout 根目录运行一个命令，建立当前 checkout 专属的依赖环境并打开 Textual 预览向导：

```powershell
pwsh -NoProfile -File .\agent-runtime\setup\bootstrap.ps1 -Prepare
```

不要将网络脚本直接 pipe 到 shell。脚本只从自身目录启动 Python engine/TUI，不会另下载或执行 installer engine。`-Prepare` 仅授权隔离 venv 的准备，向导没有通过这个参数获得 Host apply authority。完全不写入的检查命令：

```powershell
pwsh -NoProfile -File .\agent-runtime\setup\bootstrap.ps1 -CheckOnly
```

先决条件：Windows AMD64、PowerShell 7（`pwsh`）、一个有有效 Python Software Foundation Authenticode 签名的 CPython 3.14.x stable runtime。真正 apply 还要求 WSL **应用**版本 >= 3.0.0，实际 WSLC canary PASS、足够空间及明确的目录所有权；Linux/macOS 目前只可做合同/fixture 验证，不能 real apply。WSL 应用版本和 WSL2 内核/虚拟化架构是不同概念。

Python 缺失时，脚本返回明确 gate。审阅 [python-runtime.json](python-runtime.json) 后，可以明确授权只为此 installer 下载/安装官方 per-user 3.14.8：

```powershell
pwsh -NoProfile -File .\agent-runtime\setup\bootstrap.ps1 -Prepare -ApprovePythonInstall
```

这个参数允许执行官方 installer，并在 checkout 的 `.setup-runtime/python-3.14.8` 安装运行时；官方 installer 可能登记自己的 per-user 安装元数据。脚本不设置 PATH、launcher、文件关联、shortcut 或 all-user installation，不升级已存在的 Python。如果发现签名错误、已有未归属目录、安装目标存在或注册的 3.14 runtime 无法验证，会停止。也可用 `-PythonPath` 指定已验证的 3.14 stable interpreter；签名及版本仍需通过检查。

Python source/hash 来自 [官方 3.14.8 release](https://www.python.org/downloads/release/python-3148/)（2026-09-30）。Windows AMD64 installer 的 SHA256 为 `759be887b96e736a3ca886daf8d575f18fcae1a09efab6902f42d59e8999f8ef`。构建时实际下载并核对 hash 和有效 PSF Authenticode 签名；bootstrap 在每次 acquisition 中重新验证二者，并拒绝 HTTP redirect。已安装 interpreter 也需有效 PSF Authenticode 签名且版本为 `3.14.x final`。

依赖锁包含 Textual 8.2.8 与全部传递依赖、PyYAML、现有 Host GitHub helper 使用的 cryptography。所有允许的 wheel hashes 来自官方 PyPI JSON metadata；构建时下载的 wheel 已与这些 metadata 比对。禁止 source build；安装使用固定 PyPI index、`--require-hashes`、隔离 pip 配置和禁用缓存。没有 global pip install，也不更新系统 pip。venv 的 ready marker 绑定依赖 lock hash 和 base interpreter；漂移或 partial install 会停止。

## 同一 engine、两种入口

PowerShell 只负责 Python 来源验证、隔离 venv 和启动；`agent_setup` engine 提供 `probe / plan / apply / verify / repair` 及 rollback，CLI 与 Textual 共用它。engine 不导入 Textual；Windows adapter 提供真实 Host probe，fixture adapter 提供确定性测试。未来 Linux/macOS adapter 可消费同一个 phase contract。

屏幕流程：欢迎/预检 → 物理存储与 Host 根目录 → 目录 placement 和 overrides → GitHub identity → model/free route → 审阅/apply → verify/results。Tab/方向键/Enter/Esc 操作，中文优先，保留英语本地化入口；每步显示当前状态和无法继续的原因。

目录计划消费七域 contract，只创建已批准的 Host-managed roots。Vendor state、secret catalog、active writer、unknown/Human-unique data 会保留；`NO_MOVE` 是有效结果。V1 不做生产数据迁移。路径检查拒绝 symlink/reparse、注入及未知 ownership，真实 material migration 必须另有事务、所有权、relocatable 分类与批准。

GitHub identity 优先发现/复用现有 Host helper 或 OS-native identity metadata，向导不接受 token、PAT、App private key 等 raw 值。metadata-only `SecretReference` 可以持久化；实际 secret 留在 Host custody。没有可授权的 concrete durable destination 和 writeback/fresh recovery 证据时，必须标注 `NOT_AUTHORIZED/BLOCKED`，不能声称完整恢复。public/free model route 是可选 route metadata，不等于 paid auth 已通过。

运行时使用已发布的 exact digest：

```text
ghcr.io/youling/opencode-foreman@sha256:fa92f37752ff6132b161ed4c2563897c94b014ab70d650846dcb09f354f55261
```

通过现有 Host launcher 启动非 root、仅 loopback 的认证 server，使用 bounded exchange，只投递当前 HOST_AGENT 上下文。HOST_AGENT 放在 OS-native Documents Known Folder；可选私有 durable destination 由 owner 选择，公共实现不硬编码任何私人仓库、路径或 credential ref。

## CLI、恢复与退出

在 setup 专属 venv 已建立后，可以使用同一入口跑非交互 probe（JSON fixture 完全不接触 Host）：

```powershell
pwsh -NoProfile -File .\agent-runtime\setup\bootstrap.ps1 -Prepare -Mode cli -Fixture .\agent-runtime\setup\tests\fixtures\windows-ready.json
```

直接 CLI 可执行 `python -m agent_setup cli PHASE`，其中 PHASE 是 `probe / plan / apply / verify / repair / rollback`；需在 setup 目录运行，或设置 PYTHONPATH 指向该目录。`--fixture` 是测试输入，`--plan` 是审阅的计划，`--output` 指向 owner 选择的输出；real apply 需要 `--host-authorized --approve` 及 engine 内部 currentness/ownership gates，缺一即停止。`--runtime` 进一步请求运行时操作，不能由 readiness 推导授权。

中断或 reboot 后先重新 probe，再使用保存的无 secret checkpoint 进行 repair/resume；currentness 漂移会阻塞。不会终止现有 WSL distro、改 hypervisor 或替用户确认系统修复。network 中断、失效身份和未知 active workload 都要显示精确 gate，重新获授权后再继续。

Host rollback/uninstall 只处理该 attempt 有 ledger 的新建资源，不删除已存在目录、vendor state、credential catalog 或 Human data。默认保留 HOST_AGENT 和可恢复证据；清理先检查 owner、当前内容及使用状态。bootstrap 本身不会自动删除 partial venv 或未知目录。若 venv 安装中断，先检查 `.setup-runtime/owner.json`、确认没有 live process 和未知文件，再由 owner 清理该 checkout 的 partial venv 并重新 `-Prepare`。官方 Python 安装如中断/需移除，使用其官方 repair/uninstall 流程，另行批准；不要把 Python 安装目录当作任意 scratch 删除。

## 开发验证

测试依赖有单独完整的 [requirements-test.lock](requirements-test.lock)，引用 runtime lock。使用专属 Python 3.14 venv：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --isolated --no-cache-dir --require-hashes -r requirements-test.lock
.\.venv\Scripts\python.exe -m pytest tests
```

CI 分别在 Windows synthetic smoke 与 Linux contract runner 验证；fixture 和 TUI tests 不做 live mutation。真实 Windows canary 必须绑定 exact Host authority，证据需脱敏后回写工单，不能将私人实例路径、身份或数据提交公共仓库。

## V1 验证边界与 owner helper

WSLC preflight 的 `ps` 探针只证明原生控制面 metadata 访问。真正 runtime
canary 必须在已批准 apply 后，通过固定 OCI pull、既有 launcher 和非 root
context/image readback 另行成立；不能把 metadata PASS 当作容器启动 PASS。

GitHub native login discovery 不会把 Human PAT 转交容器。现有
[Host provider](../host/windows/project_github.py) 的 custody 实现仍由 Host owner
管理；V1 setup 通过 owner 批准的适配器消费它，不直接读取原始 App key 或 token。
适配器必须提供固定 `status --json`、`writeback --json`、`verify --json` 协议。
状态字段仅为 state、repo、work、projection_directory/server_env 引用及
context_sha256/durable_destination；writeback 还必须证明 private_destination=true。
verify 必须返回 authenticated_api/github_read/github_write/fresh_recovery 严格布尔证明，
绑定同一 repo/Work/context hash。此协议不是新身份或 privilege broker；没有
Host owner 已提供的适配器时，相关步骤保持 NOT_AUTHORIZED，向导不安装 unrestricted
App/PAT，也不把字符串引用或勾选授权当成验证证据。内置 project_github.py 的原生
CLI 与此 metadata 协议不同，不能直接当作该可执行适配器调用。

当前版本没有 bundled native-keyring-to-runtime 或 model-provider OAuth 适配器。
Model helper/reference/free-route 仅为 owner 选择输入，尚未做有效 provider/价格
readback 时状态为 NOT_AUTHORIZED；不会进行付费或免费 inference。完整认证
first-run 与真实 fresh recovery 要在具体 Host owner 适配器/权限具备后验收。

中断事务在 config root 的 `.agent-runtime-setup/plan.json` 保存完整无 secret
审查方案。先 `repair` 查看恢复理由，再显式批准同一计划重试；apply/rollback
共享独占锁。未知/stale lease 不会自动删除。Rollback 遇到 READY/PASS 的 live
runtime 会要求先按既有 launcher 的 owned-stop 机制停止，避免删掉其 context。
Uninstall 只删除 ledger/marker 证明的新建、仍无唯一数据的内容；journal 保留。
