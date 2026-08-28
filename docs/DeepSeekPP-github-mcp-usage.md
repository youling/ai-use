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

## 2. 防止工具结果被 `[truncated]` 截断 —— 两层预算，别只会分页

截断有两个**独立预算层**，根因不同，手段不同：

### 层①：MCP 传输层（可配置）

- 对应 DeepSeek++ MCP 的「结果字节」，管 **MCP 服务器 → 插件** 这段传输。
- 默认 64000，调大到 512000 可解决「大 JSON 列表 / 大文件在传输层被砍」的问题。

### 层②：模型上下文注入层（当前无 UI 直接配置项）

- 插件把工具结果注入模型可见上下文时，存在一个**更小**的预算。
- **硬实测**：`结果字节=512000` 时，6425 字节的 `AGENTS.md` 仍 `[truncated]`，而 4397 字节的 `README.md` 完整 → 预算阈值约在 **4.4KB ~ 6.4KB 之间**，远小于 512000。
- 结论：**瓶颈在层②而非层①**。「调大结果字节根治一切截断」「新会话生效」都是错误归因——对层②无效。

### 可操作对策

1. **单次读尽量小**：`get_file_contents` 精确到单文件路径；列目录用 `fields` 只取必要字段；`issue_read(get_comments)` 用 `page + perPage` 分页。
2. **单条超长且无法拆**（如超长 dispatch comment）：MCP 侧读不到全文，改走本地 clone 后 `cat`/`git grep`。
3. **根治层②需改插件注入层代码**（`core/tool/` 或 `core/mcp/transports/` 中的截断逻辑），属 Builder 工作，Agent 不自行改动。

## 3. 防自己单轮输出触顶（与 MCP 无关，但常混淆）

1. 长报告不要刷在聊天里——直接 `add_issue_comment` 或写文件落盘，聊天只给一句话摘要。
2. 一个回复只带 1~2 个工具调用，别「大段文字 + 多个工具 XML」挤爆单轮。
3. 现象区分：
   - 工具结果里出现 `[truncated]` → 读入 payload 超限（层①或层②）。
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
- [ ] 列表类数据：先分页/过滤控制单次体积；超大单条改本地 clone 读。
- [ ] 写入前先确认有写权限（读成功 ≠ 写成功）。
- [ ] 长内容落盘，不在聊天里刷长报告。

## 6. 已实测验证（2026-08-29，youlingfu token）

| 工具 | 目标 | 结果 | 备注 |
|---|---|---|---|
| `get_me` | - | ✅ | 身份 `youlingfu` |
| `list_issues` | `youling/re` | ✅ | 返回 14 个 open issues |
| `get_file_contents` | `.gitignore` (429B) | ✅ | 完整 |
| `get_file_contents` | `re/README.md` (4397B) | ✅ | 完整 |
| `get_file_contents` | `re/AGENTS.md` (6425B) | ❌ | `[truncated]`；结果字节 512000 仍截 → 瓶颈在注入层 |
| `create_or_update_file` | `youling/ai-use` | ✅ | 带 sha 更新本文件成功 |
| `search_code` | `youling/ai-use` | ❌ | 返回空，`incomplete_results: true` |
| `issue_read get_comments` | `youling/re#1` | ⚠️ | 全量 12 条截断；分页到末页后末尾超长 dispatch 仍截 |

**关键结论 1：`search_code` 对私有仓库无效。**

GitHub 的 code search API 只索引公开仓库。即使 token 具备私有仓库读权限，`search_code` 对私有仓库仍返回 `total_count: 0` 且 `incomplete_results: true`，不能作为私有仓代码检索手段。

私有仓库代码定位的替代方案：
1. 已知文件路径 → `get_file_contents` 精确读文件。
2. 追溯变更历史 → `list_commits`（可按 `path` 过滤）→ `get_commit` 看 diff。
3. 粗粒度目录浏览 → `get_file_contents` 传目录 path + `fields` 减小体积。
4. 需要本地全文检索 → 在本地 clone 后用 `git grep`，不要指望远端 code search。

**关键结论 2：截断瓶颈在注入层，不在「结果字节」。** 见 §2。

## 7. DeepSeek++ 接入 GitHub MCP 完整配置指南

### 7.1 配置入口

1. 打开 DeepSeek 网页（https://chat.deepseek.com/），确保已安装并启用 DeepSeek++ 扩展。
2. 打开 DeepSeek++ 侧边栏。
3. 进入「工具 / MCP」页面。
4. 点击「新增 MCP 服务」。

