"""the longest main-thread tasks in a trace and what is inside them"""
import json, sys, collections
ev = json.load(open(sys.argv[1])); ev = ev['traceEvents'] if isinstance(ev, dict) else ev
X = [e for e in ev if e.get('ph') == 'X' and 'dur' in e]
# main thread = the thread with the most FunctionCall
th = collections.Counter((e['pid'], e['tid']) for e in X if e['name'] == 'FunctionCall').most_common(1)[0][0]
M = sorted([e for e in X if (e['pid'], e['tid']) == th], key=lambda e: e['ts'])
tasks = [e for e in M if e['name'] in ('RunTask', 'ThreadControllerImpl::RunTask')]
tasks.sort(key=lambda e: -e['dur'])
for t in tasks[:8]:
    s, en = t['ts'], t['ts'] + t['dur']
    inside = collections.Counter()
    for e in M:
        if e is t or e['ts'] < s or e['ts'] + e['dur'] > en: continue
        if e['name'] in ('RunTask', 'ThreadControllerImpl::RunTask'): continue
        inside[e['name']] += e['dur']
    print(f"task {t['dur'] / 1000:6.1f}ms at {(s - M[0]['ts']) / 1000:7.0f}ms:", ', '.join(f'{k} {v / 1000:.1f}' for k, v in inside.most_common(9)))
    # js functions inside
    fns = collections.Counter()
    for e in M:
        if e['ts'] >= s and e['ts'] + e['dur'] <= en and e['name'] in ('FunctionCall', 'TimerFire', 'FireAnimationFrame', 'EventDispatch'):
            d = e.get('args', {}).get('data', {}); fns[(d.get('functionName') or d.get('type') or e['name']) + ':' + str(d.get('lineNumber', ''))] += e['dur']
    print('      js:', ', '.join(f'{k} {v / 1000:.1f}' for k, v in fns.most_common(6)))
