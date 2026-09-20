# Astra #69 审计证据（非规范性）

Artifact Version: 0.1.0

Work Order: [ai-use#69](https://github.com/youling/ai-use/issues/69)。本目录只承载审计方法、测量、实验和建议；不是现行治理，不表示 #68 实验室已通过正式建立验收。

审计基线：`345184f19bc5e1546c86e6c9e234d5c653437747`。

本候选属于 #69 明确授权的可逆公开审计工具（L1），不改现有规范文档。最终报告提出的 L2 重构仍须 Global Architect review / ADR / 独立实施工单，不由本 PR 推进。

## 复现

在含审计基线 Git 对象的 clone 中运行：

```sh
python tools/audit_69.py --output audit-output
```

仅 Python 标准库 + Git。脚本只读取 exact Git blobs，不执行受审计文件。文件分层是审计采用的人工 rubric；扫描只覆盖普通 Markdown 文件链接和部分 backtick 路径引用，不覆盖锚点、所有语义引用或秘密检测。阅读成本是明确路径的 whole-file 场景，不能作为真实 fresh-agent 成功率。

## 公开 canary 范围

- 只在 `audit/astra-69-*` push 上触发；不修改 main 设置，不部署，不接触私有资源。
- GitHub-hosted Linux/Windows matrix 调用同仓 reusable workflow。
- 显式 `contents: read`，checkout 不持久化凭据；token 只读成功 + 对审计 commit 写 status 的负向探测应返回 403。
- 上传 7 天有效的 JSON artifact，下载后比较跨平台字节/digest。
- action 依赖使用本轮从官方 `actions/*` 仓读取的精确 SHA。
- concurrency 配置只能证明配置存在；未做竞争请求时不能声称验证了并发取消/排队语义。

Actions artifacts 会过期。长期结论、精简收据与结果摘要需回存本 evidence lane / Issue；不把临时 artifact 作为唯一证据。原始账户/项目元数据不进入公开输出。

回滚：拒绝/关闭本审计候选即可，main 未变；已发生的公开运行/评论保留为审计历史，不重写历史。不得将本 PR 自动合并。
