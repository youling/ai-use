# Magpie → ZCode Start Plan：HT 工头 CLI 接线实测（2026-11-12）

状态：`BOUNDED_CLI_ROUTE_VERIFIED`。本页为 L3 非规范性经验，DIRECT 集成验证；不注册新的总工头、Work 或生产网关。

## 结论与范围

本机既有 Magpie 可以给 OpenCode CLI 提供智谱模型。本轮实际跑通 `OpenCode 2.2.7 → 本机 Magpie 0.1.3732 → zcode/GLM-5.3-Flash-Trial`，模型输出和网关使用记录相互对应。OpenCode 是执行客户端，赠送额度消耗路由是 ZCode，不是 Beam、ChatGPT 或另一个普通 BigModel API Key。

这没有修复 [裸 ZCode CLI 的既有启动问题](../zcode-cli-20261112/README.md)，也没有验证并发上限、长任务可靠性或 JG 远程调用。Human 最新指示为效率优先：北京时间 2026-11-12 09:00 前尽量利用有空位的智谱赠送资源，但不限于某一个模型；Magpie 内已授权的免费模型均可补位。OpenRouter 免费资源先用于独立单任务，复杂工头能力另行验证。额度与可并发数要分别判断，过期后重新核验，不能把临时偏好固化为永久默认。

## 固定版本与现场

- Magpie 可执行文件：`E:\下载\软件\magpie-windows-amd64.exe`，版本 `0.1.3732`，SHA-256 `af8649bb5253677c18e68d493236e742e44ea42efa90f5e9b62f20365b5ffe0b`。
- 对应上游 tag `v0.1.3732` 指向 `aebcfb93f7b324f2e9c9ddf1c913c27130ab08e1`；这是版本映射，不是对本机二进制可复现构建的证明。
- 已安装插件 `@magpie-community/opencode-zcode-auth@0.1.59`；本机已有登录，未复制/显示上游凭据、未重新登录。
- OpenCode CLI `2.2.7`；上游 tag commit `fedc6f208aa2bd54c1019227214568083f6380ad`。
- 现役 Magpie `role=app`、PID `57060`，自 2026-11-11T09:04:54Z 运行，监听 `127.0.0.1:3425`。本轮未启动第二实例、未修改用户全局模型配置、未开放 LAN/Tailscale 监听。
- 初次在受限执行环境中得到 `running=false` 及插件缓存 `EPERM`；经正常本机用户执行通道读回确认是访问环境差异，不能据此重装或认定服务停止。
- HT 主工作树位于 JG，核对 HEAD `72b7f245fb1640b0e78bfdccd1ff5fbc5cc3012f`，保持干净。本机仅短暂保留几 KB 合成客户端配置和结果，正式工件在 JG jobs 目录。

## 已执行的验证

| 检查 | 结果与边界 |
| --- | --- |
| `/v1/models` | 显示 `zcode/GLM-5.3-Flash` 与 `zcode/GLM-5.3-Flash-Trial`；目录存在本身不是推理成功 |
| 智谱初次合成请求 | HTTP 429；插件说明 Start Plan 并发保护，要求冷却 180 秒。没有通过换账号、端点或重启来绕过 |
| 等满冷却后单次请求 | HTTP 200，返回 `MAGPIE_ZCODE_READY`，requested/served 均为智谱 Trial；约 13.2 秒 |
| 免费后备文本调用 | `opencode-go/beam-free` 返回 `MAGPIE_FREE_READY`，HTTP 200 |
| 免费后备工具结构 | 合成 `echo_receipt` 返回 `tool_calls` 和正确参数；没有执行外部动作；不等于智谱工具执行验收 |
| OpenCode→Beam | CLI exit 0，返回 `OPENCODE_MAGPIE_READY` |
| OpenCode→智谱 | CLI exit 0，纯合成接收流程审查返回 `ZCODE_MAGPIE_REVIEW_READY`；网关记录 provider=zcode、served=GLM-5.3-Flash-Trial、effort=high、HTTP 200，约 29.5 秒 |

客户端记录另伴随一条零 token 的 499，成功 200 行和 CLI 终态均保留；499 的确切内部来源未追查，不能将其算作另一次成功推理，也不据此宣称所有网络请求无异常。并发压测、真实代码执行、长期无人值守、跨主机密钥隔离均未验收。

