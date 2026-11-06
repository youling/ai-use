# Public OCI Artifact Supply — 可复用制品合同

**Artifact Version: 0.1.0 (candidate)** · **Classification: L2 generic capability contract**

本合同只定义 **OCI 制品从版本化输入到可核验交付的跨业务公共能力**；适用于 Agent Runtime、普通服务容器及独立 Linux/WSL 工作区。当前通用实现及支持范围见 [README](README.md)。它不是新的 OCI Image Spec、容器引擎、Fleet 管理器、调度器、任务状态数据库或统一凭据系统。

## 1. Semantic owner 与消费者

| 内容 | 语义 owner |
| --- | --- |
| OCI image manifest/index/config/layer/descriptor | OCI 官方规范；本仓仅按其格式实现受限验证 |
| 通用 input pin、产物身份、验收阶段、离线归档核验与可插拔分发接口 | `ai-use/capabilities/oci` |
| Agent 专用镜像 Dockerfile、上下文/凭据、conformance 与发布/回退治理 | 现有 `ai-use/agent-runtime`，本能力是其可选工具 |
| 业务镜像配方、业务测试、业务状态卷、版本与上线接受标准 | 业务项目 owner |
| Fleet node_uid/transport capability、真实节点配置、私有路径/账户、UID 映射、SSH pin | 对应部署实例或 Fleet owner；**普通使用者不依赖 Fleet** |
| 特定企业/模型账号认证、secret value/custody | 真实授权与保管方；镜像中不得携带生产 secret |

Public contract 可以支持 registry 发布、授权 SSH/rsync、离线 tar、本地文件或其它传输工具，但**不强制任何一种**。任务使用者负责自己的目标机器、传输身份与数据保留；通用代码不得把某个组织的节点名、盘符、namespace、HTTP endpoint、Agent 模型写成默认值。

## 2. 对象身份不能混淆

1. **Source revision**：构建配方/依赖与项目代码的 Git commit 或 owner 等价不可变来源，外部基础镜像应以不可变 digest pin；构建前核对当前检出及版本。
2. **Image manifest digest**：由 OCI manifest 的原始字节计算，形如 `sha256:<64hex>`，描述 config/layers；多平台情况下 index digest 与每个平台的 manifest digest 不同。
3. **Image config digest**：OCI config blob 的 digest，常对应本地镜像 ID，但不得未经核验与 registry manifest identity 互换。
4. **Layer descriptor digest / diffID**：descriptor digest 对该层的**存储字节**（压缩或非压缩）计算；diffID 对**未压缩** layer tar 字节计算，两者不等价。
5. **Archive SHA-256 / size**：对交付 tar/tar.gz 整个文件的实际字节计算；外部包装/压缩不同，即使 inner OCI manifest 相同，archive hash 也可能不同。
6. **Receipt**：有 source、actual artifact digests、actual checks、time/host scope 和可信引用的证据；本地计算出的 hash 本身不是发布者真实性证明，也不是部署或权限授权。

接收端必须从 owner 当前可信来源取得 **期望 archive SHA + image manifest digest + 平台**，然后验证接收字节和 OCI descriptor 关系。任何未验证、缺失或冲突的期望值不得被当作成功；完整性检验不替代签名/身份、许可合规、供应链或实际 runtime smoke。

## 3. 分层交付与异常恢复

```text
SOURCE_PIN
  -> BUILD_IN_AUTHORIZED_ENGINE
  -> REAL_IMAGE_SMOKE + SOURCE/CONFIG CHECK
  -> SAVE_OCI_ARCHIVE
  -> ARCHIVE_SHA + OCI_DESCRIPTOR_VALIDATION
  -> OWNER_APPROVES_DELIVERY_MANIFEST
  -> AUTHORIZED_TRANSPORT
  -> RECEIVER_SHA + OCI_DESCRIPTOR_VALIDATION
  -> IMPORT / UNPACK (receiver-owned)
  -> REAL_RECEIVER_SMOKE / VOLUME / RESOURCE CHECK
  -> ACCEPT / ACTIVATE / ROLLBACK under consumer authority
```

