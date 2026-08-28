# DeepSeek++ GitHub MCP 使用守则

> 写给所有通过 DeepSeek++ 调用 GitHub MCP 的 Agent / DeepSeek Chat 会话。
> 目标：冷启动任何私有项目时，不重复踩「读不到 / 被截断 / 误用工具 / 无权写入」四类坑。

## 0. 先认清身份与权限（第一件事）

1. 介入任何仓库前，先调 `get_me` 确认当前 MCP 认证身份。
   - 身份不一定是仓库 owner，可能是被授权的跨账号（例如 `youlingfu` / `youling-architect`）。
2. **读成功 ≠ 写成功**。判断方法：
   - 读：`get_file_contents` / `issue_read` 返回正文 = 可读。
   - 写：`create_branch` / `create_or_update_file` 返回 `404 Not Found`（而非 403）= 只读授权 / 无写权限。
3. 无写权限时：
   - 不要反复重试写操作。
   - 把内容用 Markdown 代码块交付给有权限的人，或让用户切换到有写权限的 token 后再写。
   - 写文档前先确认目标仓库：写错仓库（跨账号只读仓）会得到同样的 404。

## 1. 读私有 GitHub 资源：只用 GitHub MCP，禁用 web_fetch / browser

| 做法 | 结果 | 结论 |
|---|---|---|
| `issue_read` / `get_file_contents` | 返回正文 | ✅ 唯一正确姿势 |
| `web_fetch` 抓 github.com 页面 | "Uh oh! error" 登录墙 | ❌ 匿名无认证 |
| `web_fetch` 抓 api.github.com | HTTP 404 | ❌ 私有资源未授权按 404 返回 |
| `browser_navigate` 后直接快照 | 空 RootWebArea | ❌ React SPA 需 wait_for + snapshot |

**铁律：私有仓库一律走 GitHub MCP 工具；`web_fetch` 与裸浏览器对 GitHub 私有内容不可用。**

## 2. 防止工具结果被 `[truncated]` 截断

1. `issue_read(get_comments)` 一次拉全量评论，payload 过大会被硬截断。
   - 目标评论若在列表末尾（最新一条），会恰好落在截断点之后，表现为「读不到」。
2. 正确做法：**分页**。
   - `issue_read` 传 `page` + `perPage`（如 `perPage: 3`，`page` 定位到尾部），只拉最后一页。
3. 大文件：`get_file_contents` 精确到单文件路径，不要整仓拉取。
4. 列目录：用 `fields` 只取需要的字段（如 `["name","type","path"]`）减小体积。

## 3. 防自己单轮输出触顶（与 MCP 无关，但常混淆）

1. 长报告不要刷在聊天里——直接 `add_issue_comment` 或写文件落盘，聊天只给一句话摘要。
2. 一个回复只带 1~2 个工具调用，别「大段文字 + 多个工具 XML」挤爆单轮。
3. 现象区分：
   - 工具结果里出现 `[truncated]` → 读入 payload 超限。
   - 聊天文字在某个字符处戛然而止（可能断在反引号中间）→ 模型单轮 max output tokens 触顶。

## 4. 写文件的规范流程（有写权限时）

1. `list_branches` 确认默认分支（通常 `main`）。
2. 新建文件：`create_or_update_file` 到 `main`，新文件无需 `sha`。
3. 更新已有文件：必须先 `get_file_contents` 拿到该文件的 `sha`，再带 `sha` 提交。
4. 多文件或需评审的改动：`create_branch` → `create_or_update_file` → `create_pull_request`。
5. 只提交与当前任务强相关的改动，不要夹带无关文件。

## 5. 冷启动最小安全清单（每次接手 GitHub 项目前过一遍）

- [ ] `get_me` 确认当前身份。
- [ ] `list_branches` 确认目标仓库 + 默认分支。
- [ ] 读 `AGENTS.md`（若存在）作为项目规则入口。
- [ ] 私有仓：只用 GitHub MCP，不碰 web_fetch / browser。
- [ ] 列表类数据：分页拉取，避免截断。
- [ ] 写入前先确认有写权限（读成功 ≠ 写成功）。
- [ ] 长内容落盘，不在聊天里刷长报告。

## 6. 已实测验证（2026-08-29，youlingfu token）

以下为本次实机验证记录，覆盖核心读写路径。

| 工具 | 目标 | 结果 | 备注 |
|---|---|---|---|
| `get_me` | - | ✅ | 身份 `youlingfu` |
| `list_issues` | `youling/re` | ✅ | 返回 14 个 open issues |
| `get_file_contents` | `youling/ai-use` | ✅ | 返回正文 + blob sha |
| `list_branches` | `youling/ai-use` | ✅ | `main` + 21 个功能分支 |
| `create_or_update_file` | `youling/ai-use` | ✅ | 带 sha 更新本文件成功 |
| `search_code` | `youling/ai-use` | ❌ | 返回空，`incomplete_results: true` |

**关键结论：`search_code` 对私有仓库无效。**

GitHub 的 code search API 只索引公开仓库。即使 token 具备私有仓库读权限，`search_code` 对私有仓库仍返回 `total_count: 0` 且 `incomplete_results: true`，不能作为私有仓代码检索手段。

私有仓库代码定位的替代方案：
1. 已知文件路径 → `get_file_contents` 精确读文件。
2. 追溯变更历史 → `list_commits`（可按 `path` 过滤）→ `get_commit` 看 diff。
3. 粗粒度目录浏览 → `get_file_contents` 传目录 path + `fields` 减小体积。
4. 需要本地全文检索 → 在本地 clone 后用 `git grep`，不要指望远端 code search。

## 7. DeepSeek++ MCP 配置回执

- 传输：`Streamable HTTP`
- 服务 URL：`https://api.githubcopilot.com/mcp/`
- 认证：Secrets 区类型选 `Bearer`，填 PAT 本体（不要加 `Bearer ` 前缀；扩展自动组装 `Authorization` 头）
- 结果字节建议调到 256000+，默认 64000 易截断大 JSON
- 三个开关（默认执行 / 允许注入 / 自动执行）全开，否则工具调用需手动确认
