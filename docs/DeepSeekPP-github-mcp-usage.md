# DeepSeek++ GitHub MCP 使用守则

> 本文写给所有通过 DeepSeek++ 调用 GitHub MCP 的 Agent / DeepSeek Chat 会话。
> 覆盖三件事：①新电脑接入配置 ②在 DeepSeek Chat 里与 GitHub 通信的注意事项 ③工具结果截断的根因与修复方案。

---

## 一、接入配置（新电脑 / 新环境一次性配置）

### 1. 配置入口

1. 打开 DeepSeek 网页（https://chat.deepseek.com/），确认已安装并启用 DeepSeek++ 扩展。
2. 打开 DeepSeek++ 侧边栏 →「工具 / MCP」→「新增 MCP 服务」。

### 2. 推荐配置（GitHub 官方 Remote MCP）

| 字段 | 值 |
|---|---|
| 名称 | `GitHub MCP`（随意） |
| 传输 | `Streamable HTTP` |
| 服务 URL | `https://api.githubcopilot.com/mcp/` |
| Headers | 留空（用 Secrets 代替） |
| Secrets | 类型 `Bearer`，值 = PAT 本体 |

> 选 Streamable HTTP 的原因：GitHub 官方 remote MCP 托管在 GitHub 服务器上，无需本地 npx / shell-host / Stdio Bridge。

### 3. 认证填法（Headers 与 Secrets 二选一）

**方式 A（推荐）：用 Secrets**
- Secrets 区「类型」选 `Bearer`
- 「值」填 PAT 本体（形如 `ghp_xxxxxxxx`），**不要**加 `Bearer ` 前缀
- 扩展会自动组装 `Authorization: Bearer <token>` 请求头
- Headers 区留空

**方式 B：用 Headers**
- Headers 区新增一行：header 输入框填 `Authorization`，Value 输入框填 `Bearer ghp_xxxxxxxx`（带前缀带空格）
- Secrets 区留空

> ⚠️ 两者只填一个，同时填会重复或冲突。
> ⚠️ PAT 生成时只显示一次，建议存好；不确定完整性就重新生成。

### 4. 参数设置

| 参数 | 默认 | 推荐 | 说明 |
|---|---|---|---|
| 连接 ms | 10000 | 10000 | 建立连接超时 |
| 请求 ms | 60000 | 60000 | 单次请求超时 |
| 发现 ms | 20000 | 20000 | 拉取工具列表超时 |
| 结果字节 | 64000 | **512000** | 管 MCP 服务器→插件传输段，调大避免大 JSON 在传输层被砍 |
| 工具上限 | 128 | 128 | GitHub MCP 工具数远不到 128 |

三个开关**必须全开**：默认执行 / 允许注入 / 自动执行。否则工具要么不注入、要么每次都要手动确认。

### 5. 验证流程

1. 保存 → 点「测试」（401 = PAT 或前缀问题；连接失败 = URL 或网络问题）。
2. 点「刷新工具」。
3. **新开一个 DeepSeek 对话**（MCP 工具描述只注入新会话）。
4. 发一句「列出 youling/re 的 issue」验证工具已注入并能跑通。

### 6. 传输方式选择参考

| 传输 | 适用场景 | 备注 |
|---|---|---|
| Streamable HTTP | 远程 HTTP MCP 服务 | ✅ 首选 |
| HTTP | JSON-RPC POST 端点 | 旧式 |
| SSE | 旧式 SSE 端点 | 遗留 |
| Stdio Bridge | 本地 stdio 服务 | 需本地 bridge 进程 |
| Native | 本机 Native Messaging host | 需额外安装 host |

> 浏览器扩展沙箱无法直接启动 stdio 进程或读任意本地文件。本地 MCP 必须经 Stdio Bridge 或 Native host 中转。

---

## 二、DeepSeek Chat 里与 GitHub 通信的注意事项（Agent 必读）

### 铁律 1：私有仓库只用 GitHub MCP 工具

| 做法 | 结果 | 结论 |
|---|---|---|
| `issue_read` / `get_file_contents` | 返回正文 | ✅ 唯一正确姿势 |
| `web_fetch` 抓 github.com 页面 | 登录墙 | ❌ 匿名无认证 |
| `web_fetch` 抓 api.github.com | HTTP 404 | ❌ 私有资源未授权按 404 返回 |
| `browser_navigate` 后直接快照 | 空 RootWebArea | ❌ React SPA 需 wait_for + snapshot |

**私有仓库一律走 GitHub MCP 工具；`web_fetch` 与裸浏览器对 GitHub 私有内容不可用。**

### 铁律 2：先认清身份与权限