工头首稿正确指出提交前写 seen 会造成重试丢失，但还把未展示的哈希错误处理当成缺陷，并低估了提交后写 JSON 的并发问题。Primary 拒绝这些推断并在同一会话要求纠正；第二轮再次收到 429，客户端记录 Retry-After 等待。一次冷却后仍被限流，Primary 核对会话和 PID 后终止该次独立客户端及其两个私有子进程（exit 1），没有重启网关或改账号。根据 Human 最新效率优先指示，将纯合成修正材料交给 Beam Free；其 CLI exit 0，返回 `MAGPIE_REVIEW_VERIFIED`，明确了数据库唯一约束、作用域幂等键、同键不同哈希拒绝、提交回执以及四类失败恢复预期。Primary 接受其为合成静态建议，不算实现或运行测试。模型接通不等于技术意见已验收；合成讨论也不等于实际测试已运行。

## 可复用的 OpenCode 2 项目级接线

以下为本机 loopback 合成试验配置；不是全局接管命令。`magpie-opencode` 是本机客户端标识，不是可供远程调用的 Gateway Secret。

```json
{
  "$schema": "https://opencode.ai/config.json",
  "providers": {
    "ht-magpie": {
      "name": "HT Magpie canary",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "http://127.0.0.1:3425/v1",
        "apiKey": "magpie-opencode"
      },
      "models": {
        "zcode/GLM-5.3-Flash-Trial": {
          "name": "ZCode gift Flash",
          "settings": { "reasoningEffort": "high" }
        }
      }
    }
  },
  "agents": {
    "ht-canary": {
      "description": "Inert connectivity canary",
      "mode": "primary",
      "system": "Use no tools or subagents. Answer only the supplied synthetic task.",
      "permissions": [{ "action": "*", "resource": "*", "effect": "deny" }]
    }
  },
  "permissions": [{ "action": "*", "resource": "*", "effect": "deny" }]
}
```

```text
opencode --standalone run --model ht-magpie/zcode/GLM-5.3-Flash-Trial --agent ht-canary --format json --archived <synthetic-prompt>
```

OpenCode 2 使用 `providers/package/settings/permissions`；不要直接套用 OpenCode 1 的 `provider/npm/options/permission` 示例。正式代码工头应由原 owner 按具体写域授予工具权限，本页 deny-all 配置仅用于接线验证。

Windows GUI 子系统的 Magpie exe 在 PowerShell 中直接调用时可能看不到输出；本轮通过 `& <exe> status --json | Out-String` 等管道实际取得 CLI 输出。使用当前已安装 `--help`，不猜测参数。

## 调度与 JG 边界

1. 当前显式选 `zcode/GLM-5.3-Flash-Trial`，避免用自动路由或普通模型名掩盖不同计费路径。即使界面显示额度充足，429 仍可能代表并发限制。
2. 收到等待提示就停止追加请求，按提示冷却，再有界串行复核；本轮只验证串行，不预设 16 路可用。插件内部重试与工头并发不可混计。
3. 免费模型按实际任务能力和可用性调度，智谱暂时限流不能阻塞独立 READY 工作。OpenRouter 用于单任务是当前调度策略，不是已证实其永远无法承担工头。网关不自动成为任务执行器；文件、Shell、测试仍由受限工头及宿主执行。
4. 施工目录、私有原件与正式产物留 JG。本机已验证的是模型入口。JG→本机网关的鉴权、允许模型、网络路径、断线处理需沿既有 ai-hub #301/#274 接缝验收；不能直接开放 3425 或把上游登录复制到 JG。
5. 不重新建设另一套网关，不修改现有账户、插件或 Fleet registry；无生产数据、数据库、业务 canonical 写入。

## 可恢复证据

- JG：`/workspace/jobs/ht/ht-10-resume/magpie-cli-bridge-20261112/`，包含配置、合成 CLI 结果、安全使用记录、manifest 及本说明。
- [既有 Portable AI Gateway 工作单 ai-hub #301](https://github.com/youling/ai-hub/issues/301)。其已合并源码与旧真实调用失败结论保持原范围；本次本机成功不是全舰队部署验收。
- [固定版本 Magpie Reference](https://github.com/yetone/magpie/blob/aebcfb93f7b324f2e9c9ddf1c913c27130ab08e1/docs/reference.md)
- [ZCode 插件项目说明（滚动文档，以本机 0.1.59 实测为准）](https://github.com/magpie-community/plugins/tree/main/packages/zcode)
- [OpenCode 2 配置](https://opencode.ai/docs/config/)、[权限](https://opencode.ai/docs/permissions/)
