"""Keyboard-first presentation only; all Host decisions belong to SetupEngine."""
from __future__ import annotations

import asyncio
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Checkbox, Footer, Input, Label, Static


TEXT = {
    "zh": {
        "title": "Agent Runtime 首次设置", "steps": ["欢迎 / 预检", "存储检查", "目录方案", "GitHub 身份", "模型身份", "审查 / 应用", "验证 / 结果"],
        "back": "上一步", "next": "下一步", "apply": "应用已审查方案", "verify": "验证", "repair": "生成修复方案", "approve": "我已审查并授权本次 Host 变更", "blocked": "等待具体 Host 授权；当前可审查方案", "error": "操作失败；未显示原始错误。请检查恢复方案。", "intro": "只检查当前环境并生成方案。不会自动升级 WSL、重启或迁移现有数据。", "identity": "填写引用与已批准 helper 路径。不要输入 token、密码或私钥。", "free": "公共免费路由是可选项，不代表付费身份验证通过。", "review": "检查各目录、原因与权限后，再明确授权应用。", "busy": "正在检查…",
    },
    "en": {
        "title": "Agent Runtime first-run setup", "steps": ["Welcome / preflight", "Storage", "Placement", "GitHub identity", "Model identity", "Review / apply", "Verify / results"],
        "back": "Back", "next": "Next", "apply": "Apply reviewed plan", "verify": "Verify", "repair": "Plan repair", "approve": "I reviewed and authorize these Host changes", "blocked": "Concrete Host authority required; plan review available", "error": "Operation failed; raw error suppressed. Check the recovery plan.", "intro": "Inspect and plan first. No automatic WSL upgrade, reboot, or existing-data migration.", "identity": "Enter references and approved helper paths only. Never enter tokens, passwords, or private keys.", "free": "Optional public free route does not prove paid-provider authentication.", "review": "Review roots, reasons, and authority before explicitly applying.", "busy": "Checking…",
    },
}
TEXT["zh"].update(github_ref="GitHub 身份引用", helper="已批准 helper 路径", durable="私有持久目标（可选，由所有者选择）", model_ref="模型身份引用", free_route="选用公共免费路由", root_override="可选：已批准目录覆盖")
TEXT["en"].update(github_ref="GitHub SecretReference", helper="Approved helper path", durable="Owner-selected private durable destination (optional)", model_ref="Model SecretReference", free_route="Optional public free route", root_override="Optional approved root override")
TEXT["zh"].update(work="GitHub Work 坐标", helper_approved="批准查询现有 helper 的身份元数据", github_authorized="授权本次 Work 的 GitHub 读写", durable_authorized="授权所选私有持久目标", recovery_requested="请求验证 GitHub fresh recovery", runtime_requested="请求拉取固定镜像并启动本次 runtime", declarations="这些选项是授权声明；只有实际验证通过才能报告 READY。")
TEXT["en"].update(work="GitHub Work coordinate", helper_approved="Approve metadata queries of existing helper", github_authorized="Authorize GitHub read/write for this Work", durable_authorized="Authorize selected private durable destination", recovery_requested="Request GitHub fresh recovery verification", runtime_requested="Request pinned-image pull and runtime start", declarations="These selections declare authority; READY still requires actual proof.")


