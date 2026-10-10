"""Actual Textual events; only the modal OS picker boundary is replaced."""
import asyncio
import copy
from pathlib import Path
import threading
import pytest

from textual.widgets import Button, Collapsible, Input, Static
from agent_setup.engine import SetupEngine, FixtureAdapter
from agent_setup.tui import SetupApp
from test_tui import FakeEngine, press_button


async def placement(app, pilot):
    await press_button(app, pilot, '#next')
    app.query_one('#advanced', Collapsible).collapsed = False
    await pilot.pause()


def test_browse_is_separate_keyboard_action_and_reprobes():
    async def scenario():
        calls = []
        ui_thread = threading.get_ident()
        def picker(**kwargs):
            calls.append((kwargs, threading.get_ident()))
            return 'Z:/PublicFixture/custom-workspace'
        engine = FakeEngine()
        app = SetupApp(engine, folder_picker=picker)
        async with app.run_test(size=(80, 24)) as pilot:
            await placement(app, pilot)
            app.query_one('#root-workspace', Input).focus()
            await pilot.pause()
            assert calls == []  # Input focus never masquerades as Browse.
            before = engine.calls.count('probe')
            app.approved_fingerprint = 'old-consent'
            await press_button(app, pilot, '#browse-workspace')
            assert len(calls) == 1 and calls[0][1] != ui_thread
            assert app.overrides['workspace'] == 'Z:/PublicFixture/custom-workspace'
            assert engine.calls.count('probe') == before + 1
            assert app.approved_fingerprint is None and not app.host_authorized
            assert app.focused.id == 'root-workspace'
            assert not app.query_one('#advanced', Collapsible).collapsed
            assert not any(isinstance(c, tuple) and c[0] == 'apply' for c in engine.calls)
    asyncio.run(scenario())


def test_cancel_keeps_fields_plan_confirmation_and_focus():
    async def scenario():
        engine = FakeEngine()
        app = SetupApp(engine, folder_picker=lambda **kwargs: None)
        async with app.run_test(size=(120, 40)) as pilot:
            await placement(app, pilot)
            app.approved_fingerprint = 'existing-consent'
            before = copy.deepcopy((app.overrides, app.plan_data, engine.calls))
            await press_button(app, pilot, '#browse-config')
            assert (app.overrides, app.plan_data, engine.calls) == before
            assert app.approved_fingerprint == 'existing-consent'
            assert app.query_one('#root-config', Input).value == ''
            assert app.focused.id == 'browse-config'
    asyncio.run(scenario())


def test_native_error_never_displays_upstream_text():
    async def scenario():
        def picker(**kwargs):
            raise OSError('PRIVATE_PATH_AND_SECRET_MUST_NOT_APPEAR')
        app = SetupApp(FakeEngine(), folder_picker=picker)
        async with app.run_test(size=(80, 24)) as pilot:
            await placement(app, pilot)
            before = copy.deepcopy(app.plan_data)
            await press_button(app, pilot, '#browse-cache')
            status = str(app.query_one('#status', Static).render())
            assert 'FOLDER_PICKER_FAILED' in status and 'PRIVATE_PATH' not in status
            assert app.plan_data == before and app.focused.id == 'browse-cache'
    asyncio.run(scenario())


def test_recommendation_is_preview_auto_clears_custom_values():
    async def scenario():
        engine = FakeEngine()
        app = SetupApp(engine)
        async with app.run_test(size=(80, 24)) as pilot:
            await placement(app, pilot)
            assert app.query_one('#root-config', Input).value == ''
            assert app.query_one('#root-config', Input).placeholder
            assert '仅为预览' in str(app.query_one('#placement-help', Static).render())
            await press_button(app, pilot, '#placement-custom')
            app.query_one('#root-config', Input).value = 'Z:/PublicFixture/typed-config'
            await press_button(app, pilot, '#recompute')
            assert app.overrides['config'] == 'Z:/PublicFixture/typed-config'
            app.approved_fingerprint = 'old-consent'
            await press_button(app, pilot, '#placement-auto')
            assert 'config' not in app.overrides and app.placement_mode == 'auto'
            assert app.approved_fingerprint is None
            assert app.query_one('#root-config', Input).value == ''
    asyncio.run(scenario())


