# Human Prompt 版本治理

## 原则

用于生成 Human SSOT 数据的 Prompt 本身就是**观测仪器的一部分**，必须进入 provenance。

一个 Deposit 不只是由“某个模型”生成，而是由以下因素共同产生：

- source conversation / source material；
- model / runtime；
- prompt version；
- transport capability；
- 必要时还包括 compression / import 规则。

因此未来评估 Deposit 时，必须能区分：

- Human 自身发生了变化；
- 模型能力发生了变化；
- Prompt 行为发生了变化；
- 压缩或导入规则发生了变化。

## 版本格式

统一使用语义版本 `X.Y.Z`：

- **MAJOR**：不兼容的输出/治理语义变化；
- **MINOR**：向后兼容的新字段、新能力或新处理分支；
- **PATCH**：不改变 schema 的修正、澄清和缺陷修复。

示例：

```text
0.1.1 -> 0.1.2
```

若只是修复“控制指令被误当素材”这类输入范围缺陷，而 Deposit schema 未改变，可升级 PATCH。

## 证据绑定

每个 Deposit 必须保留实际生成它的 Prompt 版本，例如：

```yaml
provenance:
  depositor_prompt:
    name: Human SSOT Depositor Prompt
    version: 0.1.2
```

规则：

1. 新 Prompt 只影响以后生成的 Deposit；
2. 旧 Deposit 保留原 Prompt 版本，不追溯改写；
3. 同一正式版本号不得对应多个不同 Prompt 正文；
4. Prompt 修改必须通过 Git commit 留痕；治理仓采用 PR 时，优先通过 PR 审计后进入主线；
5. 测试案例必须记录测试所用 Prompt 版本、模型/环境（已知时）、输入范围和原始输出；
6. Git 历史负责代码级审计，Deposit/Test provenance 负责语义级对应，两者不能互相替代。

## 测试与回归

Prompt 不是凭感觉优化，而应根据真实失败样本演进：

```text
模型输出
  -> 发现失败类型
  -> 保存原始证据
  -> 修正 Prompt
  -> 升级版本
  -> 用旧案例回归
```

例如某模型把 Depositor Prompt 自身总结成 `EXTERNAL_KNOWLEDGE`，应保存该原始输出并归类为 input-scope / control-data-plane failure；新版本必须能在同类输入上返回 `NO_DEPOSIT_NEEDED`，而不是再次总结协议。

## 禁止事项

- 不通过改写旧 Deposit 来伪装成新 Prompt 生成；
- 不复用同一版本号承载不同 Prompt 语义；
- 不因为模型“看起来更聪明”就省略 Prompt/version provenance；
- 不把 Git commit time 当成 Human event time。
