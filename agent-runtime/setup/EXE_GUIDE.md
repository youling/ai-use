# Windows：双击 AgentRuntimeSetup.exe

普通用户从 **AgentRuntimeSetup.exe** 开始，不需要先安装 Python、PowerShell 7、Git、Codex 或 OpenCode，也不需要进入源码目录运行命令。

本轮构建是 **UNSIGNED_TEST_ONLY（未签名测试版本）**，供精确版本审查和预览验收。下载地址、SHA256 和实际运行证据以 [#137 的最新交付记录](https://github.com/youling/ai-use/issues/137) / 对应 PR 的 Windows EXE CI artifact 为准；在产物上传前不能将源码 ZIP 当作安装包。GitHub Actions 会将可执行文件与证明文件装在一个 artifact ZIP 中：只需解压它并双击顶层的 `AgentRuntimeSetup.exe`，无需下载源码或运行 PowerShell。

**验收状态：PR #138 暂停合并。** 前一版本 `8f24f1b` 的 EXE 已实际启动，但 BOSS 首次“下一步”遇到 `EXISTING_ROOT_METADATA_INVALID`。返工版本须重新通过架构复审，再做授权的现场验收；构建成功、合成向导通过和原生只读规划通过，都不能替代 BOSS 实机首次使用结果。

## 第一次打开

1. 从当前工单提供的 GitHub CI artifact 下载，核对交付记录中的 SHA256。解压后的主文件只有一个 `AgentRuntimeSetup.exe`；其余 checksum、provenance、许可和运行截图是审查材料。
2. 双击 EXE。控制台会显示启动与内嵌运行时检查进度，然后打开中文 Textual 向导。Tab / 方向键移动，Enter 选择，Esc 返回，Ctrl+Q 退出。
3. 查看电脑检查，再选择“下一步”查看六个目录。缺少 WSL **应用**3.0 或 WSLC 时会说明运行时前提；仍可打开向导，不会自动安装、升级 WSL 或重启。
4. 本测试版本仅检查和生成计划。它没有发布者签名，任何授权参数都不能将它解锁为真实安装。实际 Host 变更、凭据连接和完整恢复仍需独立的可信分发与 Host 授权。

SmartScreen/Defender 可能提示未识别或未签名程序。不要关闭安全防护、添加全局排除或被要求绕过策略；可以等待有独立授权、签名和验收证据的发布版本。SHA256 可用于核对下载字节，不能替代发布者签名。

可选的字节核对方法：在已解压文件所在目录，用 Windows 自带命令提示符运行 `certutil -hashfile AgentRuntimeSetup.exe SHA256`，将结果与工单和 `SHA256SUMS.txt` 比较。[Microsoft 的 hashfile 说明](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/certutil#-hashfile) 指明该操作计算文件摘要；它不是启动前提，不需要 PowerShell 7。

遇到错误窗口会保留固定错误码和退出提示，不输出原始 traceback 或密钥。先记录错误码，再退出；不要清理已有数据来试图让预检通过。

已有上下文格式不兼容时，保持原目录和文件不变。将界面给出的业务角色与固定原因码交由电脑所有者核对；不要手动改删 HOST_AGENT、状态库或凭据文件。未知格式、未知所有权或危险路径不能通过重新选址绕过。

## ROOT_OVERLAP 怎么处理

这表示两个目录角色相同或互相包含，例如工作区包含配置。界面只显示业务角色、来源和冲突类别，不要求公开原始路径。

已有目录保持原位。可明确选择 **“审阅新隔离目录方案（保留已有目录）”**，查看另一个高速盘隔离命名空间的六个目录；这是新方案的预览，不是搬迁、删除或 Host 授权。冲突检查仍保留，不能通过按钮绕过未知所有权、reparse、容量或原始 hash 保护。

测试区分四类证据：二进制启动、合成宿主向导、隔离 Known Folder 的原生只读读取与规划、BOSS 实机验收。前三类使用自有合成上下文，不能据此宣称 BOSS 问题已经解决。需要排查时，EXE 的 `--diagnose-root-plan` 是用户明确发起的只读诊断：本地解析现有安装上下文，只输出角色、来源、关系和固定码，不输出路径、账号或上下文正文。不要上传原始 HOST_AGENT、认证数据库或日志。

## 内嵌来源与安全边界

EXE 沿用同一 SetupEngine、Windows Adapter、HOST_AGENT 和固定公共 OCI。冻结模式核对实际加载的 Python DLL、PSF 签名、内嵌资源/依赖锁及构建源；脚本模式继续使用既有官方 Python 签名与 hash 门禁。“内嵌内容核验成功”与“发布者可信”“真实安装已完成”是不同状态。

可执行文件默认不读取凭据库，不共享旧 OpenCode 的 auth/session/state，不发起模型推理。Windows 内置 PowerShell 5.1 仅作为固定的本地元数据/签名 helper，用户无需另装 PowerShell 7；受保护服务器凭据目录的 SID/SYSTEM ACL 验证保持。

## 开发者入口

源码 checkout 的 [bootstrap.ps1](bootstrap.ps1) 和 [V2 源码指南](V2_GUIDE.md) 是开发者回归入口，不是普通用户的安装前提。Windows 原生构建采用 [PyInstaller](https://pyinstaller.org/en/stable/) 的受锁定版本，构建和许可证明随 artifact 提供。构建产物只上传到本 PR 的 CI artifacts，本轮不发布 Stable Release、GHCR 或生产部署。