def isolated_machine(tmp_path):
    docs = tmp_path / 'documents'; docs.mkdir()
    fast, slow = tmp_path / 'fast', tmp_path / 'other-disk'
    fast.mkdir(); slow.mkdir()
    data = {'platform':'windows', 'python_version':'3.14.8', 'python_verified':True,
            'wsl_app_version':'3.0.1', 'wslc_capability':{'state':'PASS'}, 'documents':str(docs),
            'existing_roots':{}, 'active_workloads':[], 'volumes':[
                {'mount':str(path), 'fs':'NTFS', 'device_id':name, 'bus_type':'NVMe' if name=='fast' else 'SATA',
                 'media_type':'SSD', 'capacity_bytes':256*2**30, 'free_bytes':64*2**30}
                for path,name in ((fast,'fast'),(slow,'other'))]}
    engine = SetupEngine(FixtureAdapter(data, tmp_path))
    return engine, fast, slow


def test_scoped_ui_rejects_absolute_child_input_without_impossible_picker(tmp_path):
    async def scenario():
        engine, fast, slow = isolated_machine(tmp_path)
        scope = engine.propose_isolated_roots(engine.probe())['isolated_scope']
        app = SetupApp(engine, folder_picker=lambda **kwargs: str(slow))
        app.overrides['isolated_scope'] = scope
        async with app.run_test(size=(120, 40)) as pilot:
            await placement(app, pilot)
            app.approved_fingerprint = 'old-consent'
            assert not list(app.query('#browse-workspace'))
            app.query_one('#root-workspace', Input).value = str(slow)
            await pilot.pause()
            assert '待重新核验' in str(app.query_one('#root-label-workspace').render())
            await press_button(app, pilot, '#recompute')
            status = str(app.query_one('#status', Static).render())
            assert '新子目录名称' in status and '安装父目录' in status
            assert app.approved_fingerprint is None
            assert app.overrides['isolated_scope'] == scope and not Path(scope).exists()
            await press_button(app, pilot, '#next')
            assert app.step == 1
    asyncio.run(scenario())


def test_scoped_custom_names_and_typed_parent_succeed_through_review(tmp_path):
    async def scenario():
        engine, fast, slow = isolated_machine(tmp_path)
        scope = engine.propose_isolated_roots(engine.probe())['isolated_scope']
        app = SetupApp(engine)
        app.overrides['isolated_scope'] = scope
        async with app.run_test(size=(120, 40)) as pilot:
            await placement(app, pilot)
            old_binding = app.plan_data['install_binding']
            await press_button(app, pilot, '#placement-custom')
            names = dict(zip(('workspace','config','cache','temp'), ('工作区','配置','缓存','临时文件')))
            app.query_one('#isolated-parent', Input).value = str(slow)
            await pilot.pause()
            await press_button(app, pilot, '#placement-custom')
            assert app.query_one('#isolated-parent', Input).value == str(slow)
            for role, name in names.items():
                app.query_one('#root-' + role, Input).value = name
            await pilot.pause()
            assert app.placement_dirty and '尚未采用' in str(app.query_one('#placement-state', Static).render())
            await press_button(app, pilot, '#recompute')
            chosen = Path(app.overrides['isolated_scope'])
            assert chosen.parent == slow and not chosen.exists()
            assert not app.placement_dirty and app.plan_data['status'] == 'READY'
            assert app.plan_data['install_binding'] != old_binding
            for role, name in names.items():
                assert Path(app.plan_data['roots'][role]['path']) == chosen / name
                assert app.query_one('#root-' + role, Input).value == name
            assert all(Path(path).is_relative_to(chosen) for path in app.plan_data['exchange'].values())
            await press_button(app, pilot, '#next')
            await press_button(app, pilot, '#skip-github')
            await press_button(app, pilot, '#skip-model')
            await press_button(app, pilot, '#next')
            assert app.step == 3 and not app.host_authorized and app.approved_fingerprint is None
            assert not chosen.exists()
    asyncio.run(scenario())


