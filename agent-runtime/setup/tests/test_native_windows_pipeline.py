"""Real Windows scanner/parser on owned fixtures; WSLC alone is simulated."""
import asyncio
import os
import pytest
from textual.widgets import Button
from agent_setup.engine import SetupError
from agent_setup.read_only_acceptance import SCENARIOS, owned_fixture_pipeline, assert_fixture_unchanged, native_read_only_planning
from agent_setup.tui import SetupApp

pytestmark=pytest.mark.skipif(os.name!='nt',reason='Actual Windows PS5/WinAPI metadata pipeline')


@pytest.mark.parametrize('scenario',SCENARIOS)
def test_native_adapter_engine_parser_cases(tmp_path,scenario):
    data=owned_fixture_pipeline(tmp_path,scenario)
    assert data['native_calls']==['PYTHON_SIGNATURE','OS_INVENTORY']
    assert data['observation']['volumes']
    assert data['observation']['python_verified'] is True
    assert data['adapter'].can_apply is False
    if data['expected_code']:
        with pytest.raises(SetupError,match=data['expected_code']):
            data['engine'].plan(data['observation'],overrides=data['overrides'])
        if scenario=='stale':
            assert data['observation']['existing_root_metadata_errors']==[{'role':'context','reason':'VERSION_UNSUPPORTED'}]
        if scenario=='junction':
            assert data['observation']['existing_root_metadata_errors']==[{'role':'config','reason':'UNSAFE_PATH'}]
    else:
        plan=data['engine'].plan(data['observation'],overrides=data['overrides'])
        assert plan['status']==data['expected_status']
        if scenario=='legacy_v1':
            assert plan['roots']['state']['path']==str(tmp_path/'state')
            assert plan['exchange']=={'in':str(tmp_path/'exchange-in'),'out':str(tmp_path/'exchange-out')}
    assert_fixture_unchanged(data)


@pytest.mark.parametrize('scenario',['fresh','legacy_v1'])
def test_native_production_pipeline_first_next(tmp_path,scenario):
    data=owned_fixture_pipeline(tmp_path,scenario)
    async def run():
        app=SetupApp(data['engine'])
        app.overrides.update(data['overrides'])
        async with app.run_test(size=(80,24)) as pilot:
            app.query_one('#next',Button).focus()
            await pilot.press('enter');await pilot.pause(.6)
            assert app.step==1
            assert not app.host_authorized
            assert app.approved_fingerprint is None
    asyncio.run(run())
    assert_fixture_unchanged(data)


def test_native_honest_runtime_gates_and_no_host_effects(tmp_path):
    result=native_read_only_planning(tmp_path)
    assert result['status']=='PASS'
    assert result['volume_metadata']=='PASS'
    assert result['meaning']=='READ_ONLY_PLAN_COMPUTED_NOT_RUNTIME_READY'
    assert result['evidence']['wslc_capability']=='NATIVE_OBSERVED'
