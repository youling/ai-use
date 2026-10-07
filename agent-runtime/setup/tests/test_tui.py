"""Headless screen tests: fake engine only; no Host or credential mutation."""
import asyncio

from textual.widgets import Button, Checkbox, Input, Static

from agent_setup.tui import SetupApp


class FakeEngine:
    def __init__(self, *, blocked=False, fail=False):
        self.calls = []
        self.blocked = blocked
        self.fail = fail

    def probe(self):
        self.calls.append("probe")
        if self.fail:
            raise RuntimeError("SECRET_SHOULD_NEVER_APPEAR")
        return {"status": "READY", "reason": "Synthetic Windows fixture"}

    def plan(self, probe, **kwargs):
        self.calls.append(("plan", kwargs))
        return {"status": "BLOCKED" if self.blocked else "READY", "host_authorized": kwargs["overrides"].get("host_authorized", False), "roots": {"workspace": {"path": kwargs["overrides"].get("workspace", "C:/Fixture/work"), "reason": "NO_MOVE"}}, "gates": [{"code": "WSLC", "state": "PASS", "reason": "Fixture only"}]}

    def apply(self, plan, approved=False):
        self.calls.append(("apply", approved))
        return {"status": "APPLIED", "reason": "Fixture only"}

    def verify(self, plan):
        self.calls.append("verify")
        return {"status": "READY", "checks": ["fixture"]}

    def repair(self, plan):
        self.calls.append("repair")
        return {"status": "BLOCKED", "reason": "Explicit repair approval required"}


async def to_review(app, pilot):
    for _ in range(5):
        await pilot.click("#next")
        await pilot.pause(0.25)
    assert app.step == 5


def test_full_keyboard_review_apply_and_results():
    async def scenario():
        engine = FakeEngine()
        app = SetupApp(engine, host_authorized=True)
        async with app.run_test(size=(100, 42)) as pilot:
            assert app.step == 0
            await pilot.press("enter")
            await pilot.pause(0.25)
            assert app.step == 1
            await pilot.click("#next")
            await pilot.pause(0.25)
            assert app.step == 2
            app.query_one("#root-workspace", Input).value = "D:/Fixture/work"
            await pilot.click("#next")
            await pilot.pause(0.25)
            assert app.step == 3
            app.query_one("#github-reference", Input).value = "fixture.github"
            app.query_one("#durable-repository", Input).value = "fixture/recovery"
            await pilot.click("#next")
            await pilot.pause(0.25)
            assert app.step == 4
            await pilot.click("#free-route")
            await pilot.click("#next")
            await pilot.pause(0.25)
            assert app.step == 5
            assert app.query_one("#apply", Button).disabled
            assert not any(isinstance(call, tuple) and call[0] == "apply" for call in engine.calls)
            await pilot.click("#approve")
            await pilot.pause(0.25)
            assert not app.query_one("#apply", Button).disabled
            await pilot.click("#apply")
            await pilot.pause(0.25)
            assert app.step == 6
            assert ("apply", True) in engine.calls
            await pilot.click("#verify")
            await pilot.pause(0.25)
            assert app.result["status"] == "READY"
            await pilot.click("#repair")
            await pilot.pause(0.25)
            assert app.result["status"] == "BLOCKED"
            plans = [call[1] for call in engine.calls if isinstance(call, tuple) and call[0] == "plan"]
            assert plans[-1]["overrides"]["workspace"] == "D:/Fixture/work"
            assert plans[-1]["github"]["ref"] == "fixture.github"
            assert plans[-1]["github"]["authorized"] is False
            assert plans[-1]["github"]["helper_approved"] is False
            assert plans[-1]["github"]["recovery_requested"] is False
            assert plans[-1]["model"]["free_route"] is True
            assert plans[-1]["durable"]["destination"] == "fixture/recovery"
            assert plans[-1]["durable"]["authorized"] is False
            assert plans[-1]["overrides"].get("runtime", False) is False
    asyncio.run(scenario())


def test_no_host_authority_or_blocked_plan_cannot_apply():
    async def scenario():
        for authority, blocked in ((False, False), (True, True)):
            engine = FakeEngine(blocked=blocked)
            app = SetupApp(engine, host_authorized=authority)
            async with app.run_test(size=(100, 42)) as pilot:
                await to_review(app, pilot)
                await pilot.click("#approve")
                await pilot.pause(0.25)
                assert app.query_one("#apply", Button).disabled
                await pilot.click("#apply")
                assert not any(isinstance(call, tuple) and call[0] == "apply" for call in engine.calls)
                # Review may continue to non-mutating verify even when apply is gated.
                await pilot.click("#next")
                await pilot.pause(0.25)
                assert app.step == 6
    asyncio.run(scenario())


