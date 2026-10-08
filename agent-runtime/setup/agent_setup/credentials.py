"""Credential metadata seam, never a credential store or token transport.

A custodian is explicitly registered by the Host owner, not discovered by PATH
or an auth.json file. The shipping adapter has no cross-provider custodian.
"""
from datetime import datetime, timezone, timedelta
import re
import json
from .engine import SECRET_PATTERN

KINDS = ('github', 'model')

def unavailable(kind, *, installed=False):
    return {'state': 'REUSE_NOT_SUPPORTED' if installed else 'NEEDS_CONNECTION',
            'account': '', 'provider': 'GitHub' if kind == 'github' else '',
            'reusable': False, 'reason_code': 'HOST_CUSTODIAN_CONNECTION_REQUIRED',
            'next_action': 'HOST_GITHUB_DEVICE_LOGIN' if kind == 'github' else 'HOST_PROVIDER_LOGIN',
            'manual_next_action': 'Use the trusted GitHub device sign-in on the Host (github.com/login/device); then ask the Host custodian for scoped runtime projection. Do not paste tokens here.' if kind == 'github' else 'Choose your provider and use its official Host sign-in or protected credential input. Existing application login is not runtime authorization.',
            'scope': 'No runtime permission requested until an owner-bound account and repository/provider scope is available.'}

def validated_metadata(kind, raw):
    """Require fresh, scoped owner attestations; an account name is not proof."""
    result = unavailable(kind)
    if not isinstance(raw, dict):
        return result
    try:
        if SECRET_PATTERN.search(json.dumps(raw)):
            return {**result, 'reason_code': 'SENSITIVE_METADATA_REJECTED'}
    except (ValueError, TypeError):
        return result
    for key in ('account', 'provider'):
        value = raw.get(key, '')
        if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.@ -]{0,100}', value) and not re.search(r'(?i)gh[pousr]_|sk-|token|password', value):
            result[key] = value
    try:
        expiry = datetime.fromisoformat(raw.get('expires_at', '').replace('Z', '+00:00'))
        current = expiry.tzinfo is not None and expiry > datetime.now(timezone.utc) + timedelta(seconds=30)
    except (ValueError, TypeError, AttributeError):
        current = False
    proven = (current and raw.get('owner_approved') is True and raw.get('authenticated') is True
              and raw.get('revoked') is False and raw.get('bounded_projection') is True)
    if kind == 'github':
        repo, work = raw.get('repo', ''), raw.get('work', '')
        proven = (proven and isinstance(repo, str) and bool(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo))
                  and isinstance(work, str) and bool(re.fullmatch(re.escape(repo) + r'#[1-9][0-9]*', work))
                  and raw.get('permissions') == {'contents': 'write', 'issues': 'write'}
                  and raw.get('repository_scope') == [repo])
    else:
        proven = proven and raw.get('provider_verified') is True and raw.get('model_verified') is True
    if proven:
        result['scope'] = ('Repository: ' + raw['repo'] + '; contents and issues write; short-lived projection' if kind == 'github' else 'Provider: ' + result['provider'] + '; selected model only; short-lived projection')
        result.update(state='AVAILABLE', reusable=True, reason_code='FRESH_OWNER_ATTESTATION', next_action='REVIEW_SCOPED_CONNECTION')
    return result
