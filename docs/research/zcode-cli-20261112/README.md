# ZCode CLI 接入实测与排障记录（2026-11-12）

**L3 / NON-NORMATIVE / PROBE_FAILED_NO_MODEL_REPLY**。这是 [#183](https://github.com/youling/ai-use/issues/183) 跨执行器研究的后续实例，不是运行器认证，也不是可直接照搬的成功启动手册。本轮采用 DIRECT 文档记录；没有制造 Foreman CLAIM 或终态事件。

## 已有资料

仓库已有 [跨执行器工头经验](../multi-runtime-foreman-20261106/README.md)，其中 ZCode 路线仅证明入口探查，未证明真实模型施工。本轮在 main `8a73ecef71a4a87df5022537692a79f5c8a617f2` 的递归路径检索和该研究复读中，未找到独立、已验证的 ZCode CLI 操作指南；这不等于历史上从未存在记录。

供应商已提供 [官方 CLI 指南](https://github.com/zai-org/ZCode/blob/b95ebaffeab641907b38652f45c1502bd762972d/apps/zcode-cli/docs/usage/README.md)。该指南面向源码构建，不能据此推定桌面应用携带的 bundle 资源齐备。

## 本次实测基线

| 项目 | 观察 |
|---|---|
| 环境 | Windows，PowerShell 7.6.9，Node.js v24.15.0 |
| 入口 | 桌面安装目录中的 `resources/glm/zcode.cjs`，通过 Node 调用 |
| CLI 版本 | `0.17.1`，与桌面程序版本分别记录 |
| CLI SHA-256 | `26785f28ab8fb9f8b0f3821f2bf71d294f4d0b8bf28108785292f86c7e14090d` |
| packaged provider config SHA-256 | `ef3d64656cb5281cce292b77ef12e96b5251582cfb00cdf9eb08e3d4565abb69` |
| 请求的模型 | `account:bigmodel-start-plan/GLM-5.3-Flash`；仅为请求配置，未证实实际模型路由 |
| 权限模式 | 显式 `plan`，普通 canary 还移除所列工具 |
| 任务输入 | 固定无业务内容的短回复 canary |
| 改动范围 | 作业私有选择配置与诊断文件；未改全局配置、登录凭据或安装 bundle |

`--version`、`--help`、`doctor --json` 成功只证明入口元数据。没有将它们算作模型调用或工具执行通过。

## 探针结果

| 探针 | 实际结果 | 解释边界 |
|---|---|---|
| Node 直接运行 bundle 的普通 prompt | 缺少 builtin provider config 定位 | 桌面安装布局与该 CLI 的默认寻址不相容 |
| 进程级指定 `ZCODE_BUILTIN_PROVIDER_CONFIG_FILE` | 不再报原寻址错误，普通 prompt 仍 `Select a model before sending a message` | 只修正了定位层 |
| 同时指定作业私有 `ZCODE_PERSONAL_PROVIDER_CONFIG_FILE`，写明 provider/model | 同样失败；stdout 无真实模型结果 | 不能将配置文件写入当成配置生效证明 |
| headless `/model account:bigmodel-start-plan/GLM-5.3-Flash` | 同样在选择模型前失败 | 此安装不能凭该调用建立可用会话 |
| 终端 TUI 入口 | `Cannot find package '@zcode/tui'` | 该桌面 bundle 缺此入口需要的依赖；未修改或补丁化安装包 |

普通 prompt 失败路径还出现 `ERA_NEGOTIATION_FAILED`，内容为关闭 transport 时的 `server/discover` probe 错误。本轮不能证明它是未选择模型的根因，也不能据此推断账户无额度、OAuth 失效或供应商拒绝服务。

所有模型 canary 均未取得可核验回复。没有用其他运行器产物冒充 ZCode 成果；未执行 HT 代码任务。

## 可以复用的排查方法

1. 分别记录桌面版本、CLI 版本、Node/系统版本与产物 hash；先核对真实 `--help`。同版本号也可能有不同 bundle、模型目录和资源。
2. 把启动分成入口、配置定位、模型选择/账户上下文、真实模型回复、受限工具产物五步；停在哪一层就报告哪一层。
3. 本例可以通过**本进程**的 builtin 配置路径消除寻址错误；这不是完整修复，不应作为“已打通”模板。不得修改安装包、伪造 entitlement/header 或导出登录密钥来强行接通。
4. 官方当前配置把个人 provider/model selection 与 CLI 运行配置分开。旧配置仅在个人文件不存在时尝试一次导入；继续改 legacy `model` 不保证切换生效。本例 legacy 有模型名而当前个人默认为空，只是诊断线索，并未证实最终根因。
5. 选择配置放任务私有文件，进程退出即解除环境覆盖。不要删除用户 v2 配置来反复强制迁移。JSON 语法正确也不保证选项、provider、登录连接和运行入口都有效。
6. `--prompt` 缺省权限是 `yolo`，因此明确指定适合任务的模式。`plan` 与工具移除都不是操作系统隔离；`--disallowed-tools` 移除整项工具，不能把 `Bash(git *)` 当命令级白名单。
7. 不套用别家 CLI 的 `--model`、`--allowed-tools` 等参数。这里的 `/model` 是 slash command；官方主线说明与已安装产物的实际表现需要分别记录。
8. stdout、stderr、退出码分别保存。本例 stderr 可含很长的 bundle 源码行；对外只保留错误类别，完整诊断留实例 owner 私域。
9. 接入探针没有通过时，业务可以沿已授权、已验证的其他执行路线推进；不让候选执行器长期占据项目关键路径，也不宣称已经使用其模型。

官方详细说明：[参数](https://github.com/zai-org/ZCode/blob/b95ebaffeab641907b38652f45c1502bd762972d/apps/zcode-cli/docs/usage/02-cli-reference.md)、[配置](https://github.com/zai-org/ZCode/blob/b95ebaffeab641907b38652f45c1502bd762972d/apps/zcode-cli/docs/usage/03-config.md)、[排障](https://github.com/zai-org/ZCode/blob/b95ebaffeab641907b38652f45c1502bd762972d/apps/zcode-cli/docs/usage/12-troubleshooting.md)。以上为查阅当时的固定源码版本；本例二进制构建提交未知，不把两者等同。

## 证据保管与接续

作业选择配置、原始失败日志和安全回执已复制至实例 owner 的中心私有作业目录，逐文件比较字节与 SHA-256。公共仓只记录方法、供应商版本和错误，不包含节点地址、私人目录、会话标识、凭据或客户正文。

下一步应由 CLI/安装包 owner 验证完整的官方 standalone 交付、账户连接及模型选择初始化。需要正常官方登录时走其受支持流程；不因桌面已登录而复制密钥，也不把此处未知归因包装为人类必须重新登录。

通过标准：无副作用真实回复 → 一个受限合成文件/测试产物 → 独立回读，三者完成后再承接业务代码。当前 **NOT_PASSED**；并发规模、费用路由、无人值守与远端部署均未验收。
