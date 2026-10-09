"""Public annotated/bare canonical V1 replay on real native inventory."""
import os
import re
import yaml
import pytest
from agent_setup.read_only_acceptance import owned_fixture_pipeline, assert_fixture_unchanged

pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Actual Windows owned-context pipeline')


@pytest.mark.parametrize('annotated', [False, True])
def test_owned_legacy_exchange_shape_roundtrip_keeps_classification_separate(tmp_path, annotated):
    fixture = owned_fixture_pipeline(tmp_path, 'legacy_v1', annotated_exchange=annotated)
    plan = fixture['engine'].plan(fixture['observation'])
    assert set(plan['exchange']) == {'in', 'out'}
    expected = {'owner': 'HOST_MANAGED', 'relocatable': False,
                'reason': 'PUBLIC_SYNTHETIC_EXCHANGE_CLASSIFICATION'} if annotated else {}
    assert plan.get('exchange_classification') == expected
    markdown = fixture['engine'].context(plan)
    context = yaml.safe_load(re.search(r'```yaml\s*\n(.*?)\n```', markdown, re.S).group(1))
    assert context['paths']['exchange'] == {**expected, **plan['exchange']}
    assert not fixture['adapter'].can_apply and not fixture['adapter'].apply_authorized
    assert plan['status'] == 'BLOCKED'  # Declared owner metadata does not prove ownership.
    assert_fixture_unchanged(fixture)
