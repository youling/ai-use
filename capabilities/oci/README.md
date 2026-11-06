# OCI Artifact Supply — 公共容器制品制作与交付能力

**Capability v0.1 · Public / portable · Consumer-neutral**

任何 AI Agent、普通应用或业务模块，都可以在**自己的仓库**保存 Dockerfile/Containerfile、版本锁定、构建脚本和验收用例，复用本能力来制作和传递 OCI 镜像。**不要求加入 Fleet、安装 ai-hub、使用 GHCR、Tailscale 或任何指定 Agent 模型。**

这是 [OCI 制品合同](CONTRACT.md) 的第一份可运行公共实现，不是自动的生产部署服务。现阶段直接可用的工具是离线档案验证器 [verify_oci.py](verify_oci.py)：独立于具体容器运行时，能在 Windows Python、Linux 和 WSL 内验证 OCI tar/tar.gz 的哈希、索引、manifest、config 与 layer 描述符。构建、实际容器 smoke、跨机拷贝和接收端运行仍使用用户现有授权的 OCI 兼容工具执行；尚未由本公共仓库证明任意宿主都可实机工作。

## 最短使用方法：先做一份真正可验证的 OCI 制品

在你的项目根目录维护源文件和锁定版本：

```text
<project>/
  Dockerfile
  src/
  tests/
  docs/  # 可选
```

**Windows：** 先用 `wsl.exe --list --verbose` 核实所选 Linux 发行版运行于 WSL 2，进入所选 Linux 环境。若用 Linux 容器工具链，构建上下文和 containerd/BuildKit 活动数据优先放 Linux 文件系统；Windows NTFS 目录可以作为归档位置。**Linux：** 直接用已授权的本机 OCI 兼容构建/运行环境。两种情况下都应记录引擎版本、连接地址、namespace、目标平台、UID、可用磁盘；这些参数由部署方提供，不能从本文猜默认 socket 或账号。

以下示例假定你已安装、验证并获授权使用 `nerdctl` / containerd / BuildKit，且当前有独立的构建工作区和一个 `Dockerfile`。示例只演示**单平台 linux/amd64**，不代表其它平台已经验收：

```bash
set -euo pipefail
: "${OCI_CONTAINERD_SOCKET:?}" "${OCI_NAMESPACE:?}" "${OCI_SOURCE_COMMIT:?}"
test "$(git rev-parse HEAD)" = "$OCI_SOURCE_COMMIT"
test -z "$(git status --porcelain)"

nerdctl --address "$OCI_CONTAINERD_SOCKET" --namespace "$OCI_NAMESPACE" version
nerdctl --address "$OCI_CONTAINERD_SOCKET" --namespace "$OCI_NAMESPACE" build \
  --platform linux/amd64 -f Dockerfile -t example:reviewed .
# 在项目自己的测试脚本中进行真实容器运行/工具及安全验收；不要仅凭 build SUCCESS 宣称可部署。
nerdctl --address "$OCI_CONTAINERD_SOCKET" --namespace "$OCI_NAMESPACE" save \
  -o example.oci.tar example:reviewed
```

**制作端**先运行只读检查，记录生成的归档和镜像 identity：

```bash
python capabilities/oci/verify_oci.py inspect example.oci.tar --report example.inspect.json
```

`inspect` 只验证**拿到的这份数据内部自洽**，并给出归档摘要与 manifest digest；它不验证制品来自可信发布者，也不证明容器已经运行。用 owner 控制的仓库/签名清单持久登记确认过的归档 SHA-256、OCI manifest digest、源提交、平台与对应测试证据。

将归档通过**当前授权的传输方式**交到另一个主机（SSH/rsync、可移动存储、受限对象存储或其他符合权限要求的机制均可）。接收端使用**制作端已经核准的两个期望值**校验：

```bash
python capabilities/oci/verify_oci.py verify received.oci.tar \
  --expected-archive-sha256 <制作端确认的64位十六进制SHA256> \
  --expected-manifest-digest sha256:<制作端确认的64位十六进制digest> \
  --expected-platform linux/amd64 \
  --report receive.verified.json
```

验证通过后，再用目标机现有**被授权**的 `nerdctl --address ... --namespace ... load -i received.oci.tar` 或兼容 OCI importer 导入。之后按项目的独立运行验收逐项确认：镜像是否存在、是否解包、是否以预期 UID/namespace 运行、实际挂载父目录权限、工作目录、网络/资源限额、重启恢复（需要时）。**导入超时**应先只读核对 digest/content/snapshot/lease，避免盲目清理或重复执行未知副作用。

如果导出的 tar **只有 Docker save 的旧式 manifest 而无 OCI `oci-layout`/`index.json`**，当前验证器会明确拒绝，不能把 Docker tar 误称为通过 OCI layout 验证。换用已验证可输出 OCI layout 的工具，或经单独受信工具转换并重新核准摘要。

## 制品验收不是一张“成功”标签

| 证据 | 真正证明了什么 | 不证明什么 |
| --- | --- | --- |
| Source pin + clean checkout | 当前源码与所声明提交一致 | 基础镜像/依赖可用或产物内容可复现 |
| Build return code | 引擎执行了构建 | 容器实际可启动 |
| `verify_oci.py inspect` | 这份 OCI archive 内部描述符/字节一致、得到实际摘要 | 内容来自可信源、diffID 或运行通过 |
| `verify_oci.py verify` | 与**事先获信任**的归档 SHA-256 和 image manifest digest 一致 | 目标主机已经导入/运行 |
| Real container smoke | 在被记录的平台/用户/环境内按实际命令运行 | 另一个宿主或生产凭据/重启已验证 |
| Receiver import + smoke | 指定接收端达到实际验收范围 | 任意宿主可以部署、业务数据卷能热拷贝 |

特别区分：**OCI manifest digest**、**config digest/image ID**、**压缩 layer digest**、**解压 diffID** 与 **外部 tar/tar.gz 文件 SHA-256** 是不同对象。相同镜像在不同归档打包方式下，外层 tar 哈希可不同。<Link title="OCI Image Spec" url="https://github.com/opencontainers/image-spec/blob/main/spec.md" />

## 支持范围与下一阶段

- **v0.1 已有公共实现**：单 manifest 的 OCI image-layout tar/tar.gz，SHA-256 descriptor、index、config 和 layer byte verification、期望摘要比较、只读 JSON 回执；纯 Python 标准库，无 Fleet/网络依赖。
- **未声明支持**：多平台 index/任意 artifact type、OCI referrer、多层外置对象、任意压缩算法的 diffID 完整验证、Docker-only archive、签名/发布者身份认证、自动 BuildKit/nerdctl 安装、rsync/SSH 会话启动、生产凭据交付或真实部署。
- **后续在同一能力中扩展**：可替换的 builder/export/transport/receiver adapters、恢复/增量传输及回滚，前提是独立测试并交付非 Fleet 消费者可运行的 canary；不得仅从既有 Fleet 私有实测自动提升为公共运行时 PASS。

本仓已有 [Agent Runtime](../../agent-runtime/README.md) 是一个可选消费者，其发布/更新/回退继续遵循 [agent-runtime 的现行 release gate](../../agent-runtime/release/README.md)。普通业务容器不因此接受 Agent Runtime 特有的角色、GHCR 或模型约束。

架构选择与权限/数据边界见 [CONTRACT.md](CONTRACT.md) / [ADR-0022](../../90_HISTORY/ADR-0022_PUBLIC_OCI_SUPPLY.md)。公共验证测试：`python -m unittest discover -s capabilities/oci/tests -v`。所有真实节点、账户、路径、原件和授权留在使用方。