1. 介入任何仓库前，先调 `get_me` 确认当前 MCP 认证身份（不一定是仓库 owner）。
2. **读成功 ≠ 写成功**。
   - 读：`get_file_contents` / `issue_read` 返回正文 = 可读。
   - 写：`create_branch` / `create_or_update_file` 返回 `404 Not Found`（而非 403）= 只读授权 / 无写权限。
3. 无写权限时：不要反复重试；把内容用 Markdown 代码块交付给有权限的人，或让用户切有写权限的 token。

> 实测陷阱：fine-grained PAT 的 Contents 和 Issues 是独立 scope。能 `create_or_update_file` 不代表能 `add_issue_comment`（后者可能 404）。写之前先想清楚目标资源属于哪个 scope。

### 铁律 3：防止单轮输出触顶

1. 长报告不要刷在聊天里——直接 `add_issue_comment` 或写文件落盘，聊天只给一句话摘要。
2. 一个回复只带 1~2 个工具调用。
3. 现象区分：
   - 工具结果里出现 `[truncated]` → 读入 payload 超限（见第三节）。
   - 聊天文字在某个字符处戛然而止（可能断在反引号中间）→ 模型单轮 max output tokens 触顶。

### 铁律 4：search_code 对私有仓库无效

GitHub code search API 只索引公开仓库。`search_code` 对私有仓库返回 `total_count: 0` 且 `incomplete_results: true`。

私有仓库代码定位替代方案：
1. 已知文件路径 → `get_file_contents` 精确读文件。
2. 追溯变更历史 → `list_commits`（可按 `path` 过滤）→ `get_commit` 看 diff。
3. 粗粒度目录浏览 → `get_file_contents` 传目录 path + `fields` 减小体积。
4. 需要本地全文检索 → 本地 clone 后用 `git grep`。

---

## 三、工具结果截断：两层预算 + 根因 + 修复方案

### 3.1 两层预算模型

截断有两个**独立预算层**，根因不同，手段不同：

**层①：MCP 传输层（可配置）**
- 对应 DeepSeek++ MCP 的「结果字节」，管 **MCP 服务器 → 插件** 传输段。
- 默认 64000，调到 512000 可解决大 JSON 列表 / 大文件在传输层被砍的问题。

**层②：模型上下文注入层（此前无 UI 直接配置项）**
- 插件把工具结果注入模型可见上下文时，存在一个更小的字符预算。
- 硬实测：`结果字节=512000` 时，6425 字节的 AGENTS.md 仍 `[truncated]`，4397 字节的 README.md 完整 → 阈值约 4.4~6.4KB。
- 结论：瓶颈在层②而非层①。

### 3.2 根因（已精确定位）

注入层用**写死的字符上限**对 tool detail/output 做 `clampText` 截断：

| 项 | 值 |
|---|---|
| detail 上限 | 4000 字符 |
| output 上限 | 8000 字符 |
| 截断后缀 | `\n...[truncated]` |

关键代码位置（deepseek-pp 源码）：
- `core/tool/execution-restore.ts` — 定义常量 `DEFAULT_DETAIL_MAX_LENGTH=4000` / `DEFAULT_OUTPUT_MAX_LENGTH=8000`
- `core/tool-loop/engine.ts` — `createToolExecutionRecord()` 调用 `clampText()`
- `core/automation/runner.ts` — 三处硬编码 4000/8000
- clampText 副本曾分散于 `core/inline-agent/prompt.ts`、`entrypoints/content.ts`、`core/interceptor/history-cleanup.ts`

**关键副作用**：`createToolExecutionRecord` 在 clamp 后直接继承 `result.truncated`，不因本次注入层截断而置 true → `truncated:false` 是假阴性，UI 里 truncated 字段不可作为「注入层是否裁过」的判据。

### 3.3 修复方案（已在本地实现，未提交上游）

修复在本地 `D:\coding\deepseek-pp` 工作树完成，验证通过：

**改动内容：**
1. 新增 `core/tool/truncation.ts` — 统一 `clampText` / `clampTextWithFlag` + `TRUNCATION_SUFFIX`。
2. 新增 `core/tool/injection-limits.ts` — settings 支撑的配置（MCP-timeout 同款模式），键 `deepseek_pp_tool_result_injection_limits`，默认 4000/8000，范围 1000–500000。
3. `truncated` 改为 `result.truncated || 本次 detail/output 被 clamp`，修复假阴性。
4. 三处消费点（tool-loop / automation / inline-agent）接配置源；clampText 副本去重。

