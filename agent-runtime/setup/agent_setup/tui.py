"""Human-facing V2 presentation; the accepted SetupEngine owns every effect."""
from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Checkbox, Collapsible, Footer, Input, Label, Static


TEXT = {
    "zh": {
        "title": "Agent Runtime 安装向导", "steps": ["电脑检查", "安装位置", "账户连接", "预览与安装", "安装结果"],
        "back": "上一步", "next": "下一步", "apply": "安装", "verify": "重新验收", "repair": "恢复建议",
        "approve": "我已审查并批准这次安装", "blocked": "当前为安全预览。实际安装需要另行取得电脑所有者授权。",
        "intro": "检查电脑，然后推荐安装位置。已有程序和数据保留原位。",
        "busy": "正在处理，请稍候…", "error": "操作未完成。请返回检查方案，或交由电脑所有者处理。",
        "details": "技术详情", "advanced": "高级：自定义安装目录", "recompute": "重新规划",
        "placement": "推荐位置 · 保留已有目录，不搬迁数据", "accounts": "账户可分别连接，也可稍后再配置。只显示非敏感身份/软件线索，不读取密钥。",
        "auto": "自动检测并复用（推荐）", "manual": "手动配置凭据", "connect": "连接", "skip": "暂时跳过",
        "credential_approve": "批准下方账户及权限对应的连接操作", "local": "安装本地容器", "review": "请审查以下实际变更，再批准安装。账户连接与本地安装独立验收。",
        "pending": "尚未验证", "needs": "需连接", "passed": "已验证", "skipped": "已跳过", "failed": "需要处理",
        "missing": "没有可安全复用的身份。使用受信任的登录入口，或暂时跳过。",
        "preview": "仅预览：未执行安装", "scope": "连接权限与操作", "github": "GitHub", "model": "AI 模型",
        "checks": ["系统", "Python", "WSL / 容器", "存储"], "result_labels": ["本地容器已安装", "GitHub 已连接", "模型已就绪", "GitHub 恢复已验证"],
        "paths": ["工作区", "配置", "缓存", "临时文件", "Exchange", "HOST_AGENT.md"],
    },
    "en": {
        "title": "Agent Runtime setup", "steps": ["Computer check", "Install location", "Connect accounts", "Review and install", "Results"],
        "back": "Back", "next": "Next", "apply": "Install", "verify": "Verify again", "repair": "Recovery advice",
        "approve": "I reviewed and approve this installation", "blocked": "Safe preview. Installation needs separate computer-owner authority.",
        "intro": "Check this computer and recommend locations. Preserve existing programs and data.",
        "busy": "Working…", "error": "Operation incomplete. Review the plan or ask the computer owner to resolve it.",
        "details": "Technical details", "advanced": "Advanced: customize directories", "recompute": "Recalculate",
        "placement": "Recommended locations · preserve existing data", "accounts": "Connect independently or later. Only non-sensitive identity/software hints are shown; no keys are read.",
        "auto": "Detect and reuse (recommended)", "manual": "Configure manually", "connect": "Connect", "skip": "Skip for now",
        "credential_approve": "Approve the displayed account, permissions and connection", "local": "Install local container", "review": "Review the actual changes before approving. Local installation and account access are verified independently.",
        "pending": "Not yet verified", "needs": "Connection needed", "passed": "Verified", "skipped": "Skipped", "failed": "Needs attention",
        "missing": "No safely reusable identity. Use the trusted login entry point, or skip for now.",
        "preview": "Preview only: installation has not run", "scope": "Connection scope and action", "github": "GitHub", "model": "AI model",
        "checks": ["System", "Python", "WSL / containers", "Storage"], "result_labels": ["Local container installed", "GitHub connected", "Model ready", "GitHub recovery verified"],
        "paths": ["Workspace", "Configuration", "Cache", "Temporary files", "Exchange", "HOST_AGENT.md"],
    },
}

_SECRET = re.compile(r"(?:gh[pousr]_|github_pat_|sk-|-----BEGIN .*PRIVATE KEY|password\s*=|token\s*=)", re.I)


def display(value: Any, limit: int = 240) -> str:
    """Only scalar metadata, never provider dictionaries, traces or terminal controls."""
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return "—"
    text = str(value)
    if _SECRET.search(text):
        return "[REDACTED]"
    text = "".join(c for c in text if c >= " " and c != "\x7f")
    return text[:limit] + ("…" if len(text) > limit else "")


