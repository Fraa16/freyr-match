"""V40 test build: extras like in Candy Crush (they keep a colour and only go off in a match).
C1 an extra swapped with a treat without a match: swapped back, no move used, nothing went off
C2 the same extra swapped into a match: it goes off (its whole line), a move is used
C3 four in a row makes a cat in the colour of the four, drawn as that treat with stripes
C4 an extra in a match made by a normal swap elsewhere goes off
C5 the bowl swapped with a treat still works, and eats the extras of that colour too (they go off)
C6 two extras swapped together: still a combo
C7 hints and the bot: no free moves with a coloured extra, only real matches
C8 collect goals count a coloured extra as its colour
C9 the bot plays 30 turns: board consistent
C10 with the rule off, the old way works again"""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import veteran
from fontfix import fonts
GAME = os.environ.get('GAME', 'game40.html')
HN = open(D + '/harness.js').read()
SHOTS = D + '/shots40'; os.makedirs(SHOTS, exist_ok=True)
fails = []
def ok(m, c, info=None):
    print(('OK   ' if c else 'FAIL ') + m + ('' if c or info is None else '  ' + json.dumps(info)[:400]))
    if not c: fails.append(m)
LVL = {'name': 'Testfeld', 'moves': 60, 'target': 1000, 'collect': [[0, 400]], 'board': ['........'] * 8}
def start(pg, lvl=LVL):
    pg.evaluate("() => { document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); if (!onMap) showMap(); }"); pg.wait_for_timeout(600)
    pg.evaluate("(d) => { LEVELS[0] = d; }", lvl)
    pg.evaluate('openLevel(1)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1400)
    pg.add_script_tag(content=HN); pg.evaluate('T_waitIdle()')
# T_setup, then the extras get the given colours
SETUP = """([T, cells, extras]) => { T_setup(T, cells, extras.map(e => e.slice(0, 4))); for (const e of extras) if (e[4] != null) grid[e[0]][e[1]].col = e[4]; render(false); return findMatches().cells.size; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 402, 'height': 874}, device_scale_factor=2, has_touch=True, is_mobile=True)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    veteran.veteran(pg)
    pg.goto('file://' + D + '/' + GAME)
    pg.evaluate("localStorage.setItem('wm-intro','1'); localStorage.setItem('wm-level', 200); localStorage.setItem('wm-purr-told','1'); localStorage.setItem('wm-music','off'); localStorage.removeItem('wm-pair40')")
    pg.reload(); pg.wait_for_timeout(600); fonts(pg)
    pg.evaluate("() => { try { if (introRun && introRun.kind === 'wake') mapSkip = true; } catch (e) {} }"); pg.wait_for_function('!introRun', timeout=10000); pg.wait_for_timeout(900)
    if pg.evaluate("document.getElementById('introOv').classList.contains('show')"): pg.click('#introX'); pg.wait_for_timeout(300)
    pg.evaluate("LEVELS[0].intro = null")
    ok('the rule is on by default', pg.evaluate('PAIR40') is True)
    start(pg)
    # C1: a cat (colour 1) at (4,3), no 1s anywhere: swap with (4,4)
    pre = pg.evaluate(SETUP, [1, [], [[4, 3, 'cat', 'h', 1]]])
    r = pg.evaluate("""async () => { const m0 = moves, s0 = score; await trySwap(4, 3, 4, 4); await T_waitIdle();
      return { moved: m0 - moves, gained: score - s0, at: grid[4][3] && grid[4][3].type, col: grid[4][3] && grid[4][3].col, check: T_check() }; }""")
    ok('C1 extra + treat without a match: swapped back, no move, nothing went off', pre == 0 and r['moved'] == 0 and r['gained'] == 0 and r['at'] == 'cat' and r['col'] == 1, r)
    # C2: two 1s at (4,5) (4,6): the cat landing at (4,4) makes a match and goes off
    pg.evaluate(SETUP, [1, [[4, 5], [4, 6]], [[4, 3, 'cat', 'v', 1]]])
    r = pg.evaluate("""async () => { const m0 = moves, s0 = score; let fired = 0; const f0 = fire; fire = function (cell) { if (cell.type === 'cat') fired++; return f0.apply(this, arguments); };
      try { await trySwap(4, 3, 4, 4); await T_waitIdle(); } finally { fire = f0; } return { moved: m0 - moves, gained: score - s0, fired, check: T_check() }; }""")
    ok('C2 the cat swapped into a match goes off, one move used', r['moved'] == 1 and r['fired'] >= 1 and r['gained'] >= 160 and not r['check'], r)
    # C3: four 2s across: a cat in colour 2, drawn as the treat with stripes
    pg.evaluate(SETUP, [2, [[3, 1], [3, 2], [3, 4], [2, 3]], []])
    r = pg.evaluate("""async () => { const seen = []; const g0 = gravity; gravity = function () { if (!seen.length) for (let k = 0; k < N * N; k++) { const x = grid[k / N | 0][k % N]; if (x && x.type === 'cat') seen.push([k, x.col, iconFor(x).includes('sprint40')]); } return g0.apply(this, arguments); };
      try { await trySwap(2, 3, 3, 3); await T_waitIdle(); } finally { gravity = g0; } return { seen, check: T_check() }; }""")
    ok('C3 four 2s make a cat of colour 2, drawn as the treat with the marks', r['seen'] and r['seen'][0][1] == 2 and r['seen'][0][2], r)
    pg.screenshot(path=SHOTS + '/c3.png')
    # C4: a nip of colour 1 at (4,2), a 1 at (4,3); a 1 swapped down into (4,4) from (3,4): the nip goes off
    pg.evaluate(SETUP, [1, [[4, 3], [3, 4]], [[4, 2, 'nip', None, 1]]])
    r = pg.evaluate("""async () => { let fired = 0; const f0 = fire; fire = function (cell) { if (cell.type === 'nip') fired++; return f0.apply(this, arguments); };
      try { await trySwap(3, 4, 4, 4); await T_waitIdle(); } finally { fire = f0; } return { fired, check: T_check() }; }""")
    ok('C4 an extra in a match made by a normal swap goes off', r['fired'] == 1 and not r['check'], r)
    # C5: bowl next to a 3; a laser of colour 3 elsewhere: the bowl eats the 3s and the laser goes off
    pg.evaluate(SETUP, [3, [[4, 4], [0, 0], [7, 7]], [[4, 3, 'bowl'], [1, 6, 'laser', None, 3]]])
    r = pg.evaluate("""async () => { let fired = 0; const f0 = fire; fire = function (cell) { if (cell.type === 'laser') fired++; return f0.apply(this, arguments); };
      try { await trySwap(4, 3, 4, 4); await T_waitIdle(); } finally { fire = f0; } return { fired, threes: countOnBoard(x => x.type === 3 && !x.fresh), check: T_check() }; }""")
    ok('C5 the bowl still goes with a treat, and sets off the extras of that colour', r['fired'] >= 1 and not r['check'], r)
    # C6: cat + nip swapped: the big cross
    pg.evaluate(SETUP, [1, [], [[4, 3, 'cat', 'h', 0], [4, 4, 'nip', None, 2]]])
    r = pg.evaluate("""async () => { const m0 = moves, s0 = score; await trySwap(4, 3, 4, 4); await T_waitIdle(); return { moved: m0 - moves, gained: score - s0, check: T_check() }; }""")
    ok('C6 two extras swapped together: combo as before', r['moved'] == 1 and r['gained'] >= 600 and not r['check'], r)
    # C7: hints: a coloured cat among treats with no match anywhere: no free move from the cat
    pg.evaluate(SETUP, [1, [], [[4, 3, 'cat', 'h', 1]]])
    r = pg.evaluate("""() => { const ms = rankMoves().filter(m => (m.r === 4 && m.c === 3) || (m.r2 === 4 && m.c2 === 3)); const fm = findMove();
      const usesCat = fm && fm.some(([r, c]) => r === 4 && c === 3); return { n: ms.length, usesCat, cm: countMoves() }; }""")
    ok('C7 hints and the bot see no free move with the coloured cat', r['n'] == 0 and not r['usesCat'], r)
    # C8: a collect goal for colour 1 counts a coloured cat of colour 1
    pg.evaluate(SETUP, [1, [[4, 5], [4, 6]], [[4, 3, 'cat', 'v', 1]]])
    r = pg.evaluate("""async () => { goals = [{ kind: 'collect', type: 1, n: 50, left: 50 }]; lastRem = []; updateHud();
      let cnt = 0; for (let k = 0; k < N * N; k++) { const x = grid[k / N | 0][k % N]; if (x && x.type === 'cat') cnt++; }
      await trySwap(4, 3, 4, 4); await T_waitIdle(); return { left: goals[0].left, check: T_check() }; }""")
    ok('C8 the cat counts for its colour in a collect goal (3 eaten at least: two 1s and the cat)', r['left'] <= 47, r)
    # C9: the bot plays 30 turns
    start(pg)
    r = pg.evaluate("""async () => { const out = [];
      for (let i = 0; i < 30 && moves > 0 && !goalsDone(); i++) { const m = bestMove(); if (!m) { out.push('no move'); break; } await trySwap(m.r, m.c, m.r2, m.c2); await T_waitIdle(); const p = T_check(); if (p.length) { out.push(i + ': ' + p.join('; ')); break; } }
      const ex = []; for (let k = 0; k < N * N; k++) { const x = grid[k / N | 0][k % N]; if (x && ['cat', 'nip', 'laser'].includes(x.type)) ex.push([x.type, x.col]); }
      return { out, moves, ex }; }""")
    ok('C9 30 bot turns: board consistent, extras on the board all have a colour', not r['out'] and all(c is not None for _, c in r['ex']), r)
    pg.screenshot(path=SHOTS + '/played.png')
    # C10: rule off: the cat goes off with any treat again
    pg.evaluate("PAIR40 = false")
    pg.evaluate(SETUP, [1, [], [[4, 3, 'cat', 'h', 1]]])
    r = pg.evaluate("""async () => { const m0 = moves, s0 = score; await trySwap(4, 3, 4, 4); await T_waitIdle(); return { moved: m0 - moves, gained: score - s0, check: T_check() }; }""")
    ok('C10 rule off: extra + treat goes off as before', r['moved'] == 1 and r['gained'] > 0 and not r['check'], r)
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', len(fails))
