"""Per-operation file projection reader. Only Git protocol pipe emits token."""
import datetime as dt
import json
import os
from pathlib import Path
import sys

def current(path=None):
    path=Path(path or os.environ.get('GITHUB_CREDENTIAL_FILE','/run/secrets/github/credential.json'))
    value=json.loads(path.read_text(encoding='utf-8'))
    expiry=dt.datetime.fromisoformat(value['expires_at'].replace('Z','+00:00'))
    if expiry.tzinfo is None or expiry<=dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=30):
        raise ValueError('CREDENTIAL_NOT_READY')
    if not isinstance(value.get('token'),str) or not value['token'] or any(c in value['token'] for c in '\r\n\x00'):
        raise ValueError('CREDENTIAL_INVALID')
    if value['work']!=os.environ['GITHUB_WORK'] or value['repo']!=os.environ['GITHUB_REPOSITORY']:
        raise ValueError('CREDENTIAL_SCOPE_MISMATCH')
    if value.get('permissions')!={'contents':'write','issues':'write'}:
        raise ValueError('CREDENTIAL_PERMISSION_MISMATCH')
    return value

def main():
    action=sys.argv[1] if len(sys.argv)>1 else ''
    if action!='get':
        return  # never persist store/erase input
    fields=dict(line.rstrip('\n').split('=',1) for line in sys.stdin if '=' in line)
    if fields.get('protocol')!='https' or fields.get('host')!='github.com':
        raise ValueError('CREDENTIAL_TARGET_DENIED')
    if fields.get('path','').removesuffix('.git')!=os.environ['GITHUB_REPOSITORY']:
        raise ValueError('CREDENTIAL_REPOSITORY_DENIED')
    value=current()
    sys.stdout.write('username=x-access-token\npassword='+value['token']+'\n\n')

if __name__=='__main__':
    try:
        main()
    except Exception:
        sys.stderr.write('RUNTIME_CREDENTIAL_NOT_READY\n')
        raise SystemExit(2)
