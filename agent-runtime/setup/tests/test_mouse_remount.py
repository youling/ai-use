"""Real compositor hit map during widget detachment, through App.on_event."""
import asyncio
from textual import events
from textual.widgets import Static
from agent_setup.tui import SetupApp
from test_tui import FakeEngine


def test_native_mouse_down_during_remount_does_not_select_detached_widget():
    async def scenario():
        app=SetupApp(FakeEngine())
        async with app.run_test(size=(120,40)) as pilot:
            await pilot.pause()
            old=app.query_one('#checks',Static)
            point=old.region.offset
            assert app.screen.get_widget_and_offset_at(point.x+2,point.y)[0] is old
            with app.batch_update():
                await old.remove()
                assert old.parent is None
                await app.on_event(events.MouseDown(None,point.x+2,point.y,0,0,1,False,False,False))
                await app.on_event(events.MouseMove(None,point.x+3,point.y,1,0,1,False,False,False))
                await app.on_event(events.MouseUp(None,point.x+3,point.y,0,0,1,False,False,False))
            await pilot.pause()
            assert app.step==0 and not app.result
    asyncio.run(scenario())


def test_attached_text_still_selects_and_mouse_navigation_still_works():
    async def scenario():
        app=SetupApp(FakeEngine())
        async with app.run_test(size=(120,40)) as pilot:
            await pilot.pause()
            widget=app.query_one('#checks',Static)
            point=widget.region.offset
            assert app.screen.get_widget_and_offset_at(point.x+2,point.y)[0] is widget
            await app.on_event(events.MouseDown(None,point.x+2,point.y,0,0,1,False,False,False))
            assert app.screen._select_state is not None
            await app.on_event(events.MouseMove(None,point.x+4,point.y,2,0,1,False,False,False))
            await app.on_event(events.MouseUp(None,point.x+4,point.y,0,0,1,False,False,False))
            await pilot.click('#next')
            await pilot.pause()
            assert app.step==1
    asyncio.run(scenario())
