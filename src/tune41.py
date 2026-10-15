"""V41: the moves of every level for the pair rule (extras only go off in a match).
The bot played all 260 levels with both rules at the current moves (_p41_old.jsonl, _p41_pair.jsonl, 30 runs each).
Wanted: with pairs the bot wins about 10 points less than it did with the old rule ("etwas schwerer"),
except the first ten levels and the levels that bring something new (intro): those stay as they were.
The old win rate of a level is only 30 runs, so it is evened out with its neighbours of the same kind (half and half).
Then the moves are fitted (logistic in the moves, as in tune36b) and checked with 40 bot runs, up to ROUNDS times.
Writes fix41.json {L: {moves}} and tune41.log. usage: python3 tune41.py [rounds]"""
import json, os, re, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tune36 as T
D = T.D
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
SRC = os.environ.get('SRC', 'game41tune.html')
os.environ['SRC'] = SRC
DROP = float(os.environ.get('DROP', '.10'))

def load(f): return {d['L']: d for d in map(json.loads, open(D + f))}
old, pair = load('_p41_old.jsonl'), load('_p41_pair.jsonl')
src = open(D + SRC).read()
i = src.index('const LEVELS = ['); j = src.index('\n];', i)
defs = re.split(r'\n  \{ name: ', src[i:j])[1:]
LV = {}
for L, t in enumerate(defs, 1):
    LV[L] = {'moves': int(re.search(r'moves: (\d+)', t).group(1)), 'hard': int((re.search(r'hard: (\d)', t) or [0, 0])[1]),
             'boss': ' boss: ' in t or "'V'" in t or 'V' in ''.join(re.findall(r"'([^']*)'", t.split('board:')[1])),
             'intro': bool(re.search(r"intro: '", t))}
win = lambda d: sum(x[0] for x in d['runs']) / len(d['runs'])
def kind(L): return (LV[L]['hard'], LV[L]['boss'])
target = {}
for L in LV:
    near = [win(old[K]) for K in LV if abs(K - L) <= 15 and K != L and kind(K) == kind(L)]
    base = .5 * win(old[L]) + .5 * (sum(near) / len(near)) if near else win(old[L])
    keep = L <= 10 or LV[L]['intro']
    target[L] = max(.15, min(.92, base - (0 if keep else DROP)))
obs = {L: [(LV[L]['moves'], win(pair[L]), 30)] for L in LV}

def fit(L, want):
    pts = obs[L]
    best = None
    for s4 in range(4, 33):
        s = s4 / 4
        for m4 in range(8 * 4, 90 * 4):
            m0 = m4 / 4
            err = sum(n * (w - 1 / (1 + math.exp(-(mv - m0) / s))) ** 2 for mv, w, n in pts) + 3 * ((s - 2.2) / 2.2) ** 2
            if best is None or err < best[0]: best = (err, m0, s)
    _, m0, s = best
    want = min(.97, max(.03, want))
    return max(10, round(m0 + s * math.log(want / (1 - want))))

log = open(D + 'tune41.log', 'a')
def say(t): print(t, flush=True); log.write(t + '\n'); log.flush()
FIX = {}
todo = [L for L in LV if abs(win(pair[L]) - target[L]) > .06]
for L in LV:
    if L not in todo: FIX[str(L)] = {'moves': LV[L]['moves']}
say(f'start: {len(todo)} of {len(LV)} levels to fit, drop {DROP}')
for rnd in range(ROUNDS):
    # a guess from one or two points can be wild: at most 8 moves away from the last one tried
    for L in todo: last = obs[L][-1][0]; FIX[str(L)] = {'moves': max(last - 8, min(last + 8, fit(L, target[L])))}
    json.dump(FIX, open(D + 'fix41.json', 'w'), indent=0)
    res = T.sim(todo, 40, {L: FIX[str(L)] for L in todo}, 'p41r%d' % rnd)
    nxt = []
    for L in todo:
        mv = FIX[str(L)]['moves']; w = T.used_of(res[L])[1]
        obs[L].append((mv, w, 40))
        say(f'r{rnd} L{L} moves {LV[L]["moves"]}->{mv} win {w:.2f} want {target[L]:.2f} probs {res[L]["probs"][:1]}')
        if abs(w - target[L]) > .1: nxt.append(L)
    todo = nxt
    if not todo: break
for L in todo: FIX[str(L)] = {'moves': fit(L, target[L])}
json.dump(FIX, open(D + 'fix41.json', 'w'), indent=0)
json.dump({'target': target, 'obs': obs}, open(D + 'tune41_obs.json', 'w'))
say('done, still off: %s' % todo)
