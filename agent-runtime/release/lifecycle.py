"""Deterministic promotion proposal guard; never publishes or changes tags."""
import re

def validate(candidate,previous=None):
    if (candidate.get('schema')!='1.0.0' or candidate.get('runtime')!='opencode'
        or candidate.get('platform')!='linux/amd64'
        or candidate.get('host_agent_major')!=1
        or not re.fullmatch(r'sha256:[a-f0-9]{64}',candidate.get('digest',''))
        or not re.fullmatch(r'[a-f0-9]{40}',candidate.get('revision',''))
        or candidate.get('conformance')!='PASS'):
        raise ValueError('CANDIDATE_NOT_READY')
    if previous is not None and previous['host_agent_major']!=candidate['host_agent_major']:
        raise ValueError('COMPATIBILITY_REVIEW_REQUIRED')
    return {'stable':candidate['digest'],'previous':None if previous is None else previous['digest'],
            'revision':candidate['revision'],'mutation':'PROPOSAL_ONLY'}

def rollback(current):
    if not re.fullmatch(r'sha256:[a-f0-9]{64}',current.get('previous') or ''):
        raise ValueError('NO_ACCEPTED_ROLLBACK_DIGEST')
    return {'stable':current['previous'],'previous':current['stable'],'mutation':'PROPOSAL_ONLY'}
