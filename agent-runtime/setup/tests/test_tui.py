"""Actual Textual Pilot tests against explicitly synthetic owner metadata."""
import asyncio
import pytest
from textual.widgets import Button, Checkbox, Input, Static
from agent_setup.tui import SetupApp, display


class FakeEngine:
    def __init__(self, *, blocked=False, fail=False, states=None):
        self.calls, self.blocked, self.fail = [], blocked, fail
        self.states = states or {"github": "REUSE_NOT_SUPPORTED", "model": "NEEDS_CONNECTION"}
        self.generation = 0

    def probe(self):
        self.calls.append("probe")
        if self.fail:
            raise RuntimeError("SECRET_SHOULD_NEVER_APPEAR")
        return {"platform": "windows", "python_verified": True, "python_version": "3.14.8", "wsl_app_version": "3.0.1", "wslc_capability": {"state": "PASS"}, "volumes": [{"fs": "NTFS", "free_bytes": 80 * 2**30}]}

    def plan(self, probe, **kwargs):
        self.calls.append(("plan", kwargs))
        self.generation += 1
        return {"fingerprint": str(self.generation), "status": "BLOCKED" if self.blocked else "READY", "host_authorized": kwargs["overrides"].get("host_authorized", False), "roots": {key: {"path": kwargs["overrides"].get(key, f"C:/Fixture/{key}"), "reason": "NO_MOVE"} for key in ("workspace", "config", "cache", "temp")}, "exchange": {"in": "C:/Fixture/exchange/in"}, "host_agent": "C:/Fixture/Documents/HOST_AGENT.md", "storage": {"media_type": "NVMe SSD", "free_bytes": 80 * 2**30}}

    def discover_credentials(self):
        self.calls.append("discover")
        return {kind: {"state": state, "account": "fixture-user" if kind == "github" else "fixture-provider", "repo": "fixture/repository", "permissions": "bounded read/write", "action": "owner projection", "reusable": state == "AVAILABLE"} for kind, state in self.states.items()}

    def connect_credential(self, kind, mode, approved=False):
        self.calls.append(("connect", kind, mode, approved))
        state = "PASS" if self.states[kind] == "AVAILABLE" else "HUMAN_GATE"
        return {"state": state, "plan_inputs": {kind: {"ref": "fixture.reference", "authorized": True}} if state == "PASS" else {}}

    def apply(self, plan, approved=False):
        self.calls.append(("apply", approved, plan["fingerprint"]))
        return {"status": "APPLIED", "capabilities": {"local_install": {"state": "PASS"}, "github": {"state": "NOT_AUTHORIZED"}, "model": {"state": "NOT_AUTHORIZED"}, "fresh_recovery": {"state": "NOT_AUTHORIZED"}}}

    def verify(self, plan):
        self.calls.append("verify")
        return {"capabilities": {"local_install": {"state": "PASS"}, "github": {"state": "REVOKED"}, "model": {"state": "PASS"}, "fresh_recovery": {"state": "BLOCKED"}}}

    def repair(self, plan):
        return {"status": "BLOCKED"}


async def press_button(app, pilot, selector):
    app.query_one(selector, Button).focus()
    await pilot.press("enter")
    await pilot.pause(0.4)


async def to_review(app, pilot):
    for _ in range(3):
        await press_button(app, pilot, "#next")
    assert app.step == 3


def test_keyboard_preview_apply_independent_results():
    async def scenario():
        engine = FakeEngine()
        app = SetupApp(engine, host_authorized=True)
        async with app.run_test(size=(80, 24)) as pilot:
            await to_review(app, pilot)
            assert app.query_one("#apply", Button).disabled
            app.query_one("#approve", Checkbox).focus()
            await pilot.press("space")
            await pilot.pause()
            await press_button(app, pilot, "#apply")
            assert app.step == 4
            text = str(app.query_one("#results", Static).render())
            assert "✔ 本地容器已安装" in text
            assert "○ GitHub 已连接" in text and "○ 模型已就绪" in text
            await press_button(app, pilot, "#verify")
            text = str(app.query_one("#results", Static).render())
            assert "✔ 模型已就绪" in text and "○ GitHub 已连接" in text
            assert app.query_one("#controls").region.bottom <= 24
    asyncio.run(scenario())


