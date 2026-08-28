# Issue #26 根因定位结论

> work: youling/ai-use#26@mcp-injection-truncation-root-cause
> 定位日期: 2026-08-29 · 只读源码研究，未提交未授权 PR

## 一、根因（一句话）

DeepSeek++ 在「工具结果 → 模型可见上下文」的注入层，用 **写死的字符上限** 对 tool detail/output 做 `clampText` 截断，上限为 **detail 4000 字符 / output 8000 字符**，与 MCP 传输层「结果字节」配置无关，也不是可配置项。

## 二、精确定位

### 截断函数
`clampText(value, maxLength)`：超过 `maxLength` 就 `slice(0, maxLength)` 并拼 `\n...[truncated]`。

### 阈值常量（写死）
文件 `core/tool/execution-restore.ts`：

```ts
const DEFAULT_DETAIL_MAX_LENGTH = 4000;
const DEFAULT_OUTPUT_MAX_LENGTH = 8000;
const TRUNCATION_SUFFIX = '\n...[truncated]';
```

### 关键调用链
`core/tool-loop/engine.ts` 的 `createToolExecutionRecord(call, result, limits)`：

```ts
detail: clampText(result.detail, limits.detailMaxLength),
output: result.output === undefined
  ? undefined
  : clampText(JSON.stringify(result.output), limits.outputMaxLength),
```

### automation 路径硬编码
`core/automation/runner.ts` 三处直接写死：

```ts
createToolExecutionRecord(executionCall, result, {
  detailMaxLength: 4000,
  outputMaxLength: 8000,
});
// ...
detail: clampText(execution.result.detail, 4000),
output: clampText(/* ... */, 8000),
```

### clampText 副本（分散实现）
除 `engine.ts` / `execution-restore.ts` 外，还有本地实现于：
- `core/inline-agent/prompt.ts`
- `entrypoints/content.ts`
- `core/interceptor/history-cleanup.ts`

这是修复时易漏点。

## 三、关键副作用：truncated 标志不可靠

`createToolExecutionRecord` 在 clamp 后**直接继承 `result.truncated`，不因本次 clamp 置 true**：

```ts
truncated: result.truncated,
```

所以内容被注入层 clamp 截断时，`truncated:false` 是假阴性。UI 里的 truncated 字段不能作为「注入层是否裁过」的判据。

## 四、修复方案

### 治标（最小改动）
提升 `core/tool/execution-restore.ts` 两个常量 + 同步 `runner.ts` 三处硬编码。

风险：常量分散多文件，只改一处不覆盖所有 clampText 副本，易漏。

### 治本（建议，Builder 级）
1. 把 detail/output 截断上限收敛为**单一配置源**（settings 里新增「工具结果注入上限」）。
2. 注入三处消费点：tool-loop / automation / inline-agent prompt。
3. `createToolExecutionRecord` 在 clamp 时正确回写 `truncated: true`（或返回是否 clamp 的布尔，由调用方处理）。

## 五、Agent 侧即时规避（根治前）

- 单次读尽量小：精确路径、`fields` 过滤、分页。
- 超大单条无法拆分时，改本地 clone 读，绕开注入层。
- 不要把「结果字节」或「新会话」当成根治手段，二者都不影响注入层 4000/8000 上限。

## 六、证据文件清单

| 文件 | 作用 |
|---|---|
| `core/tool-loop/engine.ts` | clampText + createToolExecutionRecord |
| `core/tool/execution-restore.ts` | 默认阈值常量 4000/8000 |
| `core/automation/runner.ts` | automation 路径硬编码 4000/8000 |
| `core/inline-agent/prompt.ts` | inline-agent 本地 clampText 副本 |
| `entrypoints/content.ts` | content 脚本 clampText 副本 |
| `core/interceptor/history-cleanup.ts` | 历史清理 clampText 副本 |

## 附：回写方式说明

本研究原计划用 `add_issue_comment` 回写 issue #26，但返回 `404 Not Found`。
结合「读成功 ≠ 写成功」与 token 实测（`create_or_update_file` 成功、`add_issue_comment` 404），判定当前 PAT 具备 **Contents 写权限**，但缺少 **Issues 写权限**（fine-grained PAT 两类 scope 独立）。
故结论以本文件形式落盘于 `youling/ai-use`，由有 issue 权限者转发或由 Human 补充 PAT scope 后再回写。
