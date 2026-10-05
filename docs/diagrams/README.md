# ai-use Diagrams

本目录保存 ai-use 自己拥有语义的 **DERIVED Diagram-as-Code source**。图用于 Human / Fresh Architect / Fresh Agent 导航，不产生治理 authority。

## Project L1

- `project.architecture.json` — ai-use Project Detail Map。
- diagram type: `architecture`
- renderer target: Archify v3.0.1-compatible typed source
- semantic source baseline: `ai-use@399650f05d1a51c642dda55bbbf2920e53c50fb4`
- presentation consumer: deployment-local Architecture Navigator or any compatible renderer

它回答：authority、L0、routing、roles、execution/recovery、durable truth、Human Host、Diagram-as-Code、owner boundary、guides/templates/history 在 ai-use 中如何分工。

## Authority

```text
AGENTS / CONSTITUTION / protocol canonical docs
        = CANONICAL

docs/diagrams/project.architecture.json
        = DERIVED NAVIGATION

rendered HTML / SVG / screenshot
        = DERIVED PRESENTATION
```

图与 canonical source 冲突时，以 canonical source 为准并修图。

## Currentness

`meta.repository.revision` 表示本图本次语义编译所依据的 exact canonical source snapshot，而不是“文件自身永远 current”的声明。

Owner repo main 发生 material semantic drift 后，Project Architect 应重新 live-read、更新 source revision/节点/边并重新验证。Navigator 可以另外显示它消费时的 exact diagram-source revision 与 freshness。

## Cross-repo consumption

ai-hub / Architecture Navigator 只允许：

- read exact accepted owner source；
- validate/render；
- stamp source repository/revision/verified_at/freshness；
- 提供 Portfolio -> Project drill-down route。

不得在 ai-hub 复制一份可独立演化的 ai-use 项目架构语义。

## Source pointers

节点的 `sources[]` 指向 ai-use 内 canonical homes。验证时应对 semantic source baseline 使用 repository-backed validation；source path 不存在、revision 不匹配或行/路径越界都应 fail closed。

参见：[`../30_PROTOCOLS/DIAGRAM_AS_CODE.md`](../30_PROTOCOLS/DIAGRAM_AS_CODE.md)。