这些是**验收证据阶段**，不是与既有 Work/Issue/PR/Release 并行的新状态机；可以按项目风险和目标跳过与本次交付无关的 transfer/receiver。实测结果按 `NOT_RUN | PASS | FAIL | BLOCKED | UNKNOWN` 如实描述受测范围，不得从 `BUILD_PASS` 直接推断 `RUNTIME_PASS`，也不得从单一 Host 的通过推断其它 Host 可用。

### 确定性处理与 fail-closed

- **错误来源/依赖**：未锁定源码或基础镜像、expected SHA 缺失/不可信、架构不匹配 → 先固定事实；不能默认浮动升级或宣称同一制品。
- **传输失败/重复**：尽可能先比较本地与接收方内容 identity；重复事件必须能被对账，不能仅凭“再运行一次”认定幂等。
- **导入/解包超时**：区分 blob 已保存、layer 已解包、snapshot/lease 仍存在、容器实际可运行；未知副作用要读回恢复，不自动丢弃有效内容或清理未归属快照。
- **磁盘空间**：输入 archive 大小不代表 runtime unpack/snapshot/overlay 的实际占用；首次使用应对该 image/driver/platform 做空间预算及安全余量验证。
- **运行时用户与挂载**：同时检查真实宿主 userns、容器 UID/GID、所有父目录可遍历性、目标叶的读/写和网络 namespace；只检查终点目录权限不足以验收。
- **清理/回滚**：只有经过 owner 判断可删、无未保存事实、无活跃 lease 和未知状态时才清理暂存；旧已接受 digest 与数据仍可回退时才宣称可回滚。
- **业务数据卷**：OCI 镜像是通常可重建的只读软件制品；数据库/缓存/用户状态不是镜像交付的一部分，不能用 SSHFS/直接 tar 文件拷贝代替有一致性保障的数据库 backup/restore。

## 4. 接口实现与可移植性

能力以**可解释的命令行 + 标准 OCI archive/layout + 可解析 JSON 结果**交付。跨消费者使用的最低接口：

- `verify_oci.py inspect <archive>`：只读生成实际 archive/index/manifest/config/layer identity，不能宣称来源已经认证。
- `verify_oci.py verify <archive> --expected-archive-sha256 X --expected-manifest-digest Y [--expected-platform P]`：严格比对可信 owner 已声明值，未匹配必须失败。两者仍不证明目标 runtime 已执行。
- 具体 BuildKit/nerdctl/Docker/Podman 工具链、构建上下文、分发方式、归档/缓存路径由**使用者参数或插件**解析。本能力不重写容器运行时、加密或传输实现。
- 初版验证器只支持单 OCI image manifest 的 tar/tar.gz（OCI `oci-layout` + `index.json`）；多平台、签名、Docker-only tar 和任意 media types 必须明确报 Unsupported，不能静默降级成功。

本公共能力的输出不会自动推动 agent-runtime GHCR 发布、project merge、生产 deploy 或跨设备数据传输。代码库 read/write 能力不等于用户已授权操作。

## 5. 采纳与演化

1. Repo-only fixtures、Windows/Linux Python CI 与 negative tests 证明 **public verifier contract**，不自动证明 Builder/Runtime/Host 端到端。
2. 真实 Windows WSL2 构建端 + 两个 Linux 接收端的私有 donor 证据可用于形成候选，但必须区分原 Host 的实际版本、权限、路径、恢复范围；移出私仓前审查独立性、许可、可移植性和 public-safe provenance。
3. 在普通业务或非 Fleet consumer 上按真实 Dockerfile 做新 canary；检查受控构建、真实镜像、归档、传输、接收及实际 runtime，按实际场景逐段验收。
4. 若将已有私有程序中的通用 build/rsync/SSH/rollback 代码迁至公共 owner，先有清晰 adapter seam、source provenance、测试与回退，然后由原 owner 在受控审查后废弃重复实现；避免同时存在两套相互漂移的通用接口。
5. 当前 [Agent Runtime 发行合同](../../agent-runtime/release/README.md) 保持有效：特定产品的 OCI release/stable/previous/Human gate 继续由该项目 owner 决定。

**Change lifecycle**：长期 schema/ownership 改变用 ai-use 现有 L2 Issue→ADR→PR→exact-head review；普通实现更新按 scope/risk 选择 L1，不因工具新增而修改 L0。
