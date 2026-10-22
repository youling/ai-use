"""One primary action; successful Apply precedes installation results."""
import asyncio
import threading
from textual.widgets import Button, Checkbox, Static
from agent_setup.engine import SetupError
from agent_setup.tui import SetupApp
from test_tui import FakeEngine, to_review, press_button


def test_failed_install_stays_on_review_and_requires_fresh_consent():
    class Failed(FakeEngine):
        def apply(self, plan, approved=False):
            self.calls.append(('apply',approved))
            raise SetupError('PUBLIC_SYNTHETIC_FAILURE')
    async def scenario():
        engine=Failed();app=SetupApp(engine,host_authorized=True)
        async with app.run_test(size=(80,24)) as pilot:
            await to_review(app,pilot)
            assert not app.query('#apply')
            assert str(app.query_one('#next',Button).label)=='安装'
            await app.advance()
            assert app.step==3 and not any(isinstance(c,tuple) and c[0]=='apply' for c in engine.calls)
            app.query_one('#approve',Checkbox).value=True
            await pilot.pause()
            await press_button(app,pilot,'#next')
            assert app.step==3 and not app.result and not app.query('#results')
            assert app.query_one('#next',Button).disabled
            assert not app.query_one('#approve',Checkbox).value
            assert 'PUBLIC_SYNTHETIC_FAILURE' in str(app.query_one('#status',Static).render())
    asyncio.run(scenario())


def test_in_progress_install_cannot_skip_to_results_or_apply_twice():
    started=threading.Event();release=threading.Event()
    class Slow(FakeEngine):
        def apply(self, plan, approved=False):
            started.set()
            assert release.wait(10)
            return super().apply(plan,approved=approved)
    async def scenario():
        engine=Slow();app=SetupApp(engine,host_authorized=True)
        async with app.run_test(size=(80,24)) as pilot:
            await to_review(app,pilot)
            app.query_one('#approve',Checkbox).value=True
            await pilot.pause()
            task=asyncio.create_task(app.advance())
            try:
                assert await asyncio.to_thread(started.wait,3)
                assert app.busy and app.step==3 and not app.query('#results')
                assert app.query_one('#next',Button).disabled
                await app.advance()
                assert app.step==3
            finally:
                release.set()
                await task
            assert app.step==4 and app.result['status']=='APPLIED'
            assert len([c for c in engine.calls if isinstance(c,tuple) and c[0]=='apply'])==1
            assert str(app.query_one('#next',Button).label)=='完成'
    asyncio.run(scenario())
