"""Manual intent must change both the model and visible mode, before planning."""
import asyncio
import copy
from pathlib import Path
import pytest
from textual.widgets import Button, Input, Label
from agent_setup.tui import SetupApp
from test_folder_picker_tui_143 import isolated_machine, placement
from test_tui import press_button


@pytest.mark.parametrize('selection',['cancel','same','other'])
def test_parent_picker_switches_visible_mode_only_on_selection(tmp_path,selection):
    async def scenario():
        engine,fast,slow=isolated_machine(tmp_path)
        app=SetupApp(engine,folder_picker=lambda **kwargs:None if selection=='cancel' else str(fast if selection=='same' else slow))
        app.overrides['isolated_scope']=engine.propose_isolated_roots(engine.probe())['isolated_scope']
        async with app.run_test(size=(120,40)) as pilot:
            await placement(app,pilot)
            assert app.placement_mode=='auto'
            before=copy.deepcopy((app.overrides,app.plan_data))
            await press_button(app,pilot,'#browse-isolated-parent')
            custom=selection!='cancel'
            assert app.placement_mode==('custom' if custom else 'auto')
            assert app.query_one('#placement-custom',Button).variant==('primary' if custom else 'default')
            assert app.query_one('#placement-auto',Button).variant==('default' if custom else 'primary')
            if custom:assert '默认名称' in str(app.query_one('#root-label-workspace',Label).render())
            if not custom:assert before==(app.overrides,app.plan_data)
            assert not Path(app.overrides['isolated_scope']).exists()
    asyncio.run(scenario())


@pytest.mark.parametrize('field,value',[('isolated-parent','absent-parent'),('root-workspace','MyWork')])
def test_keyboard_edit_switches_visible_mode_before_validation(tmp_path,field,value):
    async def scenario():
        engine,fast,slow=isolated_machine(tmp_path)
        app=SetupApp(engine)
        app.overrides['isolated_scope']=engine.propose_isolated_roots(engine.probe())['isolated_scope']
        async with app.run_test(size=(120,40)) as pilot:
            await placement(app,pilot)
            before=copy.deepcopy(app.plan_data)
            app.query_one('#'+field,Input).focus()
            if field=='isolated-parent':
                await pilot.press('ctrl+a','backspace')
            await pilot.press(*value)
            await pilot.pause()
            assert app.placement_mode=='custom' and app.placement_dirty
            assert app.query_one('#placement-custom',Button).variant=='primary'
            assert app.query_one('#placement-auto',Button).variant=='default'
            assert app.plan_data==before
            assert app.focused.id==field and app.approved_fingerprint is None
            assert not Path(app.overrides['isolated_scope']).exists()
    asyncio.run(scenario())
