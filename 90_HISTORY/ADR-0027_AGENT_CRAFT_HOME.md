# ADR 0027 — 人机协作工艺的 GitHub 入口

- 状态：Human 已同意建立入口，随关联 PR 审查与合并生效
- Work：[ai-use #199](https://github.com/youling/ai-use/issues/199)
- 当前内容归 [人机协作工艺](../agent-craft/README.md)

## 背景

工艺观察和改进待办先在单机积累。换会话或设备时，新接手者需要知道从哪里恢复、如何找复验条件，以及哪些事实由原项目负责。

## 裁决

在一级目录 `agent-craft/` 建立公开工艺入口。[目录首页](../agent-craft/README.md) 拥有工艺范围、研究索引和可公开的观察摘要。[工艺待办](../agent-craft/BACKLOG.md) 拥有跨案例的工艺改进待办。专题成果沿 [研究索引](../docs/research/README.md) 寻址。治理规则和项目的事实、权限、生命周期及验收各由现行 owner 管理。实例设备、运行配置和原始材料沿用 [Owner / Instance Boundary](../30_PROTOCOLS/OWNER_INSTANCE_BOUNDARY.md)。

## 其他方案

把入口放进 `docs/research/` 可以沿用专题研究导航，持续待办会与已归档研究共用入口。单设一级目录能独立恢复工艺工作，同时让研究记录继续按原路径被引用。

## 影响

现有研究和项目证据通过链接接入。旧目录、文档编号和启动阅读顺序沿用原规则。公开摘要的可复用性取决于证据范围，跨项目采用由适用 owner 决定。若撤销本入口，按关联 PR 回滚索引和入口，公开专题与源项目历史仍可从各自路径追溯。
