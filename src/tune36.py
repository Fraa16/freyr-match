"""Tunes levels 161-260 with the bot (sim36.py), in two steps:
1) length: with plenty of moves, how many moves does the bot need? goals are scaled until that matches the planned length
2) moves: the moves are set so the bot wins about as often as planned (normal levels get a little harder towards 260)
Writes fix36.json (only the fields that changed). usage: python3 tune36.py [phase]   phase: all (default), length, moves"""
import json, os, sys, subprocess, math, random
D = os.path.dirname(os.path.abspath(__file__)) + '/'
LV = {161 + i: d for i, d in enumerate(json.load(open(D + 'levels36.json')))}
FIX = json.load(open(D + 'fix36.json')) if os.path.exists(D + 'fix36.json') else {}
cur = lambda L: {**LV[L], **FIX.get(str(L), {})}
PHASE = sys.argv[1] if len(sys.argv) > 1 else 'all'
LEVELS = list(range(161, 261))

def sim(levels, runs, ovr, tag):
    """runs the bot over the levels in two processes, returns {L: [[won, left, moves, used], ...]}"""
    json.dump({str(k): v for k, v in ovr.items()}, open(D + f'_ovr_{tag}.json', 'w'))
    half = [levels[0::2], levels[1::2]]
    procs = []
    for i, part in enumerate(half):
        if not part: continue
        out = D + f'_sim_{tag}_{i}.jsonl'
        if os.path.exists(out): os.remove(out)
        env = dict(os.environ, OVR=D + f'_ovr_{tag}.json', SRC=os.environ.get('SRC', 'game36t.html'))
        procs.append((subprocess.Popen(['python3', D + 'sim36.py', ','.join(map(str, part)), str(runs), os.path.basename(out)], cwd=D, env=env,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), out))
    res = {}
    for p, out in procs:
        p.wait()
        for line in open(out):
            r = json.loads(line); res[r['L']] = r
    return res

def plan_len(L, d):
    t = (L - 161) / 99
    n = 15 + 5 * t
    if d.get('intro') in ('belt', 'dark', 'wild'): n = 11
    if d.get('hard') == 1: n += 3
    if d.get('hard') == 2: n += 5
    if d.get('long'): n *= 1.8
    return n
def plan_win(L, d):
    t = (L - 161) / 99
    if d.get('intro') in ('belt', 'dark', 'wild'): return .85
    if d.get('hard') == 2: return .35
    if d.get('hard') == 1: return .45
    return .72 - .12 * t

def masked(d): return sum(ch != ' ' for r in d['board'] for ch in r)
def scale(L, f):
    d = cur(L); ch = {}
    if d.get('collect'): ch['collect'] = [[t, max(6, round(n * f))] for t, n in d['collect']]
    if d.get('bells'): ch['bells'] = max(1, min(8, round(d['bells'] * f)))
    if d.get('make'): ch['make'] = [[w, max(1, min(6, round(n * f)))] for w, n in d['make']]
    if d.get('goldrush'): ch['goldrush'] = max(3, min(24, round(d['goldrush'] * f)))
    if d.get('boss'): ch['boss'] = max(20, min(110, round(d['boss'] * f)))
    if d.get('cover'): ch['cover'] = max(10, min(round(.92 * masked(d)), round(d['cover'] * f)))
    if f > 1.25 and not (d.get('collect') or d.get('bells') or d.get('make') or d.get('goldrush')):
        # only board goals (dark, boxes, milk ...): one kind to eat on top
        used = {t for t, _ in d.get('collect', [])}
        t = random.Random(L).choice([x for x in range(5) if x not in used])
        ch['collect'] = [[t, round(14 * (f - 1) + 10)]]
    FIX.setdefault(str(L), {}).update(ch)

def used_of(r):
    w = [x for x in r['runs'] if x[0]]
    return sum(x[3] for x in w) / len(w) if w else 99, len(w) / len(r['runs'])

if PHASE in ('all', 'length'):
    todo = list(LEVELS)
    for it in range(4):
        ovr = {L: {**{k: v for k, v in FIX.get(str(L), {}).items()}, 'moves': 70} for L in todo}
        res = sim(todo, 6, ovr, 'len')
        nxt = []
        for L in todo:
            d = cur(L); u, w = used_of(res[L]); want = plan_len(L, d)
            f = want / max(1, u)
            print(f'len it{it} L{L} used {u:.1f} want {want:.1f} win {w:.2f} f {f:.2f} probs {res[L]["probs"][:2]}', flush=True)
            if abs(f - 1) > .15 and it < 3: scale(L, max(.6, min(2.6, f))); nxt.append(L)
        json.dump(FIX, open(D + 'fix36.json', 'w'), ensure_ascii=False, indent=0)
        todo = nxt
        if not todo: break

if PHASE in ('all', 'moves', 'cont'):
    # first guess from the measured length, then three rounds of corrections
    lens = {}
    res = sim(LEVELS, 6, {L: {**FIX.get(str(L), {}), 'moves': 70} for L in LEVELS}, 'len2')
    for L in LEVELS: lens[L] = used_of(res[L])[0]
    if PHASE != 'cont':
        for L in LEVELS:
            d = cur(L); FIX.setdefault(str(L), {})['moves'] = max(10, round(lens[L] * (.9 + .75 * plan_win(L, d) ** 2)))
    for it, runs in enumerate([20, 24, 30, 40] if PHASE != 'cont' else [24, 30, 40]):
        it += 4 - (3 if PHASE == 'cont' else 4)
        res = sim(LEVELS, runs, {L: FIX.get(str(L), {}) for L in LEVELS}, 'mv')
        for L in LEVELS:
            d = cur(L); w = used_of(res[L])[1]; want = plan_win(L, d); m = d['moves']
            err = want - w
            step = 0 if abs(err) < (.08 if it < 3 else .06) else max(1, round(abs(err) * lens[L] * .9)) * (1 if err > 0 else -1)
            if it == 3: step = max(-2, min(2, step))
            print(f'mv it{it} L{L} moves {m} win {w:.2f} want {want:.2f} -> {m + step}', flush=True)
            FIX[str(L)]['moves'] = max(10, m + step)
        json.dump(FIX, open(D + 'fix36.json', 'w'), ensure_ascii=False, indent=0)
for f in os.listdir(D):
    if f.startswith('_ovr_') or f.startswith('_sim_'): os.remove(D + f)
print('done')
