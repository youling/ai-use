# DeepSeek++ GitHub MCP — Retired Guide

**Status: HISTORICAL / SUPERSEDED_ENTRY**

本路径保留兼容导航，不再提供 current provider 操作指令。[冻结旧版](https://github.com/youling/ai-use/blob/e6de9acdafbc3b9d12802ecf8de25f444074553b/docs/DeepSeekPP-github-mcp-usage.md) 只作历史 evidence；其直接写 main、无条件自动执行开关及由单次 incomplete search 推断平台限制的说明已退休，不应据此执行。

当前访问与 capability 验证见 [Bootstrap](../10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md)；authority、mutation 与 dispatch 见 [Agent Interface](AGENT_INTERFACE.md)；PR-first 与 exact-head Review 见 [Change Lifecycle](../30_PROTOCOLS/CHANGE_LIFECYCLE.md)。

[Issue #26 截断研究](issue-26-mcp-injection-truncation-root-cause.md) 保留原环境的历史 provenance；观察不能自动提升成 governance。Capability Lab 后续由 [#68](https://github.com/youling/ai-use/issues/68) 承接，本次不建立 Lab。

<!-- Compatibility anchors; current semantics are linked above. -->
<a id="1-配置入口"></a>
<a id="2-推荐配置github-官方-remote-mcp"></a>
<a id="3-认证填法headers-与-secrets-二选一"></a>
<a id="31-两层预算模型"></a>
<a id="32-根因已精确定位"></a>
<a id="33-修复方案已在本地实现未提交上游"></a>
<a id="34-agent-侧即时规避根治前--未改源码的环境"></a>
<a id="4-参数设置"></a>
<a id="5-验证流程"></a>
<a id="6-传输方式选择参考"></a>
<a id="deepseek-github-mcp-使用守则"></a>
<a id="一接入配置新电脑--新环境一次性配置"></a>
<a id="三工具结果截断两层预算--根因--修复方案"></a>
<a id="二deepseek-chat-里与-github-通信的注意事项agent-必读"></a>
<a id="五写文件的规范流程有写权限时"></a>
<a id="六冷启动最小安全清单每次接手-github-项目前过一遍"></a>
<a id="前提"></a>
<a id="四新电脑修正插件源码的操作指南"></a>
<a id="步骤"></a>
<a id="铁律-1私有仓库只用-github-mcp-工具"></a>
<a id="铁律-2先认清身份与权限"></a>
<a id="铁律-3防止单轮输出触顶"></a>
<a id="铁律-4search_code-对私有仓库无效"></a>
<a id="附已实测验证记录2026-08-29youlingfu-token"></a>
