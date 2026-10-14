"""Second pass for the moves of levels 161-260: uses every (moves, win rate) the bot has measured so far (tune36*.log) and
picks the moves where the curve crosses the planned win rate (logistic fit), then checks with 40 bot runs and repeats for the levels still off.
usage: python3 tune36b.py [rounds]"""
import json, os, re, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tune36 as T   # (only the helpers; tune36 runs nothing when imported with PHASE 'none')
D = T.D
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 2
obs = {L: [] for L in T.LEVELS}
for log, runs in [('tune36.log', {0: 20, 1: 24}), ('tune36b.log', {1: 24, 2: 30, 3: 40})]:
    if not os.path.exists(D + log): continue
    for line in open(D + log):
        m = re.match(r'mv it(\d) L(\d+) moves (\d+) win ([\d.]+)', line)
        if not m: continue
        it, L, mv, w = int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))
        if L == 243 and log == 'tune36.log': continue   # 243 got an extra goal after the first run
        obs[L].append((mv, w, runs.get(it, 24)))
def fit(L, want):
    pts = obs[L]
    if not pts: return None
    # logistic in the moves, slope from the data if there are two different move counts, else a guess
    best = None
    for s in [x / 4 for x in range(2, 41)]:
        for m0x in range(10 * 4, 70 * 4):
            m0 = m0x / 4
            err = sum(n * (w - 1 / (1 + math.exp(-(mv - m0) / s))) ** 2 for mv, w, n in pts)
            # a weak pull towards a plausible slope (about two moves per 10 % around the middle)
            err += 3 * ((s - 2.2) / 2.2) ** 2
            if best is None or err < best[0]: best = (err, m0, s)
    _, m0, s = best
    want = min(.97, max(.03, want))
    return max(10, round(m0 + s * math.log(want / (1 - want))))
T.FIX = json.load(open(D + 'fix36.json'))
todo = list(T.LEVELS)
for rnd in range(ROUNDS):
    for L in todo:
        d = T.cur(L); mv = fit(L, T.plan_win(L, d))
        if mv: T.FIX[str(L)]['moves'] = mv
    json.dump(T.FIX, open(D + 'fix36.json', 'w'), ensure_ascii=False, indent=0)
    res = T.sim(todo, 40, {L: T.FIX.get(str(L), {}) for L in todo}, 'fit')
    nxt = []
    for L in todo:
        d = T.cur(L); w = T.used_of(res[L])[1]; want = T.plan_win(L, d)
        obs[L].append((d['moves'], w, 40))
        print(f'fit r{rnd} L{L} moves {d["moves"]} win {w:.2f} want {want:.2f}', flush=True)
        if abs(w - want) > .1: nxt.append(L)
    todo = nxt
    if not todo: break
# the last guesses for the ones still off
for L in todo:
    d = T.cur(L); mv = fit(L, T.plan_win(L, d))
    if mv: T.FIX[str(L)]['moves'] = mv
json.dump(T.FIX, open(D + 'fix36.json', 'w'), ensure_ascii=False, indent=0)
json.dump({str(k): v for k, v in obs.items()}, open(D + 'tune36_obs.json', 'w'))
print('done, still off:', todo)