**验证结果：**
- `npm run compile` ✅
- `prompt:freeze` ✅ 无 golden drift
- 新测试 `tests/tool-result-injection-limits.test.ts`（23 用例）✅
- `npm test`：1829 通过，6 个失败均为 Windows 环境预存问题（shell-host / sidepanel 路径 / 时序），与本次改动无关

**注意：**
- 默认值仍为 4000/8000，且尚无 settings UI 绑定 → 观察行为与修复前相同。
- 若要调大上限，需手动写 storage 键 `deepseek_pp_tool_result_injection_limits`，或补 settings UI。
- 改动仅本地工作树，需 build 加载或 commit+PR 上游后才生效。

### 3.4 Agent 侧即时规避（根治前 / 未改源码的环境）

1. **单次读尽量小**：精确路径、`fields` 过滤、`page + perPage` 分页。
2. **单条超长且无法拆**（如超长 dispatch comment）：MCP 侧读不到全文，改本地 clone 后 `cat` / `git grep`。
3. 不要把「结果字节」或「新会话」当根治手段——二者都不影响注入层 4000/8000 上限。

---

## 四、新电脑修正插件源码的操作指南

> 适用场景：在新电脑装了 DeepSeek++，配置好 GitHub MCP 后，想让本机插件也获得「注入层可配置 + truncated 正确回写」的修复。

### 前提

1. 已按第一节配置好 GitHub MCP。
2. 本机有 Node.js 环境，能 clone 并构建插件。
3. 已从 GitHub 拉取 deepseek-pp 源码（上游若已合并修复则直接拉最新；若未合并，需本地应用修复补丁）。

### 步骤

1. **确认上游是否已合并修复**：
   - 打开 `zhu1090093659/deepseek-pp`，看是否存在 `core/tool/injection-limits.ts`。
   - 存在 → 直接 clone 最新 main，跳到步骤 4。
   - 不存在 → 需本地应用修复（见下）。

2. **本地应用修复（上游未合并时）**：
   - 将本机 `D:\coding\deepseek-pp` 工作树的改动做成 patch，或直接把相关文件复制到新电脑对应路径。
   - 核心新增文件：`core/tool/truncation.ts`、`core/tool/injection-limits.ts`。
   - 修改文件：`core/tool/execution-restore.ts`、`core/tool-loop/engine.ts`、`core/automation/runner.ts`、`core/inline-agent/prompt.ts`、`entrypoints/content.ts`、`core/interceptor/history-cleanup.ts`。

3. **安装依赖**：`npm install`。

4. **构建**：`npm run build:chrome`（Edge 用 `build:edge`，Firefox 用 `build:firefox`）。

5. **加载扩展**：
   - Chrome：打开 `chrome://extensions/`，开启开发者模式，加载 `dist/chrome-mv3/`。
   - Edge：`edge://extensions/` 加载 `dist/edge-mv3/`。
   - Firefox：`about:debugging#/runtime/this-firefox` 加载 `dist/firefox-mv3/manifest.json`。

6. **验证**：
   - 刷新 DeepSeek 页面，新开会话，确认 MCP 工具已注入。
   - 如需调大注入上限，手动写 storage 键 `deepseek_pp_tool_result_injection_limits`（如 `{"detailMaxLength":16000,"outputMaxLength":32000}`），或等 settings UI 补上后在界面里改。

> ⚠️ 若上游已合并，优先用上游版本，不要本地手改，避免和后续更新冲突。

---

## 五、写文件的规范流程（有写权限时）

1. `list_branches` 确认默认分支（通常 `main`）。
2. 新建文件：`create_or_update_file` 到 `main`，新文件无需 `sha`。
3. 更新已有文件：必须先 `get_file_contents` 拿到该文件的 `sha`，再带 `sha` 提交。
4. 多文件或需评审的改动：`create_branch` → `create_or_update_file` → `create_pull_request`。
5. 只提交与当前任务强相关的改动，不要夹带无关文件。

---

## 六、冷启动最小安全清单（每次接手 GitHub 项目前过一遍）

- [ ] `get_me` 确认当前身份。
- [ ] `list_branches` 确认目标仓库 + 默认分支。
- [ ] 读 `AGENTS.md`（若存在）作为项目规则入口。
- [ ] 私有仓：只用 GitHub MCP，不碰 web_fetch / browser。
- [ ] 列表类数据：分页/过滤控制单次体积；超大单条改本地 clone 读。
- [ ] 写入前先确认有写权限（读成功 ≠ 写成功；Contents 与 Issues 权限独立）。
- [ ] 长内容落盘，不在聊天里刷长报告。

---

## 附：已实测验证记录（2026-08-29，youlingfu token）

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
| `add_issue_comment` | `youling/ai-use#26` | ❌ | 404；Contents 有写权但 Issues 无写权 |