def test_scoped_parent_picker_preserves_custom_names_and_cancel(tmp_path):
    async def scenario():
        engine, fast, slow = isolated_machine(tmp_path)
        scope = engine.propose_isolated_roots(engine.probe())['isolated_scope']
        answers = iter([None, str(slow)])
        app = SetupApp(engine, folder_picker=lambda **kwargs: next(answers))
        app.overrides['isolated_scope'] = scope
        async with app.run_test(size=(120, 40)) as pilot:
            await placement(app, pilot)
            app.query_one('#root-cache', Input).value = '我的缓存'
            await pilot.pause()
            before = copy.deepcopy((app.overrides, app.plan_data))
            await press_button(app, pilot, '#browse-isolated-parent')
            assert before == (app.overrides, app.plan_data)
            assert app.query_one('#root-cache', Input).value == '我的缓存'
            await press_button(app, pilot, '#browse-isolated-parent')
            chosen = Path(app.overrides['isolated_scope'])
            assert chosen.parent == slow and Path(app.plan_data['roots']['cache']['path']) == chosen / '我的缓存'
            assert not chosen.exists() and app.focused.id == 'browse-isolated-parent'
    asyncio.run(scenario())


def test_cross_disk_parent_reselection_regenerates_all_roots(tmp_path):
    async def scenario():
        engine, fast, slow = isolated_machine(tmp_path)
        scope = engine.propose_isolated_roots(engine.probe())['isolated_scope']
        app = SetupApp(engine, folder_picker=lambda **kwargs: str(slow))
        app.overrides['isolated_scope'] = scope
        async with app.run_test(size=(120, 40)) as pilot:
            await placement(app, pilot)
            old_binding = app.plan_data['install_binding']
            app.overrides['cache'] = str(Path(scope) / 'custom-cache')
            app.approved_fingerprint = 'old-consent'
            await press_button(app, pilot, '#browse-isolated-parent')
            chosen = Path(app.overrides['isolated_scope'])
            assert chosen.parent == slow and not chosen.exists() and not Path(scope).exists()
            assert all(role not in app.overrides for role in ('workspace','config','cache','temp'))
            assert all(Path(root['path']).is_relative_to(chosen) for role,root in app.plan_data['roots'].items() if role in ('workspace','config','cache','temp'))
            assert all(Path(path).is_relative_to(chosen) for path in app.plan_data['exchange'].values())
            assert app.plan_data['storage']['device_id'] == 'other'
            assert app.plan_data['install_binding'] != old_binding and app.approved_fingerprint is None
            assert app.focused.id == 'browse-isolated-parent' and not app.host_authorized
            assert not app.busy and app.words['busy'] not in app.status_text
    asyncio.run(scenario())


@pytest.mark.parametrize('name', ['..', '../outside', 'other/child', 'C:\\outside', 'cache:stream', 'CON', 'bad.'])
def test_scoped_invalid_names_keep_valid_plan_and_cannot_advance(tmp_path, name):
    async def scenario():
        engine, fast, slow = isolated_machine(tmp_path)
        scope = engine.propose_isolated_roots(engine.probe())['isolated_scope']
        app = SetupApp(engine)
        app.overrides['isolated_scope'] = scope
        async with app.run_test(size=(80, 24)) as pilot:
            await placement(app, pilot)
            before = copy.deepcopy(app.plan_data)
            app.approved_fingerprint = 'old-consent'
            app.query_one('#root-cache', Input).value = name
            await pilot.pause()
            await press_button(app, pilot, '#next')
            assert app.step == 1 and app.plan_data == before
            assert app.approved_fingerprint is None and '输入尚未采用' in app.status_text
            assert app.query_one('#root-cache', Input).value == name and not Path(scope).exists()
    asyncio.run(scenario())


def test_scoped_duplicate_names_are_rejected_by_original_engine(tmp_path):
    async def scenario():
        engine, fast, slow = isolated_machine(tmp_path)
        scope = engine.propose_isolated_roots(engine.probe())['isolated_scope']
        app = SetupApp(engine)
        app.overrides['isolated_scope'] = scope
        async with app.run_test(size=(120, 40)) as pilot:
            await placement(app, pilot)
            before = copy.deepcopy(app.plan_data)
            app.query_one('#root-cache', Input).value = 'same'
            app.query_one('#root-config', Input).value = 'same'
            await pilot.pause()
            await press_button(app, pilot, '#next')
            assert app.step == 1 and app.plan_data == before and 'ROOT_OVERLAP' in app.status_text
            assert app.placement_dirty and not Path(scope).exists()
    asyncio.run(scenario())
