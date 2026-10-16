# #143 文件夹选择验收边界

施工基线：`main@ebba67e26042f28d56ecefc64443cfd4ab3fd242`，工作项 [#143](https://github.com/youling/ai-use/issues/143)。沿用 SetupEngine、WindowsAdapter、HOST_AGENT、冻结来源检查与公共不可变 OCI；本轮不增加安装引擎或 Host 权限。

自定义成功路径修复基线为合并 PR #144 后的 `main@ba20a59e0799b5e1bf257c34a1336d8d99eb58ec`。新隔离 UI 的原生选择器只选择现存父目录，四项输入为新子目录名称；通过原 `propose_isolated_roots` 生成独立作用域，再由原 `plan` 核验实际四项路径和 Exchange。验收必须核对自定义名称被采用、合法重新选址保留名称、两项 Skip 到最终审阅且退出前未创建安装根。仅证明越界输入被拒绝或弹窗能打开，不构成自定义成功。

交付必须绑定当前 PR 的精确 HEAD、完整 CI、真实 EXE artifact 和 SHA256。尚未上传的文件不得称为可下载产物。本说明不以旧版 CI 或本机工程构建替代新候选证据。

| 验证层 | 验证内容／适用条件 | 结论范围 |
| --- | --- | --- |
| 原生对话框 | Windows 文件夹模式、STA 生命周期、取消、固定错误、焦点返回 | 原生 chooser 的实际运行与可用边界；单独报告真实运行或 seam |
| 生产链及 chooser seam | 实际 WindowsAdapter → probe → 已有公开 V1 → plan → Textual，仅 chooser 返回自有目录或取消 | 公共旧状态下的选择、取消、键盘和重规划；不声称真实用户目录已通过 |
| 冻结 EXE | 同一 CI 字节在空外部依赖 PATH、任意工作目录下执行；picker 模块与源码 hash 纳入资源核对 | Bundle 执行、资源定位和指定公开输入矩阵 |
| Builder 实机 | 仅在实际 Host 的独立授权范围内，用同一交付字节走预授权路径；否则标 NOT_EXERCISED | 当前获准设备的预授权路径；不替代 BOSS canary；旧版 #137 结果不转移到新字节 |

受控输入覆盖 fresh 和带分类说明的有效 V1、自动推荐与自定义、键盘 Browse、取消保持原方案、新父目录下的独立子作用域、范围外选择拒绝、未知 owner、reparse、容量和 protected-root 冲突。只使用公开合成上下文及测试所有的临时目录；既有文件必须保持 hash，预览不得创建安装目录。选择成功后必须清除旧确认并通过原引擎重规划；取消不得修改确认。

证据分开报告：`NATIVE_FOLDER_DIALOG`、`CHOOSER_SEAM`、`FROZEN_BUNDLE_EXECUTION`、`BUILDER_PREAUTH_JOURNEY`、`BOSS_CANARY`。注入 chooser 返回值不能被称为实际 Windows 对话框通过；合成宿主不能被称为 Builder 或 BOSS 的真实安装成功。Host Apply、凭据连接、模型认证、恢复、签名发布和合并仍有各自门禁。

对话框使用每次独立的 Client GUID 和 `DONTADDTORECENT`，并尝试清除该私有客户端状态。`ClearClientData` 未能验证时如实记录 `HISTORY_CLEANUP_UNVERIFIED`；这不将正常选择或取消变成失败，也不代表已审计或清除了 Windows 全部 MRU／Shell 历史。[Microsoft Common Item Dialog](https://learn.microsoft.com/en-us/windows/win32/shell/common-file-dialog)、[SetClientGuid](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifiledialog-setclientguid) 和 [ClearClientData](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifiledialog-clearclientdata) 是本边界的接口依据。
