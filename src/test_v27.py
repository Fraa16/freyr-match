"""V27: the Schnurr-Power is kept across levels, leftover moves after the zoomies become extras that go off,
the feast bowl also eats what is round it, two bowls give a second helping, the new effects leave nothing behind"""
import os, sys
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import veteran
GAME = os.environ.get('GAME', 'game.html')
H = open(D + '/harness.js').read()
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
fails = 0
def ok(name, cond, info=''):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + str(info)), flush=True)
    if not cond: fails += 1
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); veteran.veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    def fresh(ml, extra=''):
        pg.goto('file://' + D + '/' + GAME)
        pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", {ml}); localStorage.setItem("wm-treats", 200); localStorage.setItem("wm-purr-told", "1"); {extra}')
        pg.reload(); pg.wait_for_timeout(600); pg.evaluate(WAIT_MAP)
    def start(L):
        pg.evaluate(f'openLevel({L})'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500)
        pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')

    # V1: the meter carries over: reload, next level, a lost level; only a jump empties it
    fresh(20, 'localStorage.setItem("wm-purr", 37);')
    ok('V1 the meter is loaded', pg.evaluate('purr') == 37, pg.evaluate('purr'))
    ok('V1 it fills slowly now', pg.evaluate('PURR_MAX') >= 40, pg.evaluate('PURR_MAX'))
    start(20)
    ok('V1 a new level keeps it', pg.evaluate('purr') >= 37, pg.evaluate('purr'))
    ok('V1 the bar shows it', pg.evaluate("document.getElementById('purrTxt').textContent").startswith(str(pg.evaluate('purr'))), pg.evaluate("document.getElementById('purrTxt').textContent"))
    pg.evaluate("() => { moves = 1; updateHud(); const m = bestMove(); trySwap(m.r, m.c, m.r2, m.c2); }")
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=30000); pg.wait_for_timeout(500)
    kept = pg.evaluate('purr')
    ok('V1 losing keeps it', kept >= 37, kept)
    pg.reload(); pg.wait_for_timeout(600); pg.evaluate(WAIT_MAP)
    ok('V1 a reload keeps it', pg.evaluate('purr') == kept, (pg.evaluate('purr'), kept))
    # V2: a full meter: the level card says so; jumping empties it
    pg.evaluate('() => { purr = PURR_MAX; drawPurr(); }')
    pg.evaluate('openLevel(20)'); pg.wait_for_timeout(500)
    ok('V2 the level card says the meter is full', pg.evaluate("!document.getElementById('introPurr').hidden && document.getElementById('introPurr').textContent.includes('Schnurr-Power')"))
    pg.click('#introBtn'); pg.wait_for_timeout(1500); pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    ok('V2 the level starts full', pg.evaluate('purr >= PURR_MAX && mascot.classList.contains("charged")'))
    pg.click('#mascot'); pg.wait_for_timeout(300)
    pg.evaluate('doAim(3, 3)'); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(300)
    ok('V2 a jump empties it (only what the jump ate is back in)', pg.evaluate('purr') < 15, pg.evaluate('purr'))
    pg.evaluate('openLevel(21)') if False else None

    # V3: the end of a level with 20 moves left: 12 sprints, the other 8 become extras and go off
    fresh(64); start(64)
    pg.evaluate("() => { window.__rain = 0; const s0 = spawnFx; spawnFx = function () { window.__rain++; return s0.apply(this, arguments); }; }")
    pg.evaluate("() => { T_setup(1, [[5,1],[5,2],[6,3]]); T_goalNext(); moves = 21; updateHud(); trySwap(6,3,5,3); }")
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=60000); pg.wait_for_timeout(400)
    st = pg.evaluate("({ moves, rain: window.__rain, bonus: lastBonus, text: document.getElementById('endBonus') ? document.getElementById('endBonus').textContent : '' })")
    ok('V3 leftover moves became extras', st['rain'] >= 8 and st['moves'] == 0, st)
    ok('V3 and they paid off', st['bonus'] > 8 * 100, st)
    pr = pg.evaluate('T_check()'); ok('V3 board consistent after the show', not pr, pr[:3] if pr else pr)

    # V4: the bowl eats its kind and everything round it (level 1 has a plain board and no robot; everything is unlocked)
    fresh(150); start(1)
    pg.evaluate('T_base(2); moves = 30; goals = [{kind: "collect", type: 5, n: 99, left: 99}]; updateHud(); render(false)')
    pg.evaluate("() => { grid[4][3] = mk('bowl'); grid[4][4] = mk(0); for (const [r, c] of [[3,2],[3,3],[3,4],[4,2],[5,2],[5,3],[5,4]]) grid[r][c] = mk(2); render(false); }")
    ids = pg.evaluate("[[3,2],[3,3],[3,4],[4,2],[5,2],[5,3],[5,4]].map(([r, c]) => grid[r][c].id)")
    pg.evaluate("() => { window.__d = false; trySwap(4, 3, 4, 4).then(() => window.__d = true); }")
    pg.wait_for_function('window.__d === true', timeout=30000); pg.evaluate('T_waitIdle()')
    left = pg.evaluate(f"(() => {{ const ids = new Set({ids}); let n = 0; for (const row of grid) for (const x of row) if (x && ids.has(x.id)) n++; return n; }})()")
    ok('V4 the bowl ate the paws round it too', left == 0, left)
    # V5: two bowls: everything, then a second helping
    pg.evaluate('T_base(2); moves = 30; goals = [{kind: "collect", type: 5, n: 999, left: 999}]; updateHud(); render(false)')
    pg.evaluate("() => { window.__n = 0; const n0 = nachschlag; nachschlag = function () { window.__n++; return n0.apply(this, arguments); }; grid[4][3] = mk('bowl'); grid[4][4] = mk('bowl'); render(false); }")
    s0 = pg.evaluate('score')
    pg.evaluate("() => { window.__d = false; trySwap(4, 3, 4, 4).then(() => window.__d = true); }")
    pg.wait_for_function('window.__d === true', timeout=40000); pg.evaluate('T_waitIdle()')
    st = pg.evaluate("({ n: window.__n, gained: score - %d, eaten: 999 - goals[0].left })" % s0)
    ok('V5 two bowls: a second helping', st['n'] == 1 and st['eaten'] >= 12, st)
    pr = pg.evaluate('T_check()'); ok('V5 board consistent', not pr, pr[:3] if pr else pr)
    # V6 (V28): one effects canvas, sized to the screen at its own resolution, and it empties itself
    pg.wait_for_timeout(1500)
    st = pg.evaluate("({ glow: !!document.getElementById('glowfx'), w: fx.width, cw: innerWidth, fxs: FXS, vfx: vfx.length, lights: lights.length, parts: parts.length })")
    ok('V6 one effects canvas at its resolution', not st['glow'] and abs(st['w'] - round(st['cw'] * st['fxs'])) <= 1 and st['fxs'] >= 1, st)
    ok('V6 nothing left running after the effects', st['vfx'] == 0 and st['lights'] == 0 and st['parts'] == 0, st)
    # V7: the first full meter after the update says once that it can be saved for the next level
    fresh(30); start(30)
    BUB = "document.getElementById('bubble') ? document.getElementById('bubble').textContent : ''"
    pg.evaluate("() => { purr = PURR_MAX; purrNew = true; drawPurr(); purrNotice(); }"); pg.wait_for_timeout(300)
    b1 = pg.evaluate(BUB)
    ok('V7 first full meter: Freyr says it can be saved', 'heb sie dir auf' in b1, b1)
    pg.evaluate("() => { purr = 0; drawPurr(); purr = PURR_MAX; purrNew = true; drawPurr(); purrNotice(); }"); pg.wait_for_timeout(300)
    b2 = pg.evaluate(BUB)
    ok('V7 only once', 'heb sie dir auf' not in b2, b2)
    ok('V7 the lesson card explains it', 'nächste Level' in pg.evaluate('INTRO.purr()[2]') and 'rund um den Napf' in pg.evaluate('INTRO.bowl()[2]'))
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', fails)
