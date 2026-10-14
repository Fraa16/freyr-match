"""the round-3 mechanics: gifts, triple boxes, cucumbers, alarm clocks, orders, gold rush, turbo robot, feather, super pounce"""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
H = open(D + '/harness.js').read()
SHOTS = '--shots' in sys.argv
BASE = int(os.environ.get('TL', 61))   # first test level (gifts+boxes), then cukes, clocks, turbo
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
def start(pg, L, ml=150):
    pg.goto('file://' + D + '/' + os.environ.get('GAME', 'game.html')); pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", {ml}); localStorage.setItem("wm-treats", 200)'); pg.reload(); pg.wait_for_timeout(600)
    if SHOTS: fonts(pg)
    pg.evaluate(WAIT_MAP); pg.evaluate(f'openLevel({L})'); pg.wait_for_timeout(400)
    if SHOTS: pg.screenshot(path=D + f'/n12_card_{L}.png')
    pg.click('#introBtn'); pg.wait_for_function('busy || !!tut', timeout=5000); pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(200)
def ev(pg, js): return pg.evaluate(js)
def swap(pg, a, b):
    ev(pg, f'(async () => {{ await trySwap({a[0]}, {a[1]}, {b[0]}, {b[1]}); }})()'); pg.wait_for_timeout(60); ev(pg, 'T_waitIdle()')