class SetupApp(App):
    """An injected engine enables deterministic headless tests without Host mutation."""

    CSS = """
    Screen { background: $surface; }
    #heading { height: 3; content-align: center middle; text-style: bold; }
    #body { height: 1fr; padding: 1 2; }
    #status { height: auto; min-height: 2; padding: 0 2; }
    #controls { height: auto; padding: 1 2; }
    Button { margin-right: 1; }
    Input { margin-bottom: 1; }
    .summary { height: auto; margin-bottom: 1; }
    """
    BINDINGS = [("escape", "back", "Back"), ("ctrl+q", "quit", "Quit"), ("up", "focus_previous", "Previous"), ("down", "focus_next", "Next")]

    def __init__(self, engine: Any, *, locale: str = "zh", host_authorized: bool = False):
        super().__init__()
        self.engine = engine
        self.words = TEXT.get(locale, TEXT["zh"])
        self.host_authorized = host_authorized
        self.step = 0
        self.probe_data: dict = {}
        self.plan_data: dict = {}
        self.result: dict = {}
        self.overrides: dict = {"host_authorized": True} if host_authorized else {}
        self.github: dict = {}
        self.model: dict = {}
        self.durable: dict = {}
        self.busy = False

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

    def summary(self, data: dict) -> str:
        # Engine returns only safe metadata. Project a bounded, intentional surface,
        # never arbitrary nested provider output or exception text.
        lines = []
        for key in ("status", "reason", "reasons", "platform", "python_version", "wsl_app_version", "wslc_capability", "storage_state", "active_workloads", "gates", "placement", "roots", "exchange", "domains", "operations", "checks"):
            if key in data:
                lines.append(f"{key}: {data[key]}")
        for volume in data.get("volumes", []):
            if isinstance(volume, dict):
                free = volume.get("free_bytes")
                capacity = volume.get("capacity_bytes")
                space = f"{free / 2**30:.1f}/{capacity / 2**30:.1f} GiB free" if isinstance(free, int) and isinstance(capacity, int) else "capacity UNKNOWN"
                lines.append(f"{volume.get('mount', '?')} · {volume.get('fs', '?')} · {volume.get('media_type', '?')} · {volume.get('bus_type', '?')} · {space}")
        return "\n".join(lines) or "—"

    async def render_step(self) -> None:
        self.query_one("#heading", Static).update(f"{self.words['title']} · {self.step + 1}/7 · {self.words['steps'][self.step]}")
        body = self.query_one("#body", VerticalScroll)
        await body.remove_children()
        widgets: list = []
        if self.step == 0:
            widgets = [Static(self.words["intro"], markup=False)]
        elif self.step == 1:
            widgets = [Static(self.summary(self.probe_data), classes="summary", markup=False)]
        elif self.step == 2:
            widgets = [Static(self.summary(self.plan_data), classes="summary", markup=False)]
            for key in ("workspace", "config", "cache", "temp"):
                widgets.extend([Label(key), Input(value=self.overrides.get(key, ""), placeholder=self.words["root_override"], id=f"root-{key}")])
        elif self.step == 3:
            widgets = [
                Static(self.words["identity"], markup=False),
                Label(self.words["github_ref"]), Input(value=self.github.get("ref", ""), id="github-reference"),
                Label(self.words["helper"]), Input(value=self.github.get("helper", ""), id="github-helper"),
                Label(self.words["work"]), Input(value=self.github.get("work", ""), placeholder="owner/repository#123", id="github-work"),
                Checkbox(self.words["helper_approved"], value=bool(self.github.get("helper_approved")), id="github-helper-approved"),
                Checkbox(self.words["github_authorized"], value=bool(self.github.get("authorized")), id="github-authorized"),
                Label(self.words["durable"]), Input(value=self.durable.get("destination", ""), placeholder="owner/repository", id="durable-repository"),
                Checkbox(self.words["durable_authorized"], value=bool(self.durable.get("authorized")), id="durable-authorized"),
                Checkbox(self.words["recovery_requested"], value=bool(self.github.get("recovery_requested")), id="recovery-requested"),
                Static(self.words["declarations"], markup=False),
            ]
        elif self.step == 4:
            widgets = [Static(self.words["free"], markup=False), Label(self.words["model_ref"]), Input(value=self.model.get("ref", ""), id="model-reference"), Label(self.words["helper"]), Input(value=self.model.get("helper", ""), id="model-helper"), Checkbox(self.words["free_route"], value=bool(self.model.get("free_route")), id="free-route")]
        elif self.step == 5:
            widgets = [Static(self.words["review"], markup=False), Static(self.summary(self.plan_data), classes="summary", markup=False), Checkbox(self.words["runtime_requested"], value=bool(self.overrides.get("runtime")), id="runtime-requested"), Static(self.words["declarations"], markup=False), Checkbox(self.words["approve"], id="approve"), Button(self.words["apply"], id="apply", disabled=True)]
        else:
            widgets = [Static(self.summary(self.result), classes="summary", markup=False), Button(self.words["verify"], id="verify"), Button(self.words["repair"], id="repair")]
        await body.mount(*widgets)
        self.query_one("#back", Button).disabled = self.step == 0 or self.busy
        self.query_one("#next", Button).disabled = self.step == 6 or self.busy
        self.query_one("#next", Button).focus()
        if self.step == 5 and not self.host_authorized:
            self.set_status(self.words["blocked"])

    def set_status(self, value: str) -> None:
        self.query_one("#status", Static).update(value)

    def save_fields(self) -> None:
        if self.step == 2:
            runtime = self.overrides.get("runtime", False)
            self.overrides = {key: self.query_one(f"#root-{key}", Input).value.strip() for key in ("workspace", "config", "cache", "temp") if self.query_one(f"#root-{key}", Input).value.strip()}
            if runtime:
                self.overrides["runtime"] = True
            if self.host_authorized:
                self.overrides["host_authorized"] = True
        elif self.step == 3:
            self.github = {"ref": self.query_one("#github-reference", Input).value.strip(), "helper": self.query_one("#github-helper", Input).value.strip(), "work": self.query_one("#github-work", Input).value.strip(), "helper_approved": self.query_one("#github-helper-approved", Checkbox).value, "authorized": self.query_one("#github-authorized", Checkbox).value, "recovery_requested": self.query_one("#recovery-requested", Checkbox).value}
            self.durable = {"destination": self.query_one("#durable-repository", Input).value.strip(), "authorized": self.query_one("#durable-authorized", Checkbox).value}
        elif self.step == 4:
            self.model = {"ref": self.query_one("#model-reference", Input).value.strip(), "helper": self.query_one("#model-helper", Input).value.strip(), "free_route": self.query_one("#free-route", Checkbox).value}

    async def invoke(self, phase: str, *args: Any, **kwargs: Any) -> dict | None:
        self.busy = True
        self.set_status(self.words["busy"])
        try:
            return await asyncio.to_thread(getattr(self.engine, phase), *args, **kwargs)
        except Exception as exc:
            # Exception messages and traces may contain credentials or raw helper output.
            category = "INPUT" if isinstance(exc, (ValueError, TypeError)) else "OPERATION"
            self.set_status(f"{self.words['error']} [{category}]")
            return None
        finally:
            self.busy = False

    async def advance(self) -> None:
        if self.busy or self.step == 6:
            return
        self.save_fields()
        if self.step == 0:
            result = await self.invoke("probe")
            if result is None:
                return
            self.probe_data = result
        if self.step in (1, 2, 3, 4):
            result = await self.invoke("plan", self.probe_data, overrides=self.overrides, github=self.github, model=self.model, durable=self.durable)
            if result is None:
                return
            self.plan_data = result
        self.set_status("")
        self.step += 1
        await self.render_step()

    async def action_back(self) -> None:
        if self.step and not self.busy:
            self.save_fields()
            self.step -= 1
            self.set_status("")
            await self.render_step()

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "runtime-requested" and self.step == 5 and event.value != bool(self.overrides.get("runtime")):
            self.overrides["runtime"] = event.value
            self.query_one("#approve", Checkbox).value = False
            self.query_one("#apply", Button).disabled = True
            self.plan_data = {}
            result = await self.invoke("plan", self.probe_data, overrides=self.overrides, github=self.github, model=self.model, durable=self.durable)
            if result is not None:
                self.plan_data = result
                self.set_status("")
                await self.render_step()
            return
        if event.checkbox.id == "approve" and self.step == 5:
            self.query_one("#apply", Button).disabled = not (event.value and self.host_authorized and self.plan_data.get("status") == "READY" and self.plan_data.get("host_authorized") is True and not self.busy)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.busy:
            return
        action = event.button.id
        if action == "next":
            await self.advance()
        elif action == "back":
            await self.action_back()
        elif action == "apply":
            if self.step != 5 or not self.host_authorized or self.plan_data.get("host_authorized") is not True or self.plan_data.get("status") != "READY" or not self.query_one("#approve", Checkbox).value:
                return
            result = await self.invoke("apply", self.plan_data, approved=True)
            if result is not None:
                self.result = result
                self.step = 6
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
