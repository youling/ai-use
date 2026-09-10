# 双词派单模板

**版本：0.1.0**

本文件本身就是模板，不再拆“字段说明 + 抽象模板 + 示例”。复制最接近当前任务的一组，替换真实值；没有节点、项目、情景或上下文参考时，直接删除对应行。

“双词”指两份东西：

- **人类派发卡**：给 Human 判断任务做什么、放哪里跑、做到哪停；
- **Agent 种子词**：给 executor 最小寻址与上下文亲和信息。任务事实仍以 durable Work Order / dispatch 为准。

运行位置按能完整完成并验证任务的**最低资源层级**选择：

`网页端 → 云端电脑 → 本地 → 本地+设备`

- **网页端**：当前 Chat/Agent 仅凭已授权 GitHub / Web / 文件等连接能力即可完成，不需要独立代码运行环境。
- **云端电脑**：需要 workspace、toolchain、进程、测试或长时间运行，但不依赖 Human 本机独有状态或真实设备；云端 Coding Agent / 云电脑可满足。
- **本地**：必须使用 Human 本机的文件、工具链、进程、私网、本地状态或其它不能可靠搬到云端的环境。
- **本地+设备**：除本地环境外，还必须访问指定节点、手机、平板或其它真实设备；必须把具体节点/设备写清楚。

能拆成独立阶段时，优先把可网页端/云端电脑完成的 tranche 单独派发，不因为最终需要设备就让整条任务占住本机。

---

## 网页端

### 人类派发卡

```text
任务：ai-use#40 Agent 规范持续执行治理预研
为什么做：已读规范的 Agent 仍可能在执行阶段回退到通用默认习惯，需要先判断治理缺口。
你要做什么：读取当前 GitHub durable state，评估 Artifact 生命周期与 Active Constraint Frame，形成架构结论；不施工。
运行位置：网页端
本轮终点：把研究结论 durable 回写 #40，停止等待 Architect Review。
```

### Agent 种子词

```text
公仓工单：youling/ai-use#40
项目：Agent 治理
情景：规范持续执行预研
上下文参考：ai-use#40
```

---

## 云端电脑

### 人类派发卡

```text
任务：fleet#43 Registry guardrails final current-main replay
为什么做：#60 的架构方向已通过，但历史 base 尚未收敛到 current main。
你要做什么：从 current main 重放 #60，保留 schema 1.2.0、management_provider_refs、managed-windows 与 Direct Intake；保持 warning-only，不做 purge。
运行位置：云端电脑
本轮终点：PR #60 新 exact head + final currentness report，停止等待 Architect Review。
```

### Agent 种子词

```text
私仓工单：youling/fleet#43/5620054398
项目：Fleet Registry
情景：Registry guardrails final current-main replay
上下文参考：PR #60；main 914497e；review 5164851976
```

---

## 本地

### 人类派发卡

```text
任务：youling-boss Windows read-only discovery
为什么做：managed-windows foundation 已进入 current main，需要开始真实机器的只读现状采集。
你要做什么：在 youling-boss 运行 canonical Windows preflight；只观察 OS、OpenSSH、Tailscale、WinRM、firewall、public fingerprint，不安装、不启用、不修改。
运行位置：本地
本轮终点：回写 YOULING_BOSS_WINDOWS_READONLY_DISCOVERY_REPORT，并给出下一轮最小 mutation plan。
```

### Agent 种子词

```text
私仓工单：youling/fleet#16/5617958691
节点：youling-boss
项目：Windows Fleet 纳管
情景：W3 Windows read-only discovery
上下文参考：#15 acceptance 5617047307
```

---

## 本地+设备

### 人类派发卡

```text
任务：Lenovo TB376FC unattended session entry / recovery canary
为什么做：真实 Android 设备需要验证无人值守唤醒、会话进入与恢复路径，不能只靠仓库推演。
你要做什么：在本地控制器连接真实 Lenovo 平板，先做只读 cold-state discovery；涉及 secure keyguard、pairing、reboot 等 Human gate 时立即停在对应 gate。
运行位置：本地+设备
本轮终点：形成 LENOVO_C4_UNATTENDED_ENTRY_RECOVERY_REPORT；未经明确授权不跨越 Human gate。
```

### Agent 种子词

```text
私仓工单：youling/fleet#17
节点：lenovo-tb376fc-assistant
项目：Android Edge
情景：无人值守 session entry / recovery
上下文参考：K20 经验；fleet#17
```

---

## 使用边界

- `私仓工单` / `公仓工单` 已表达 BOOT-1 access class；具体 authenticated route 与 fallback 仍以 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` 为准。
- Agent 种子词默认只放：工单地址，以及有价值时的节点 / 项目 / 情景 / 上下文参考；没有就省略。
- `上下文参考` 只是调度与 warm-context affinity，不是 authority，也不能覆盖 current GitHub SSOT。
- role、startup mode、scope、acceptance、requirements、reporting、stop、权限与安全 gate 留在 durable dispatch / Work Order；不要复制进种子词。
- 运行位置是 Human 调度信息，不授予 capability 或 authority；executor 启动后仍须验证实际工具与权限。