class SetupApp(App):
    CSS = """
    Screen { background: $surface; }
    #heading { height: 2; content-align: center middle; text-style: bold; background: $primary; }
    #body { height: 1fr; padding: 0 1; }
    #status { height: auto; max-height: 3; padding: 0 1; color: $warning; }
    #controls { height: 3; padding: 0 1; }
    Button { min-width: 10; margin-right: 1; }
    Input { margin-bottom: 1; }
    Static { height: auto; }
    .section { text-style: bold; margin-top: 1; color: $accent; }
    .summary { margin-bottom: 1; }
    .account-actions { height: 3; }
    .account-actions Input { width: 1fr; margin-bottom: 0; }
    Collapsible { padding: 0; }
    Checkbox { height: auto; }
    """
    BINDINGS = [("escape", "back", "Back"), ("ctrl+q", "quit", "Quit"), ("up", "focus_previous", "Previous"), ("down", "focus_next", "Next")]

    def __init__(self, engine: Any, *, locale: str = "zh", host_authorized: bool = False, folder_picker=None):
        super().__init__()
        self.engine, self.host_authorized = engine, host_authorized
        self.words = TEXT.get(locale, TEXT["zh"])
        self.step = 0
        self.probe_data, self.plan_data, self.result = {}, {}, {}
        self.github, self.model, self.durable = {}, {}, {}
        self.overrides = {"host_authorized": True} if host_authorized else {}
        self.overrides["runtime"] = True
        self.credentials: dict = {}
        self.mode = "auto"
        self.busy = False
        self.approved_fingerprint: str | None = None
        self.root_overlap=False
        self.status_text=''
        self.folder_picker = folder_picker
        self.placement_mode = "auto"
        self.advanced_open = False
        self.placement_dirty = False
        self.placement_parent_draft: str | None = None

    def root_field_value(self, role: str) -> str:
        value = self.overrides.get(role, '')
        if self.overrides.get('isolated_scope'):
            return Path(value).name if value else ''
        return value

    def compose(self) -> ComposeResult:
        yield Static(self.words["title"], id="heading", markup=False)
        yield VerticalScroll(id="body")
        yield Static("", id="status", markup=False)
        with Horizontal(id="controls"):
            yield Button(self.words["back"], id="back")
            yield Button(self.words["next"], id="next", variant="primary")
        yield Footer()

    async def on_mount(self) -> None:
        await self.render_step()
        result = await self.invoke("probe")
        if result is not None:
            self.probe_data = result
            self.set_status("")
            await self.render_step()

    def state_label(self, state: Any) -> str:
        return self.words["passed"] if state == "PASS" else self.words["skipped"] if state == "SKIPPED" else self.words["failed"] if state in {"FAIL", "BLOCKED", "REVOKED", "EXPIRED"} else self.words["needs"] if state in {"REUSE_NOT_SUPPORTED", "NEEDS_CONNECTION", "MISSING", "NOT_AUTHORIZED"} else self.words["pending"]

    def checks_summary(self) -> str:
        p = self.probe_data
        states = [p.get("platform") == "windows", p.get("python_verified") is True and str(p.get("python_version", "")).startswith("3.14."), p.get("wslc_capability", {}).get("state") == "PASS" and str(p.get("wsl_app_version", "")).split(".")[0].isdigit() and int(str(p.get("wsl_app_version", "0")).split(".")[0]) >= 3, any(v.get("free_bytes", 0) >= 8 * 2**30 and v.get("fs") in {"NTFS", "ReFS"} for v in p.get("volumes", []))]
        remedies = ["需要 Windows；当前环境不能执行安装", "需要官方签名的 Python 3.14", "需要 WSL 应用 3.0+ 与可用容器能力", "需要本地 NTFS/ReFS 磁盘与至少 8 GiB 余量"] if self.words is TEXT["zh"] else ["Windows required for installation", "Verified official Python 3.14 required", "WSL application 3.0+ and container capability required", "Local NTFS/ReFS with at least 8 GiB free required"]
        return "\n".join(f"{'✔' if state else '○'} {label} · {self.words['passed'] if state else remedies[i] if p else self.words['pending']}" for i, (label, state) in enumerate(zip(self.words["checks"], states)))

    def placement_summary(self) -> str:
        rows = self.plan_data.get("placement_rows", [])
        if rows:
            labels = dict(zip(("workspace", "config", "cache", "temp", "exchange", "host_agent"), self.words["paths"]))
            formatted = []
            for row in rows:
                label = labels.get(row.get("name"), row.get("label") or row.get("name"))
                media = row.get("media") or " / ".join(display(row.get(key)) for key in ("bus_type", "media_type"))
                free = row.get("free") or (f"{row['free_bytes'] / 2**30:.1f} GiB" if isinstance(row.get("free_bytes"), int) else "—")
                reason = self.placement_reason(row.get("name"), row.get("reason"))
                formatted.append(f"{display(label)}  {display(row.get('path'), 500)}\n  {display(media)} · {display(free)} · {reason}")
            return "\n".join(formatted)
        roots = self.plan_data.get("roots", {})
        entries = [(label, roots.get(key, {}).get("path")) for label, key in zip(self.words["paths"][:4], ("workspace", "config", "cache", "temp"))]
        entries += [(self.words["paths"][4], self.plan_data.get("exchange", {}).get("in")), (self.words["paths"][5], self.plan_data.get("host_agent"))]
        storage = self.plan_data.get("storage", {})
        free = storage.get("free_bytes")
        explanation = "NO_MOVE · " + display(storage.get("media_type")) + (f" · {free / 2**30:.1f} GiB" if isinstance(free, int) else "")
        return "\n".join(f"{label}  {display(path, 500)}\n  {explanation}" for label, path in entries)

    def placement_reason(self, name: str | None, reason: Any) -> str:
        zh = self.words is TEXT["zh"]
        root = self.plan_data.get("roots", {}).get(name, {})
        if root.get("owner") == "UNKNOWN":
            return "目录所有权需核验" if zh else "Ownership needs verification"
        if name == "host_agent":
            redirected = self.plan_data.get("documents_state") == "ONEDRIVE_REDIRECTED"
            return ("OneDrive 重定向；原版本保护" if redirected else "系统文档目录；原版本保护") if zh else ("OneDrive; existing-version guard" if redirected else "Known Folder; existing-version guard")
        if name == "exchange":
            return "独立交换目录；保留原生状态" if zh else "Scoped exchange; preserve native state"
        if isinstance(reason, str) and ("NO_MOVE" in reason or "preserve" in reason.lower()):
            return "保留已有目录，不搬迁数据" if zh else "Preserve existing root; no migration"
        return "新建目录；当前磁盘规划" if zh else "New root on selected local storage"

    def result_summary(self) -> str:
        capabilities = self.result.get("capabilities", {})
        return "\n".join(f"{'✔' if capabilities.get(key, {}).get('state') == 'PASS' else '○'} {label} · {self.state_label(capabilities.get(key, {}).get('state'))}" for key, label in zip(("local_install", "github", "model", "fresh_recovery"), self.words["result_labels"]))

    def account_summary(self, kind: str) -> str:
        data = self.credentials.get(kind, {})
        identity = display(data.get("account") or data.get("provider") or data.get("label"))
        return f"{self.words[kind]} · {identity} · {self.state_label(data.get('state'))}\n{self.account_action(kind, data)}"

    def account_action(self, kind: str, data: dict) -> str:
        zh = self.words is TEXT["zh"]
        code = data.get("next_action")
        if code == "HOST_GITHUB_DEVICE_LOGIN":
            return "先由可信 GitHub 客户端发起设备授权，再按提示在 github.com/login/device 确认一次性代码。容器授权由电脑所有者另行完成；不要在向导输入密钥。" if zh else "Start device authorization in a trusted GitHub client, then confirm its one-time code at github.com/login/device. The owner separately authorizes runtime access; never enter keys here."
        if code == "HOST_PROVIDER_LOGIN":
            return "请使用所选提供商的官方登录或受保护输入，再由电脑所有者授权模型连接；也可暂时跳过。" if zh else "Use your provider's official sign-in or protected input, then ask the owner to authorize model access; or skip for now."
        if code == "REVIEW_SCOPED_CONNECTION":
            return "先核对下方账户、目标与权限，再明确批准短期连接。仍须实际验证才能就绪。" if zh else "Review the account, target and permissions below before approving bounded access. Actual verification is still required."
        return self.words["missing"]

    def plan_blocker(self) -> str:
        if self.plan_data.get("status") != "BLOCKED":
            return ""
        gate = next((item for item in self.plan_data.get("gates", []) if isinstance(item, dict) and item.get("state") == "BLOCKED"), {})
        raw = gate.get("code", "PLAN_BLOCKED")
        code = raw if isinstance(raw, str) and re.fullmatch(r"[A-Z0-9_]{1,64}", raw) else "PLAN_BLOCKED"
        zh = self.words is TEXT["zh"]
        if code.startswith("ROOT_"):
            remedy = "已有目录所有权无法确认。保留数据，改用新的目录或请所有者确认。" if zh else "Existing root ownership is unverified. Preserve data; select a new root or ask its owner."
        elif code.startswith("PLACEMENT_") or code == "STORAGE_CAPACITY":
            remedy = "请选择本地 NTFS/ReFS 目录，并保留至少 8 GiB 余量。" if zh else "Choose local NTFS/ReFS storage with at least 8 GiB free."
        elif code in {"CONTEXT_CURRENT", "DOCUMENTS_KNOWN_FOLDER"}:
            remedy = "请由电脑所有者核对系统文档目录及现有配置；不会覆盖未知数据。" if zh else "Ask the owner to verify Documents and existing configuration; unknown data remains untouched."
        elif code.startswith("WSL"):
            remedy = "需要 WSL 应用 3.0+ 与可用容器能力；请由所有者处理系统变更。" if zh else "WSL application 3.0+ and containers are required. System changes need the owner."
        elif code == "PYTHON_314":
            remedy = "需要官方签名的 Python 3.14；请返回受信任的启动入口。" if zh else "Verified official Python 3.14 is required; return to the trusted bootstrap."
        else:
            remedy = "安装前提未满足。保留当前数据，交由电脑所有者检查。" if zh else "Installation prerequisites are unmet. Preserve current data and ask the owner to check."
        return f"[{code}] {remedy}"

    def scope_summary(self, kind: str) -> str:
        data = self.credentials.get(kind, {})
        # Approved owners supply only metadata. Missing scope never silently authorizes.
        labels = ("账户", "仓库", "权限", "操作") if self.words is TEXT["zh"] else ("Account", "Repository", "Permissions", "Action")
        permissions = data.get("permissions") or data.get("scope")
        if isinstance(permissions, dict):
            permissions = ", ".join(f"{key}: {display(permissions[key], 16)}" for key in ("contents", "issues") if key in permissions)
        if data.get("next_action") in {"HOST_GITHUB_DEVICE_LOGIN", "HOST_PROVIDER_LOGIN"}:
            permissions = "尚未请求容器权限" if self.words is TEXT["zh"] else "No runtime permission requested"
        action = "所有者确认后连接" if self.words is TEXT["zh"] else "Connect after owner approval"
        fields = list(zip(labels, (data.get("account") or data.get("provider"), data.get("repository") or data.get("repo"), permissions, action)))
        return " · ".join(f"{label}: {display(value)}" for label, value in fields)

    async def render_step(self) -> None:
        self.query_one("#heading", Static).update(f"{self.words['title']} · {min(self.step + 1, 4)}/4 · {self.words['steps'][self.step]}")
        body = self.query_one("#body", VerticalScroll)
        await body.remove_children()
        widgets: list = []
        if self.step == 0:
            widgets = [Static(self.words["intro"], markup=False), Static(self.checks_summary(), id="checks", classes="summary", markup=False)]
            details = "Python: " + display(self.probe_data.get("python_version")) + "\nWSL: " + display(self.probe_data.get("wsl_app_version"))
            widgets.append(Collapsible(Static(details, markup=False), title=self.words["details"], collapsed=True))
            if self.root_overlap:
                widgets.append(Button('审阅新隔离目录方案（保留已有目录）' if self.words is TEXT['zh'] else 'Review separate roots; preserve existing data',id='review-isolated-roots'))
        elif self.step == 1:
            widgets = [Static(self.words["placement"], classes="section", markup=False), Static(self.placement_summary(), id="placement", markup=False)]
            state_text = ('上次核验方案；输入已改变，尚未采用' if self.placement_dirty else '当前已核验方案') if self.words is TEXT['zh'] else ('Last validated plan; edits not adopted' if self.placement_dirty else 'Current validated plan')
            widgets.insert(1, Static(state_text, id='placement-state', markup=False))
            if self.plan_data.get('isolated_scope_reviewed'):
                widgets.append(Static('仅审阅新目录方案；已有目录和原生 OpenCode 保留。实际安装仍需单独授权。' if self.words is TEXT['zh'] else 'Review only: existing directories and native OpenCode preserved. Installation requires separate approval.',markup=False))
            advanced: list = []
            zh = self.words is TEXT['zh']
            advanced.append(Static('空白输入框使用自动推荐；灰色路径仅为预览。输入或浏览后会改为自定义，重新核验后才成为方案。' if zh else 'Empty fields use recommendations; grey paths are previews. Type or browse to customize, then revalidate.', id='placement-help', markup=False))
            advanced.append(Horizontal(Button('自动推荐' if zh else 'Automatic', id='placement-auto', variant='primary' if self.placement_mode=='auto' else 'default'), Button('自定义' if zh else 'Custom', id='placement-custom', variant='primary' if self.placement_mode=='custom' else 'default'), classes='account-actions'))
            if self.overrides.get('isolated_scope'):
                scope = Path(self.overrides['isolated_scope'])
                advanced.append(Static('先选择安装父目录，再填写四类新子目录的名称。程序会在父目录内新建独立目录，保留已有数据；下方名称不能填写盘符或绝对路径。预览不会创建任何安装目录。' if zh else 'Choose an existing installation parent, then name four new subfolders. A separate namespace preserves existing data. Enter names below, not drive letters or absolute paths. Preview creates no installation directories.', markup=False))
                advanced.append(Label('安装父目录（已有文件夹）' if zh else 'Installation parent (existing folder)'))
                advanced.append(Horizontal(Input(value=self.placement_parent_draft if self.placement_parent_draft is not None else str(scope.parent), id='isolated-parent'), Button('选择父目录…' if zh else 'Choose parent…', id='browse-isolated-parent'), classes='account-actions'))
                advanced.append(Static(('将新建独立目录：' if zh else 'New separate namespace: ') + display(str(scope), 500), markup=False))
            for key, label in zip(("workspace", "config", "cache", "temp"), self.words["paths"]):
                mode = ('自定义值' if zh else 'Custom value') if self.overrides.get(key) else ('自动推荐 · 仅预览' if zh else 'Recommended preview')
                path = self.plan_data.get('roots', {}).get(key, {}).get('path')
                if self.overrides.get('isolated_scope'):
                    advanced += [Label(f'{label} · 新子目录名称 · {mode}' if zh else f'{label} · New subfolder name · {mode}', id=f'root-label-{key}'), Input(value=self.root_field_value(key), placeholder=Path(path).name if path else '', id=f'root-{key}')]
                else:
                    advanced += [Label(f'{label} · {mode}', id=f'root-label-{key}'), Horizontal(Input(value=self.root_field_value(key), placeholder=display(path), id=f"root-{key}"), Button('浏览…' if zh else 'Browse…', id=f'browse-{key}'), classes='account-actions')]
            advanced.append(Button(self.words["recompute"], id="recompute"))
            widgets.append(Collapsible(*advanced, title=self.words["advanced"], collapsed=not self.advanced_open, id="advanced"))
        elif self.step == 2:
            widgets = [Static(self.words["accounts"], markup=False), Horizontal(Button(self.words["auto"], id="mode-auto", variant="primary" if self.mode == "auto" else "default"), Button(self.words["manual"], id="mode-manual", variant="primary" if self.mode == "manual" else "default"), classes="account-actions")]
            for kind in ("github", "model"):
                data = self.credentials.get(kind, {})
                diagnostic = "\n".join(display(data.get(key)) for key in ("reason_code", "manual_next_action", "next_action"))
                widgets += [Static(self.account_summary(kind), id=f"account-{kind}", classes="section", markup=False), Static(self.scope_summary(kind), markup=False), Checkbox(f"{self.words[kind]}: {self.words['credential_approve']}", id=f"approve-{kind}"), Horizontal(Button(self.words["connect"], id=f"connect-{kind}", disabled=True), Button(self.words["skip"], id=f"skip-{kind}"), classes="account-actions"), Collapsible(Static(diagnostic, markup=False), title=self.words["details"], collapsed=True)]
        elif self.step == 3:
            changes = "核验安装目录并写入 HOST_AGENT.md。" if self.words is TEXT["zh"] else "Verify owned roots and write HOST_AGENT.md."
            if self.overrides.get("runtime"):
                changes += " 拉取固定公开镜像；启动隔离本地验证容器（暂不联网）。" if self.words is TEXT["zh"] else " Pull the pinned public image; start an isolated local verification container (offline)."
            widgets = [Static(self.words["review"], markup=False), Static(changes, markup=False), Static(self.placement_summary(), classes="summary", markup=False), Checkbox(self.words["local"], value=bool(self.overrides.get("runtime")), id="runtime-requested"), Checkbox(self.words["approve"], id="approve"), Button(self.words["apply"], id="apply", disabled=True)]
        else:
            widgets = [Static(self.result_summary(), id="results", classes="summary", markup=False), Button(self.words["verify"], id="verify"), Button(self.words["repair"], id="repair")]
            if not self.result:
                widgets.insert(0, Static(self.words["preview"], markup=False))
        if self.probe_data.get('runtime_provenance',{}).get('distribution')=='UNSIGNED_TEST_ONLY':
            widgets.insert(0,Static('未签名测试版本 · 仅预览；内容核验不代表发布者签名。' if self.words is TEXT['zh'] else 'Unsigned test build · preview only; content verification is not publisher signing.',id='unsigned-notice',markup=False))
        await body.mount(*widgets)
        self.query_one("#back", Button).disabled = self.step == 0 or self.busy
        self.query_one("#next", Button).disabled = self.step == 4 or self.busy
        self.query_one("#next", Button).focus()
        blocker = self.plan_blocker() if self.step in {1, 3} else ""
        if blocker:
            self.set_status(blocker)
        elif self.step == 3 and not self.host_authorized:
            self.set_status(self.words["blocked"])

    def set_status(self, value: str) -> None:
        self.status_text=value
        self.query_one("#status", Static).update(value)

    def invalidate_approval(self) -> None:
        self.approved_fingerprint = None
        if self.step == 3 and self.query("#approve"):
            self.query_one("#approve", Checkbox).value = False
            self.query_one("#apply", Button).disabled = True

    def save_fields(self) -> bool:
        if self.step == 1:
            candidate = dict(self.overrides)
            for key in ("workspace", "config", "cache", "temp"):
                value = self.query_one(f"#root-{key}", Input).value.strip()
                if value and self.overrides.get('isolated_scope'):
                    if (value in {'.','..'} or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
                        or value.endswith(('.', ' ')) or re.fullmatch(r'(?:CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\..*)?', value, re.I)):
                        self.set_status('这里只填写新子目录名称；安装位置请在“安装父目录”中选择。输入尚未采用。' if self.words is TEXT['zh'] else 'Enter a new subfolder name here. Select the installation location in Parent. Input has not been adopted.')
                        return False
                    value = str(Path(self.overrides['isolated_scope']) / value)
                if value:
                    candidate[key] = value
                else:
                    candidate.pop(key, None)
            self.overrides = candidate
        return True

    async def recalculate_placement(self, *, new_parent_selected: bool = False) -> bool:
        """Resolve UI names through the existing owner-reviewed parent contract."""
        if not self.save_fields():
            return False
        if not await self.refresh_probe():
            return False
        if self.overrides.get('isolated_scope'):
            parent = self.query_one('#isolated-parent', Input).value.strip()
            scope = Path(self.overrides['isolated_scope'])
            if new_parent_selected or parent != str(scope.parent):
                proposal = await self.invoke('propose_isolated_roots', self.probe_data, parent=parent)
                if proposal is None:
                    return False
                candidate = dict(self.overrides)
                candidate['isolated_scope'] = proposal['isolated_scope']
                for role in ('workspace','config','cache','temp'):
                    if role in candidate:
                        candidate[role] = str(Path(proposal['isolated_scope']) / Path(candidate[role]).name)
                plan = await self.invoke('plan', self.probe_data, overrides=candidate, github=self.github, model=self.model, durable=self.durable)
                if plan is None:
                    return False
                self.overrides, self.plan_data = candidate, plan
                self.placement_dirty = False
                self.placement_parent_draft = None
                self.set_status('')
                return True
        return await self.replan()

    async def pick_directory(self, initial_path: str | None, title: str) -> str | None:
        """The only dialog seam; the original engine validates every returned path."""
        old_status = self.status_text
        self.busy = True
        self.set_status(self.words['busy'])
        try:
            from .folder_picker import choose_folder
            selected = await asyncio.to_thread(self.folder_picker or choose_folder, initial_path=initial_path, title=title)
            if selected is not None and (not isinstance(selected, str) or not selected):
                raise ValueError('INVALID_FOLDER_RESULT')
            self.set_status(old_status)
            return selected
        except Exception as error:
            from .folder_picker import FolderPickerError
            code = str(error) if isinstance(error, FolderPickerError) else 'FOLDER_PICKER_FAILED'
            if not re.fullmatch(r'FOLDER_PICKER_[A-Z_]{1,48}', code):
                code = 'FOLDER_PICKER_FAILED'
            self.set_status(f"{self.words['error']} [{code}]")
            return None
        finally:
            self.busy = False

    async def refresh_probe(self) -> bool:
        result = await self.invoke('probe')
        if result is None:
            return False
        self.probe_data = result
        return True

    async def browse_root(self, role: str) -> None:
        initial = self.query_one(f'#root-{role}', Input).value or self.plan_data.get('roots', {}).get(role, {}).get('path')
        selected = await self.pick_directory(initial, ('选择' if self.words is TEXT['zh'] else 'Choose ') + dict(zip(('workspace','config','cache','temp'), self.words['paths']))[role])
        if selected is None:
            self.query_one(f'#browse-{role}', Button).focus()
            return
        self.save_fields()
        self.invalidate_approval()
        self.placement_mode = 'custom'
        self.advanced_open = True
        self.overrides[role] = selected
        self.query_one(f'#root-{role}', Input).value = selected
        if await self.refresh_probe() and await self.replan():
            await self.render_step()
        self.query_one(f'#root-{role}', Input).focus()

    async def browse_isolated_parent(self) -> None:
        selected = await self.pick_directory(self.overrides.get('isolated_scope'), '选择隔离根的父目录（不搬迁已有数据）' if self.words is TEXT['zh'] else 'Choose a parent for a fresh isolation root (preserve data)')
        if selected is None:
            self.query_one('#browse-isolated-parent', Button).focus()
            return
        self.invalidate_approval()
        self.query_one('#isolated-parent', Input).value = selected
        if not await self.recalculate_placement(new_parent_selected=True):
            return
        self.advanced_open = True
        self.root_overlap = False
        self.set_status('')
        await self.render_step()
        self.query_one('#browse-isolated-parent', Button).focus()

    async def invoke(self, phase: str, *args: Any, **kwargs: Any) -> dict | None:
        self.busy = True
        self.set_status(self.words["busy"])
        try:
            return await asyncio.to_thread(getattr(self.engine, phase), *args, **kwargs)
        except Exception as exc:
            # SetupError carries stable internal codes, not upstream text or
            # secrets. Keep unexpected exceptions generic and unexposed.
            from .engine import SetupError
            code=str(exc) if isinstance(exc,SetupError) else ''
            safe_code=code if re.fullmatch(r'[A-Z][A-Z0-9_]{1,63}',code) else ('INPUT' if isinstance(exc,(ValueError,TypeError)) else 'OPERATION')
            explanation=''
            prefix=self.words['error']
            if safe_code=='EXISTING_ROOT_METADATA_INVALID' and isinstance(exc,SetupError):
                prefix='目录契约需审查' if self.words is TEXT['zh'] else 'Root contract needs review'
                from .engine import metadata_diagnostics
                names=dict(zip(('workspace','config','cache','temp'),self.words['paths']))
                names.update({'state':'原生状态' if self.words is TEXT['zh'] else 'Native state','exchange':'Exchange','context':'既有契约' if self.words is TEXT['zh'] else 'Existing contract'})
                for error in metadata_diagnostics(exc.metadata_errors):
                    explanation+=f" {names[error['role']]} · {error['reason']}"
                explanation+=('；旧目录保留。请电脑所有者运行只读目录诊断并交维护者审查；不要编辑、删除配置或目录。' if self.words is TEXT['zh'] else '; old roots preserved. Owner: run read-only root diagnostics for maintainer review. Do not edit or delete configuration or directories.')
            if safe_code=='ROOT_OVERLAP' and isinstance(exc,SetupError):
                self.root_overlap=True
                names=dict(zip(('workspace','config','cache','temp'),self.words['paths']))
                for conflict in exc.conflicts:
                    roles=conflict.get('roles',[])
                    if len(roles)!=2 or any(role not in names for role in roles):continue
                    relation=conflict.get('relation')
                    if relation not in {'SAME_DIRECTORY','CONTAINS'}:continue
                    pair=' / '.join(names[role] for role in roles)
                    explanation+=f" {pair}: "+(('指向同一目录' if relation=='SAME_DIRECTORY' else '目录包含关系冲突') if self.words is TEXT['zh'] else ('same directory' if relation=='SAME_DIRECTORY' else 'directory containment conflict'))
                explanation+=('；保留已有数据，请审阅独立的新作用域目录。可运行只读目录诊断。' if self.words is TEXT['zh'] else '; preserve existing data, review separate scoped roots. Read-only root diagnostics are available.')
            if safe_code=='ISOLATED_SCOPE_TARGET_ESCAPE':
                explanation+=(' 自定义子目录必须位于当前隔离根内。要换磁盘，请明确选择“重新选择隔离根目录/磁盘”，审阅新方案；已有数据保留。' if self.words is TEXT['zh'] else ' Custom folders must stay inside the current isolation root. To change disk, explicitly reselect the isolation parent and review a new plan; preserve existing data.')
            self.set_status(f"{prefix} [{safe_code}]{explanation}")
            return None
        finally:
            self.busy = False

    async def replan(self) -> bool:
        self.invalidate_approval()
        result = await self.invoke("plan", self.probe_data, overrides=self.overrides, github=self.github, model=self.model, durable=self.durable)
        if result is None:
            if self.root_overlap and self.step==0:
                status=self.status_text
                await self.render_step()
                self.set_status(status)
            return False
        self.plan_data = result
        self.placement_dirty = False
        self.placement_parent_draft = None
        self.set_status("")
        return True

    async def advance(self) -> None:
        if self.busy or self.step == 4:
            return
        if self.step == 1:
            if not await self.recalculate_placement():
                return
        elif not self.save_fields():
            return
        if self.step == 0:
            result = await self.invoke("probe")
            if result is None:
                return
            self.probe_data = result
        if self.step != 1 and not await self.replan():
            return
        if self.step == 1:
            result = await self.invoke("discover_credentials")
            if result is not None:
                self.credentials = result
        self.step += 1
        self.set_status("")
        await self.render_step()

    async def action_back(self) -> None:
        if self.step and not self.busy:
            if not self.save_fields():
                return
            self.invalidate_approval()
            self.step -= 1
            self.set_status("")
            await self.render_step()

    async def on_input_changed(self, event: Input.Changed) -> None:
        self.invalidate_approval()
        if self.step == 1 and event.input.id == 'isolated-parent':
            if event.value != str(Path(self.overrides['isolated_scope']).parent):
                self.placement_parent_draft = event.value
                self.placement_dirty = True
                self.query_one('#placement-state', Static).update('上次核验方案；父目录输入尚未采用' if self.words is TEXT['zh'] else 'Last validated plan; parent edit not adopted')
                self.set_status('安装父目录已改变；请选择“重新规划”核验新方案。' if self.words is TEXT['zh'] else 'Parent changed; recalculate to validate the new plan.')
        if self.step == 1 and (event.input.id or '').startswith('root-'):
            role = event.input.id.removeprefix('root-')
            if role not in ('workspace','config','cache','temp'):
                return
            if event.value:
                self.placement_mode = 'custom'
            if event.value.strip() != self.root_field_value(role):
                self.placement_dirty = True
                zh = self.words is TEXT['zh']
                label = dict(zip(('workspace','config','cache','temp'), self.words['paths']))[role]
                self.query_one(f'#root-label-{role}', Label).update(label + (' · 待重新核验' if zh else ' · Pending revalidation'))
                self.query_one('#placement-state', Static).update('上次核验方案；输入已改变，尚未采用' if zh else 'Last validated plan; input edit not adopted')
                self.set_status('目录输入已改变；当前预览尚未更新。请选择“重新规划”重新核验。' if zh else 'Directory input changed; preview is stale. Recalculate to revalidate.')

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id in {"approve-github", "approve-model"}:
            kind = event.checkbox.id.removeprefix("approve-")
            self.query_one(f"#connect-{kind}", Button).disabled = not (event.value and self.host_authorized)
        elif event.checkbox.id == "runtime-requested" and self.step == 3 and event.value != bool(self.overrides.get("runtime")):
            self.overrides["runtime"] = event.value
            await self.replan()
            await self.render_step()
        elif event.checkbox.id == "approve" and self.step == 3:
            self.approved_fingerprint = self.plan_data.get("fingerprint") if event.value else None
            self.query_one("#apply", Button).disabled = not (event.value and self.host_authorized and self.plan_data.get("status") == "READY" and self.plan_data.get("host_authorized") is True and not self.busy)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.busy:
            return
        action = event.button.id or ""
        if action == "next":
            await self.advance()
        elif action=='review-isolated-roots' and self.step==0 and self.root_overlap:
            proposal=await self.invoke('propose_isolated_roots',self.probe_data)
            if proposal is not None:
                self.overrides['isolated_scope']=proposal['isolated_scope']
                if await self.replan():
                    self.root_overlap=False
                    self.step=1
                    await self.render_step()
        elif action == "back":
            await self.action_back()
        elif action == "recompute":
            self.advanced_open = True
            if await self.recalculate_placement():
                await self.render_step()
        elif action.startswith('browse-') and self.step == 1:
            role = action.removeprefix('browse-')
            if role == 'isolated-parent' and self.overrides.get('isolated_scope'):
                await self.browse_isolated_parent()
            elif role in ('workspace','config','cache','temp'):
                await self.browse_root(role)
        elif action == 'placement-auto' and self.step == 1:
            self.invalidate_approval()
            self.placement_parent_draft = None
            for role in ('workspace','config','cache','temp'):
                self.overrides.pop(role, None)
            self.placement_mode, self.advanced_open = 'auto', True
            for role in ('workspace','config','cache','temp'):
                self.query_one('#root-' + role, Input).value = ''
            if await self.refresh_probe() and await self.replan():
                await self.render_step()
        elif action == 'placement-custom' and self.step == 1:
            self.placement_mode, self.advanced_open = 'custom', True
            if not self.save_fields():
                return
            await self.render_step()
            self.query_one('#root-workspace', Input).focus()
        elif action.startswith("mode-"):
            self.mode = action.removeprefix("mode-")
            self.invalidate_approval()
            await self.render_step()
        elif action.startswith("skip-"):
            kind = action.removeprefix("skip-")
            setattr(self, kind, {})
            self.credentials[kind] = {"state": "SKIPPED"}
            self.invalidate_approval()
            await self.render_step()
        elif action.startswith("connect-"):
            kind = action.removeprefix("connect-")
            if not self.host_authorized or not self.query_one(f"#approve-{kind}", Checkbox).value:
                return
            result = await self.invoke("connect_credential", kind, self.mode, approved=True)
            if result is not None:
                self.credentials[kind] = result
                inputs = result.get("plan_inputs", {})
                if isinstance(inputs, dict) and isinstance(inputs.get(kind), dict):
                    setattr(self, kind, inputs[kind])
                else:
                    setattr(self, kind, {})
                self.invalidate_approval()
                await self.render_step()
        elif action == "apply":
            if self.step != 3 or not self.host_authorized or self.plan_data.get("host_authorized") is not True or self.plan_data.get("status") != "READY" or not self.query_one("#approve", Checkbox).value or self.approved_fingerprint != self.plan_data.get("fingerprint"):
                return
            result = await self.invoke("apply", self.plan_data, approved=True)
            if result is not None:
                self.result, self.step = result, 4
                self.set_status("")
                await self.render_step()
        elif action in ("verify", "repair"):
            result = await self.invoke(action, self.plan_data)
            if result is not None:
                self.result = result
                self.set_status("")
                await self.render_step()


def run_tui(engine: Any, *, locale: str = "zh", host_authorized: bool = False) -> None:
    SetupApp(engine, locale=locale, host_authorized=host_authorized).run()