@pytest.mark.parametrize("authority,blocked", [(False, False), (True, True)])
def test_preview_and_blocked_plan_cannot_apply(authority, blocked):
    async def scenario():
        engine = FakeEngine(blocked=blocked)
        app = SetupApp(engine, host_authorized=authority)
        async with app.run_test(size=(80, 24)) as pilot:
            await to_review(app, pilot)
            app.query_one("#approve", Checkbox).value = True
            await pilot.pause()
            assert app.query_one("#apply", Button).disabled
            await press_button(app, pilot, "#next")
            assert app.step == 4
            assert not any(isinstance(c, tuple) and c[0] == "apply" for c in engine.calls)
    asyncio.run(scenario())


@pytest.mark.parametrize("states", [{"github": "AVAILABLE", "model": "AVAILABLE"}, {"github": "REUSE_NOT_SUPPORTED", "model": "NEEDS_CONNECTION"}, {"github": "AVAILABLE", "model": "NEEDS_CONNECTION"}, {"github": "NEEDS_CONNECTION", "model": "AVAILABLE"}, {"github": "NEEDS_CONNECTION", "model": "NEEDS_CONNECTION"}])
def test_auto_manual_partial_accounts_and_explicit_consent(states):
    async def scenario():
        engine = FakeEngine(states=states)
        app = SetupApp(engine, host_authorized=True)
        async with app.run_test(size=(120, 40)) as pilot:
            for _ in range(2):
                await press_button(app, pilot, "#next")
            assert app.step == 2
            assert app.query_one("#connect-github", Button).disabled
            assert not app.query(Input)  # No raw credentials, helpers or Work form.
            app.query_one("#approve-github", Checkbox).value = True
            await pilot.pause()
            await press_button(app, pilot, "#connect-github")
            assert ("connect", "github", "auto", True) in engine.calls
            assert bool(app.github) == (states["github"] == "AVAILABLE")
            await press_button(app, pilot, "#mode-manual")
            assert app.query_one("#connect-model", Button).disabled
            app.query_one("#approve-model", Checkbox).value = True
            await pilot.pause()
            await press_button(app, pilot, "#connect-model")
            assert ("connect", "model", "manual", True) in engine.calls
            await press_button(app, pilot, "#skip-github")
            assert app.github == {} and app.credentials["github"]["state"] == "SKIPPED"
            await press_button(app, pilot, "#next")
            assert not app.query_one("#approve", Checkbox).value
    asyncio.run(scenario())


def test_edited_plan_invalidates_consent_and_keyboard_advanced():
    async def scenario():
        app = SetupApp(FakeEngine(), locale="en", host_authorized=True)
        async with app.run_test(size=(80, 24)) as pilot:
            await to_review(app, pilot)
            app.query_one("#approve", Checkbox).value = True
            await pilot.pause()
            assert not app.query_one("#apply", Button).disabled
            await pilot.press("escape")
            await pilot.pause()
            assert app.step == 2
            await pilot.press("escape")
            await pilot.pause()
            app.query_one("#root-config", Input).value = "C:/Fixture/" + "long-directory/" * 12
            await press_button(app, pilot, "#next")
            await press_button(app, pilot, "#next")
            assert app.step == 3
            assert app.query_one("#apply", Button).disabled
            assert not app.query_one("#approve", Checkbox).value
            await pilot.press("tab", "down", "up")
            assert app.query_one("#controls").region.bottom <= 24
    asyncio.run(scenario())


def test_exception_and_metadata_are_sanitized_without_raw_repr():
    assert display({"token": "hidden"}) == "—"
    assert display(["PASS"]) == "—"
    assert display("ghp_not-real-fixture") == "[REDACTED]"
    assert "\x1b" not in display("\x1b[31m")
    async def scenario():
        app = SetupApp(FakeEngine(fail=True))
        async with app.run_test(size=(80, 24)) as pilot:
            await press_button(app, pilot, "#next")
            assert app.step == 0
            text = str(app.query_one("#status", Static).render())
            assert "OPERATION" in text and "SECRET_SHOULD_NEVER_APPEAR" not in text
    asyncio.run(scenario())


