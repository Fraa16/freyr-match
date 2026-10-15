"""(V41: the swap checks are for the old rule, without pairs; the pair rule has its own test, test_v40.py)
V38: tile logic.
S: an extra swapped with a treat that makes a match where it lands: the extra goes off AND the match is eaten and earns its extra
   (S1 the user's case: a cat swapped sideways out of a column of paws, the paw that comes in makes four: a new cat appears;
    S2 the same across; S3 the new extra's cell is inside the blast of the old one: it still appears; S4 no match: as before)
B: bells come down in changing columns, never twice in a row in the same one (unless there is no other gap for a while)"""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import veteran
from fontfix import fonts
GAME = os.environ.get('GAME', 'game.html')
HN = open(D + '/harness.js').read()
fails = []
def ok(m, c, info=None):
    print(('OK   ' if c else 'FAIL ') + m + ('' if c or info is None else '  ' + json.dumps(info)[:400]))
    if not c: fails.append(m)
LVL = {'name': 'Testfeld', 'moves': 60, 'target': 1000, 'collect': [[0, 400]], 'board': ['........'] * 8}
BELLS = {'name': 'Glocken', 'moves': 200, 'target': 1000, 'bells': 60, 'board': ['........'] * 8}
def start(pg, lvl):
    pg.evaluate("() => { document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); if (!onMap) showMap(); }"); pg.wait_for_timeout(600)
    pg.evaluate("(d) => { LEVELS[0] = d; }", lvl)
    pg.evaluate('openLevel(1)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1400)
    pg.add_script_tag(content=HN); pg.evaluate('T_waitIdle()')
# a board without T, the given T cells and extras; swap; what extras are on the board right after the first round of clearing
SWAP = """async ([T, cells, extras, sw]) => {
  T_setup(T, cells, extras);
  if (findMatches().cells.size) return { pre: true };
  const seen = []; const g0 = gravity;
  gravity = function () { if (!seen.length) seen.push(T_kinds()); return g0.apply(this, arguments); };
  try { await trySwap(...sw); await T_waitIdle(); } finally { gravity = g0; }
  return { first: seen[0] || [], check: T_check() };
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 402, 'height': 874}, device_scale_factor=2, has_touch=True, is_mobile=True)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    veteran.veteran(pg)
    pg.goto('file://' + (GAME if GAME.startswith('/') else D + '/' + GAME))
    pg.evaluate("localStorage.setItem('wm-intro','1'); localStorage.setItem('wm-news41','done'); localStorage.setItem('wm-pair40','off'); localStorage.setItem('wm-level', 200); localStorage.setItem('wm-purr-told','1'); localStorage.setItem('wm-music','off')")
    pg.reload(); pg.wait_for_timeout(600); fonts(pg)
    pg.evaluate("() => { try { if (introRun && introRun.kind === 'wake') mapSkip = true; } catch (e) {} }"); pg.wait_for_function('!introRun', timeout=10000); pg.wait_for_timeout(900)
    if pg.evaluate("document.getElementById('introOv').classList.contains('show')"): pg.click('#introX'); pg.wait_for_timeout(300)
    pg.evaluate("LEVELS[0].intro = null")
    start(pg, LVL)

    # S1: paws at (1,1) (2,1) (4,1), an upright cat at (3,1), a paw at (3,2): swap cat and paw
    r = pg.evaluate(SWAP, [1, [[1, 1], [2, 1], [4, 1], [3, 2]], [[3, 1, 'cat', 'v']], [3, 1, 3, 2]])
    cats = [k for k in r.get('first', []) if k[2] == 'cat']
    ok('S1 cat swapped out of a column of paws: the four paws make a new upright cat where the paw landed', [3, 1, 'cat', 'v'] in cats, r)
    ok('S1 the old cat went off (no cat left in column 2)', not any(k[1] == 2 and k[2] == 'cat' for k in cats), r)
    ok('S1 board consistent', not r.get('check'), r.get('check'))
    # S2: across: paws at (3,0) (3,2) (3,3), a flat cat at (3,1), a paw at (2,1): swap cat and paw upwards
    r = pg.evaluate(SWAP, [1, [[3, 0], [3, 2], [3, 3], [2, 1]], [[3, 1, 'cat', 'h']], [3, 1, 2, 1]])
    cats = [k for k in r.get('first', []) if k[2] == 'cat']
    ok('S2 the paw swapped down makes four across: a new flat cat', [3, 1, 'cat', 'h'] in cats, r)
    # S3: the old cat clears the row the new one appears in: the new one still appears
    r = pg.evaluate(SWAP, [1, [[1, 1], [2, 1], [4, 1], [3, 2]], [[3, 1, 'cat', 'h']], [3, 1, 3, 2]])
    cats = [k for k in r.get('first', []) if k[2] == 'cat']
    ok('S3 new cat inside the blast of the old one still appears', [3, 1, 'cat', 'v'] in cats, r)
    # S3b: five paws make a bowl. Paws at (1,1) (2,1) (4,1) (5,1), laser at (3,1), paw at (3,0)
    r = pg.evaluate(SWAP, [1, [[1, 1], [2, 1], [4, 1], [5, 1], [3, 0]], [[3, 1, 'laser']], [3, 1, 3, 0]])
    ok('S3b laser swapped out of five: a bowl appears', any(k[:3] == [3, 1, 'bowl'] for k in r.get('first', [])), r)
    # S4: no match where the treat lands: as before, both go, no new extra
    r = pg.evaluate(SWAP, [1, [[3, 2]], [[3, 1, 'cat', 'v']], [3, 1, 3, 2]])
    ok('S4 no match: nothing new appears in the first round', not r.get('first'), r)
    ok('S4 board consistent', not r.get('check'), r.get('check'))
    # S5: the bowl eats the kind as before, no extra from the paws it was swapped with
    r = pg.evaluate(SWAP, [1, [[1, 1], [2, 1], [4, 1], [3, 2]], [[3, 1, 'bowl']], [3, 1, 3, 2]])
    ok('S5 bowl swapped with a paw: eats the paws, no new cat', not [k for k in r.get('first', []) if k[2] != 'bowl'] and not r.get('check'), r)
    # S6: a plain swap is untouched: four in a column from a normal swap gives a cat
    r = pg.evaluate(SWAP, [1, [[1, 1], [2, 1], [4, 1], [3, 2]], [], [3, 1, 3, 2]])
    ok('S6 plain swap: the cat appears as always', [3, 1, 'cat', 'v'] in r.get('first', []), r)

    # B: the bot plays a bell level; where does every new bell come down?
    start(pg, BELLS)
    r = pg.evaluate("""async () => {
      const cols = [], known = new Set(); const g0 = gravity;
      const scan = () => { for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const x = grid[r][c]; if (x && x.type === 'bell' && !known.has(x.id)) { known.add(x.id); cols.push(c); } } };
      scan(); const first = cols.length;
      gravity = function () { const r = g0.apply(this, arguments); scan(); return r; };
      const probs = [];
      try {
        for (let i = 0; i < 90 && moves > 0 && !goalsDone(); i++) { const m = bestMove(); if (!m) break; await trySwap(m.r, m.c, m.r2, m.c2); await T_waitIdle(); const p = T_check(); if (p.length) { probs.push(i + ': ' + p.join('; ')); break; } }
      } finally { gravity = g0; }
      const sp = cols.slice(first), same = sp.filter((c, i) => i && c === sp[i - 1]).length;
      return { sp, same, distinct: new Set(sp).size, probs, down: cfg.bells - remaining(goals.find(g => g.kind === 'bells')) };
    }""")
    print('   bell columns', r['sp'], 'same as the one before:', r['same'], 'distinct', r['distinct'], 'down', r['down'])
    ok('B1 enough bells came down to judge (>= 12)', len(r['sp']) >= 12, r)
    ok('B2 bells come in at least 5 different columns', r['distinct'] >= 5, r)
    ok('B3 at most one in ten comes down the same column as the one before', r['same'] <= len(r['sp']) // 10, r)
    ok('B4 board consistent while playing', not r['probs'], r['probs'])
    # B5: a bell from the start drops out of column 2: the gap there gets a treat, the next bell waits for a gap elsewhere
    r = pg.evaluate("""async () => {
      await T_waitIdle(); T_base(1); lastBellCol = -1; bellWait = 0;
      grid[7][2] = mk('bell'); bellsLeft = 5; render(false);
      const n = collectBells(); gravity(); await new Promise(r => setTimeout(r, 400));
      const bellsNow = []; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (grid[r][c] && grid[r][c].type === 'bell') bellsNow.push([r, c]);
      grid[3][5] = null; gravity(); await new Promise(r => setTimeout(r, 400));
      const after = []; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (grid[r][c] && grid[r][c].type === 'bell') after.push([r, c]);
      return { n, bellsNow, after, check: T_check() };
    }""")
    ok('B5 the bell dropped out of column 2: no new bell there right away', r['n'] == 1 and not r['bellsNow'], r)
    ok('B5 the next gap elsewhere (column 5) gets the bell', r['after'] == [[0, 5]], r)
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', len(fails))