FIND = "(t) => { const o = []; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const x = grid[r][c]; if (x && (x.type === t || (t === 'clock' && x.clock != null))) o.push([r, c, x.hp, x.clock]); } return o; }"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2 if SHOTS else 1); __import__('veteran').veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    ok = lambda name, cond, info='': print(('OK   ' if cond else 'FAIL ') + name, info)
    # ---- gifts and triple boxes
    start(pg, BASE)
    ok('goals gifts+boxes', ev(pg, 'goals.map(g => g.kind).join()') == 'boxes,gifts', ev(pg, 'goals.map(g => g.kind + ":" + remaining(g)).join()'))
    gifts = ev(pg, f'({FIND})("gift")'); boxes = ev(pg, f'({FIND})("box")')
    ok('board has 4 gifts, 4 triple boxes', len(gifts) == 4 and all(x[2] == 3 for x in boxes), (gifts, boxes))
    if SHOTS: pg.screenshot(path=D + '/n12_gifts.png')
    # a vertical three right next to the gift at (1,1)
    ev(pg, "() => { const T = 0, o = 1; grid[0][0] = mk(T); grid[1][0] = mk(T); grid[2][0] = mk(o); grid[3][0] = mk(T); grid[0][1] = mk(2); grid[2][1] = mk(3); grid[3][1] = mk(2); render(false); }")
    pre = ev(pg, 'findMatches().cells.size'); swap(pg, (3, 0), (2, 0))
    g11 = ev(pg, 'grid[1][1] && grid[1][1].type')
    ok('gift opened into an extra', g11 in ('cat', 'laser', 'nip', 'bowl') and ev(pg, 'remaining(goals[1])') == 3, f'pre {pre} -> {g11}, gifts left {ev(pg, "remaining(goals[1])")}, check {ev(pg, "T_check()")[:2]}')
    # the triple box at (2,2) takes three hits
    hps = []
    for i in range(3):
        ev(pg, 'T_waitIdle()'); pg.wait_for_timeout(400); ev(pg, 'T_waitIdle()')
        ev(pg, '(async () => { aim = { kind: "paw" }; inv.paw = 3; await doAim(2, 2); })()'); pg.wait_for_timeout(60); ev(pg, 'T_waitIdle()')
        hps.append(ev(pg, 'grid[2][2] && grid[2][2].type === "box" ? "box" + grid[2][2].hp : "gone"'))
    ok('triple box: 3 -> 2 -> 1 -> gone', hps == ['box2', 'box1', 'gone'], hps)
    # ---- cucumbers
    start(pg, BASE + 1)
    cs0 = ev(pg, f'({FIND})("cuke")'); mv0 = ev(pg, 'moves')
    ev(pg, '(async () => { const m = bestMove(); await trySwap(m.r, m.c, m.r2, m.c2); })()'); pg.wait_for_timeout(60); ev(pg, 'T_waitIdle()')
    cs1 = ev(pg, f'({FIND})("cuke")')
    ok('cucumbers hop after a move', len(cs1) <= len(cs0) and set(map(tuple, (x[:2] for x in cs1))) != set(map(tuple, (x[:2] for x in cs0))), f'{[x[:2] for x in cs0]} -> {[x[:2] for x in cs1]} check {ev(pg, "T_check()")[:2]}')
    if SHOTS: pg.screenshot(path=D + '/n12_cukes.png')
    # chase one: a match next to it
    r, c = cs1[0][:2]
    n0 = ev(pg, 'remaining(goals.find(g => g.kind === "cukes"))')
    ev(pg, f"() => {{ const r = {r}, c = {c}; const nb = [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]].filter(([a, b]) => inB(a, b) && mask[a][b] && grid[a][b] && isNormal(grid[a][b].type)); window.__nb = nb; for (const [a, b] of nb) {{ grid[a][b] = mk(9); }} render(false); }}")
    gone = ev(pg, f"() => {{ const before = countOnBoard(x => x.type === 'cuke'); return before; }}")
    ev(pg, "() => { for (const [a, b] of window.__nb) grid[a][b] = mk(0); render(false); }")
    # make a horizontal three that touches the cucumber via a paw hit instead (robust): the paw tool on the cucumber
    ev(pg, f'(async () => {{ aim = {{ kind: "paw" }}; inv.paw = 2; await doAim({r}, {c}); }})()'); pg.wait_for_timeout(60); ev(pg, 'T_waitIdle()')
    ok('a hit chases a cucumber away', ev(pg, 'remaining(goals.find(g => g.kind === "cukes"))') == n0 - 1, f'{n0} -> {ev(pg, "remaining(goals.find(g => g.kind === \"cukes\"))")}')
    # ---- alarm clocks
    start(pg, BASE + 2)
    cl0 = ev(pg, f'({FIND})("clock")')
    ok('two clocks at 9', len(cl0) == 2 and all(x[3] == 9 for x in cl0), cl0)
    if SHOTS: pg.screenshot(path=D + '/n12_clocks.png')
    ev(pg, '(async () => { const m = bestMove(); await trySwap(m.r, m.c, m.r2, m.c2); })()'); pg.wait_for_timeout(60); ev(pg, 'T_waitIdle()')
    cl1 = ev(pg, f'({FIND})("clock")')
    ok('clocks tick down', all(x[3] == 8 for x in cl1 if x[3] is not None) and len(cl1) >= 1, cl1)
    ev(pg, "() => { for (const row of grid) for (const x of row) if (x && x.clock > 0) { x.clock = 1; drawClock(x); } }")
    if SHOTS: pg.wait_for_timeout(200); pg.screenshot(path=D + '/n12_clocklow.png')
    # a move that does not touch the clocks
    ev(pg, '(async () => { const cl = []; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (grid[r][c] && grid[r][c].clock > 0) cl.push(r * N + c); const ms = rankMoves().filter(m => ![m.r * N + m.c, m.r2 * N + m.c2].some(k => cl.some(q => Math.abs((q / N | 0) - (k / N | 0)) + Math.abs(q % N - k % N) <= 2))); const m = ms[0] || bestMove(); await trySwap(m.r, m.c, m.r2, m.c2); })()')
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=20000); pg.wait_for_timeout(300)
    ok('a clock rings: level lost', ev(pg, 'clockRang') and 'Wecker' in ev(pg, 'document.getElementById("endTitle").textContent'), ev(pg, 'document.getElementById("endTitle").textContent') + ' | ' + ev(pg, 'document.getElementById("endText").textContent'))
    if SHOTS: pg.screenshot(path=D + '/n12_rang.png')
    mv = ev(pg, 'moves'); pg.click('#rescueBtn'); pg.wait_for_timeout(300)
    ok('rescue sets clocks back and adds moves', ev(pg, 'moves') == mv + 5 and all(x[3] >= 5 for x in ev(pg, f'({FIND})("clock")')), (ev(pg, 'moves'), ev(pg, f'({FIND})("clock")')))
    # ---- turbo robot, orders, gold rush
    start(pg, BASE + 3)
    ok('goals boss+make+gold', ev(pg, 'goals.map(g => g.kind + (g.what || "")).join()') == 'boss,makecat,makecombo,gold', ev(pg, 'goals.map(g => goalText(g, remaining(g))).join(" | ")'))
    if SHOTS: pg.screenshot(path=D + '/n12_turbo.png')
    pos = [ev(pg, '[boss.r, boss.c]')]
    for i in range(3):
        ev(pg, '(async () => { const m = bestMove(); await trySwap(m.r, m.c, m.r2, m.c2); })()'); pg.wait_for_timeout(60); ev(pg, 'T_waitIdle()')
        pos.append(ev(pg, '[boss.r, boss.c]'))
    steps = [abs(a[0] - b2[0]) + abs(a[1] - b2[1]) for a, b2 in zip(pos, pos[1:])]
    ok('turbo robot drives up to 2 cells per move', max(steps) == 2, (pos, steps, ev(pg, 'T_check()')[:2]))
    # orders: a cat from four in a row, a combo from two extras, gold treats eaten
    ev(pg, "() => { boss.hp = 0; for (const [r, c] of bossCellsAt(boss.r, boss.c)) grid[r][c] = mk(2); if (boss.el) boss.el.remove(); boss = null; goals = goals.filter(g => g.kind !== 'boss'); }")
    ev(pg, 'goals.forEach(g => { if (g.kind === "make" || g.kind === "gold") g.left = g.n; }); updateHud()')
    ev(pg, 'T_setup(1, [[6,0],[6,1],[6,3],[5,2]])'); swap(pg, (5, 2), (6, 2))
    ok('order: a built cat counts', ev(pg, 'goals.find(g => g.what === "cat").left') == 1, ev(pg, 'goals.map(g => g.kind + ":" + remaining(g)).join()'))
    ev(pg, "() => { T_base(1); const a = mk('cat'); a.dir = 'h'; grid[4][3] = a; grid[4][4] = mk('nip'); render(false); }"); swap(pg, (4, 3), (4, 4))
    ok('order: a combo counts', ev(pg, 'goals.find(g => g.what === "combo").left') == 0, ev(pg, 'goals.map(g => g.kind + ":" + remaining(g)).join()'))
    ev(pg, "() => { T_setup(2, [[6,0],[6,1],[5,2]]); grid[6][0].gold = true; grid[6][1].gold = true; render(false); }"); g0 = ev(pg, 'goals.find(g => g.kind === "gold").left'); swap(pg, (5, 2), (6, 2))
    ok('gold rush: golden treats count', ev(pg, 'goals.find(g => g.kind === "gold").left') == g0 - 2, (g0, ev(pg, 'goals.find(g => g.kind === "gold").left')))
    # the magic feather and the super pounce
    ev(pg, 'T_base(3); render(false); inv.feather = 2; drawTools();')
    ok('feather tool in the bar', ev(pg, "!!document.querySelector('#tools [data-id=feather]')"))
    ev(pg, '(async () => { aim = { kind: "feather" }; await doAim(3, 3); })()'); pg.wait_for_timeout(60); ev(pg, 'T_waitIdle()')
    ok('feather turns a treat into a Flitzekatze', ev(pg, 'grid[3][3].type') == 'cat' and ev(pg, 'inv.feather') == 1, (ev(pg, 'grid[3][3].type'), ev(pg, 'inv.feather')))
    ok('super pounce hits row, column and the 4 corners around', ev(pg, 'aimKeys("pounce", 3, 3).length') == 19, ev(pg, 'aimKeys("pounce", 3, 3).length'))
    ev(pg, 'maxLevel = 90'); ok('no super pounce before level 91', ev(pg, 'aimKeys("pounce", 3, 3).length') == 15)
    print('errors:', errs)
    b.close()