### 7.2 推荐配置（GitHub 官方 Remote MCP）

| 字段 | 值 |
|---|---|
| 名称 | `GitHub MCP`（随意） |
| 传输 | `Streamable HTTP` |
| 服务 URL | `https://api.githubcopilot.com/mcp/` |
| Headers | 留空（用 Secrets 代替） |
| Secrets | 类型 `Bearer`，值 = PAT 本体 |

> 为什么选 Streamable HTTP：GitHub 官方 remote MCP 是托管在 GitHub 服务器上的 HTTP 服务，无需本地 npx / shell-host / Stdio Bridge，是浏览器扩展环境下最顺的接入方式。

### 7.3 认证填法：Headers 与 Secrets 二选一

**方式 A（推荐）：用 Secrets**
- Secrets 区「类型」选 `Bearer`
- 「值」填 **PAT 本体**（形如 `ghp_xxxxxxxx`），**不要**加 `Bearer ` 前缀
- 扩展会自动组装成 `Authorization: Bearer <token>` 请求头
- Headers 区留空

**方式 B：用 Headers**
- Headers 区新增一行，两个输入框分别填：
  - header 输入框：`Authorization`
  - Value 输入框：`Bearer ghp_xxxxxxxx`（带前缀带空格）
- Secrets 区留空

> ⚠️ 两者只填一个，同时填会重复或冲突。
> ⚠️ PAT 生成时只显示一次，建议存好；不确定完整性就重新生成。

### 7.4 参数详解（结果字节只管传输层，注入层另有预算）

| 参数 | 默认 | 推荐 | 说明 |
|---|---|---|---|
| 连接 ms | 10000 | 10000 | 建立连接超时，远程 HTTP 够用 |
| 请求 ms | 60000 | 60000 | 单次请求超时，读大文件/长列表够用 |
| 发现 ms | 20000 | 20000 | 拉取工具列表超时，够用 |
| 结果字节 | 64000 | 512000 | 只管 MCP 服务器→插件传输段。**不是截断的唯一根治点**：注入模型上下文时的更小预算（实测约 4.4~6.4KB）不受它控制 |
| 工具上限 | 128 | 128 | GitHub MCP 工具数远不到 128，无需改 |

> ⚠️ 实测教训：`结果字节=512000` 已生效时，6425 字节的 `AGENTS.md` 仍 `[truncated]`。说明瓶颈在工具结果→模型上下文的注入层，而非传输层。注入层当前无 UI 直接配置项；Agent 侧只能用「单次读更小 + 本地 clone 兜底」绕过，根治需改插件源码（Builder 职责）。

### 7.5 三个开关

| 开关 | 状态 | 作用 |
|---|---|---|
| 默认执行 | **开** | 服务级默认策略：工具默认自动跑 |
| 允许注入 | **开** | 工具描述注入 prompt，模型才能感知工具并调用 |
| 自动执行 | **开** | 模型输出工具调用即自动执行，无需手动确认 |

> 三个开关必须全开，否则工具要么不注入、要么每次调用都要手动点确认。

### 7.6 保存后验证流程

1. 点「保存」。
2. 点「测试」验证 initialize/list 行为与延迟。
   - 通 → 继续下一步。
   - 401 → PAT 错误或前缀问题。
   - 连接失败 → URL 或网络问题。
3. 点「刷新工具」填充工具缓存。
4. 新开一个 DeepSeek 对话（MCP 工具描述注入新会话）。
5. 发一句「列出 youling/re 的 issue」验证工具已注入并能跑通。

### 7.7 传输方式选择参考

| 传输 | 适用场景 | 备注 |
|---|---|---|
| Streamable HTTP | 远程 HTTP MCP 服务（GitHub 官方推荐） | ✅ 首选 |
| HTTP | JSON-RPC POST 端点 | 旧式 |
| SSE | 旧式 SSE 端点 | 遗留 |
| Stdio Bridge | 本地 stdio 服务 | 需本地 bridge 进程，浏览器沙箱不能直接跑 stdio |
| Native | 本机 Native Messaging host | 需额外安装 host（如 shell-host） |

> 浏览器扩展沙箱无法直接启动 stdio 进程或读任意本地文件。本地 MCP 必须经 Stdio Bridge 或 Native host 中转。