def test_escape_retains_edits_and_tab_arrows_navigate():
    async def scenario():
        app = SetupApp(FakeEngine(), locale="en")
        async with app.run_test(size=(100, 42)) as pilot:
            await pilot.press("enter")
            await pilot.pause(0.25)
            await pilot.click("#next")
            await pilot.pause(0.25)
            app.query_one("#root-config", Input).value = "C:/Fixture/config"
            await pilot.press("escape")
            await pilot.pause(0.25)
            assert app.step == 1
            await pilot.click("#next")
            await pilot.pause(0.25)
            assert app.query_one("#root-config", Input).value == "C:/Fixture/config"
            focus = app.focused
            await pilot.press("tab")
            assert app.focused is not focus
            await pilot.press("down", "up")
            assert "Placement" in str(app.query_one("#heading", Static).render())
    asyncio.run(scenario())


def test_exception_is_sanitized_and_does_not_advance():
    async def scenario():
        app = SetupApp(FakeEngine(fail=True))
        async with app.run_test(size=(100, 42)) as pilot:
            await pilot.press("enter")
            await pilot.pause(0.25)
            assert app.step == 0
            status = str(app.query_one("#status", Static).render())
            assert "OPERATION" in status
            assert "SECRET_SHOULD_NEVER_APPEAR" not in status
    asyncio.run(scenario())


def test_changed_plan_requires_fresh_review_confirmation():
    async def scenario():
        engine = FakeEngine()
        app = SetupApp(engine, host_authorized=True)
        async with app.run_test(size=(100, 42)) as pilot:
            await to_review(app, pilot)
            await pilot.click("#approve")
            await pilot.pause(0.25)
            assert not app.query_one("#apply", Button).disabled
            await pilot.press("escape")
            await pilot.pause(0.25)
            assert app.step == 4
            app.query_one("#model-reference", Input).value = "fixture.new-model"
            await pilot.click("#next")
            await pilot.pause(0.25)
            assert app.step == 5
            assert not app.query_one("#approve", Checkbox).value
            assert app.query_one("#apply", Button).disabled
            assert not any(isinstance(call, tuple) and call[0] == "apply" for call in engine.calls)
    asyncio.run(scenario())


def test_explicit_identity_and_runtime_declarations_reach_engine():
    async def scenario():
        engine = FakeEngine()
        app = SetupApp(engine, host_authorized=True)
        async with app.run_test(size=(100, 50)) as pilot:
            for _ in range(3):
                await pilot.click("#next")
                await pilot.pause(0.25)
            assert app.step == 3
            app.query_one("#github-reference", Input).value = "fixture.github"
            app.query_one("#github-helper", Input).value = "C:/Fixture/helper.py"
            app.query_one("#github-work", Input).value = "fixture/recovery#127"
            app.query_one("#durable-repository", Input).value = "fixture/recovery"
            for selector in ("#github-helper-approved", "#github-authorized", "#durable-authorized", "#recovery-requested"):
                app.query_one(selector, Checkbox).focus()
                await pilot.press("space")
                await pilot.pause(0.25)
            await pilot.click("#next")
            await pilot.pause(0.25)
            await pilot.click("#next")
            await pilot.pause(0.25)
            assert app.step == 5
            await pilot.click("#approve")
            await pilot.pause(0.25)
            assert not app.query_one("#apply", Button).disabled
            await pilot.click("#runtime-requested")
            await pilot.pause(0.25)
            assert not app.query_one("#approve", Checkbox).value
            assert app.query_one("#apply", Button).disabled
            plans = [call[1] for call in engine.calls if isinstance(call, tuple) and call[0] == "plan"]
            assert plans[-1]["overrides"]["runtime"] is True
            assert plans[-1]["github"] == {"ref": "fixture.github", "helper": "C:/Fixture/helper.py", "work": "fixture/recovery#127", "helper_approved": True, "authorized": True, "recovery_requested": True}
            assert plans[-1]["durable"]["authorized"] is True
            assert not any(isinstance(call, tuple) and call[0] == "apply" for call in engine.calls)
    asyncio.run(scenario())
