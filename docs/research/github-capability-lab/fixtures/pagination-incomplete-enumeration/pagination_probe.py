"""Public read-only bounded pagination fixture. Writes only a local compact receipt.

No mutation, secrets, label text, or private resources are exported. The record
is one observation window, not snapshot isolation or an authorization claim.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import subprocess

API_VERSION = '2026-03-10'
REPOSITORY = 'youling/ai-use'
MAX_PAGES = 20

def gh(*args):
    p = subprocess.run(['gh', *args], capture_output=True, encoding='utf-8')
    if p.returncode:
        raise RuntimeError('Read failed; incomplete evidence, no absence/currentness claim')
    value = json.loads(p.stdout)
    if isinstance(value, dict) and value.get('errors'):
        raise RuntimeError('GraphQL errors; incomplete evidence')
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    meta = gh('api', f'repos/{REPOSITORY}', '-H', f'X-GitHub-Api-Version: {API_VERSION}')
    if meta.get('private') or meta.get('visibility') != 'public':
        raise RuntimeError('Fixture accepts public repository only')
    ids, rest_pages = [], []
    for page in range(1, MAX_PAGES+1):
        values = gh('api', f'repos/{REPOSITORY}/labels?per_page=2&page={page}', '-H', f'X-GitHub-Api-Version: {API_VERSION}')
        ids.extend(x['node_id'] for x in values)
        rest_pages.append(len(values))
        if len(values) < 2:
            break
    else:
        raise RuntimeError('REST page budget exhausted; incomplete')
    query = 'query($after:String) { repository(owner:"youling",name:"ai-use") { labels(first:2,after:$after) { totalCount nodes { id } pageInfo { hasNextPage endCursor } } } }'
    cursor, gql_ids, gql_pages, totals = None, [], [], []
    for _ in range(MAX_PAGES):
        cli = ['api','graphql','-f','query='+query]
        if cursor:
            cli += ['-f','after='+cursor]
        data = gh(*cli)['data']['repository']['labels']
        gql_ids.extend(x['id'] for x in data['nodes'])
        totals.append(data['totalCount'])
        gql_pages.append({'count':len(data['nodes']),'has_next_page':data['pageInfo']['hasNextPage']})
        if not data['pageInfo']['hasNextPage']:
            break
        next_cursor = data['pageInfo']['endCursor']
        if not next_cursor or next_cursor == cursor:
            raise RuntimeError('Missing/repeated cursor; incomplete')
        cursor = next_cursor
    else:
        raise RuntimeError('GraphQL page budget exhausted; incomplete')
    if not (len(ids) == len(set(ids)) == len(gql_ids) == len(set(gql_ids)) and set(ids) == set(gql_ids) and set(totals) == {len(ids)}):
        raise RuntimeError('Enumeration mismatch; no full-set claim')
    if len(ids) <= 2:
        raise RuntimeError('Insufficient public fixture population for first-page negative case')
    finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = {
        'receipt_version':'1.0.0', 'repository':REPOSITORY, 'visibility':'public',
        'started_at':started,'finished_at':finished,
        'principal_type':'existing authenticated GitHub CLI session',
        'permission_class':'public repository read, no scope expansion', 'plan':'unknown',
        'api_version':API_VERSION, 'graphql_version':'unversioned schema at observation',
        'fixture_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        'source_kind':'non-Git live label metadata in the recorded observation window',
        'rest_page_counts':rest_pages,'graphql_pages':gql_pages,
        'unique_count':len(ids),'same_unique_ids':True,
        'unique_id_set_sha256':hashlib.sha256(json.dumps(sorted(ids),separators=(',',':')).encode()).hexdigest(),
        'first_page_count':rest_pages[0], 'first_page_complete':False,
        'resources_created':[], 'cleanup':'NOT_REQUIRED_READ_ONLY',
        'limits':['Small collection in one observation window; no atomic snapshot isolation',
                  'No concurrent mutation, rate-limit recovery, private visibility or search-index coverage',
                  'First page or forbidden/truncated output cannot prove absence or a full set'],
    }
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'finished_at':finished,'unique_count':len(ids),'rest_pages':rest_pages,'same_unique_ids':True,'first_page_complete':False}))

if __name__ == '__main__':
    main()