def test_runtime_edit_and_fingerprint_drift_cancel_apply():
    async def scenario():
        engine = FakeEngine()
        app = SetupApp(engine, host_authorized=True)
        async with app.run_test(size=(120, 40)) as pilot:
            await to_review(app, pilot)
            app.query_one("#approve", Checkbox).value = True
            await pilot.pause()
            app.query_one("#runtime-requested", Checkbox).value = False
            await pilot.pause(0.4)
            assert app.query_one("#apply", Button).disabled
            assert not app.query_one("#approve", Checkbox).value
            app.query_one("#approve", Checkbox).value = True
            await pilot.pause()
            app.plan_data["fingerprint"] = "changed-after-confirmation"
            await press_button(app, pilot, "#apply")
            assert app.step == 3
            assert not any(isinstance(c, tuple) and c[0] == "apply" for c in engine.calls)
    asyncio.run(scenario())


def test_preview_cannot_connect_and_normal_six_rows_fit_narrow_terminal():
    async def scenario():
        engine = FakeEngine(states={"github": "AVAILABLE", "model": "AVAILABLE"})
        app = SetupApp(engine)
        async with app.run_test(size=(80, 24)) as pilot:
            await press_button(app, pilot, "#next")
            assert app.step == 1
            svg = app.export_screenshot()
            assert "HOST_AGENT.md" in svg and "Exchange" in svg
            assert "{'" not in svg
            await press_button(app, pilot, "#next")
            app.query_one("#approve-github", Checkbox).value = True
            await pilot.pause()
            assert app.query_one("#connect-github", Button).disabled
            assert not any(isinstance(c, tuple) and c[0] == "connect" for c in engine.calls)
    asyncio.run(scenario())


def test_unknown_existing_config_shows_visible_actionable_blocker():
    class UnknownRootEngine(FakeEngine):
        def plan(self, probe, **kwargs):
            result = super().plan(probe, **kwargs)
            result["status"] = "BLOCKED"
            result["roots"]["config"]["owner"] = "UNKNOWN"
            result["gates"] = [{"code": "ROOT_CONFIG", "state": "BLOCKED", "reason": "raw provider diagnostic should not be rendered"}]
            return result

    async def scenario():
        app = SetupApp(UnknownRootEngine(), host_authorized=True)
        async with app.run_test(size=(80, 24)) as pilot:
            await press_button(app, pilot, "#next")
            status = str(app.query_one("#status", Static).render())
            assert "ROOT_CONFIG" in status and "改用新的目录" in status
            assert "raw provider" not in status
            assert app.query_one("#status").region.bottom <= 24
            svg = app.export_screenshot()
            assert "ROOT_CONFIG" in svg
            await press_button(app, pilot, "#next")
            await press_button(app, pilot, "#next")
            assert "ROOT_CONFIG" in str(app.query_one("#status", Static).render())
            app.query_one("#approve", Checkbox).value = True
            await pilot.pause()
            assert app.query_one("#apply", Button).disabled
    asyncio.run(scenario())


def test_shipping_login_actions_are_localized_in_both_modes():
    app = SetupApp(FakeEngine())
    app.credentials = {"github": {"state": "REUSE_NOT_SUPPORTED", "next_action": "HOST_GITHUB_DEVICE_LOGIN", "manual_next_action": "raw owner technical instructions"}, "model": {"state": "NEEDS_CONNECTION", "next_action": "HOST_PROVIDER_LOGIN"}}
    for mode in ("auto", "manual"):
        app.mode = mode
        assert "github.com/login/device" in app.account_summary("github")
        assert "电脑所有者" in app.account_summary("github")
        assert "官方登录" in app.account_summary("model")
        assert "HOST_PROVIDER_LOGIN" not in app.account_summary("model")
        assert "raw owner" not in app.account_summary("github")
