"""V26: no jump button; a tap on Freyr starts the pounce; the full meter is loud (paw, rays, gold bar, stars, meow); a reminder after two unused moves"""
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
ST = """() => ({ btn: !!document.getElementById('purrGo'), charged: mascot.classList.contains('charged'), aiming: mascot.classList.contains('aiming'),
  paw: !document.querySelector('.mtap').hidden, txt: document.getElementById('purrTxt').textContent, full: document.getElementById('barwrap').classList.contains('full'),
  aim: aim && aim.kind, purr, meows: window.__meows || 0, bubble: document.getElementById('bubble') ? document.getElementById('bubble').textContent : '' })"""
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); veteran.veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/' + GAME); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 12); localStorage.setItem("wm-purr-told", "1")'); pg.reload(); pg.wait_for_timeout(600); pg.evaluate(WAIT_MAP)
    pg.evaluate('openLevel(12)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1600)
    pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    pg.evaluate("() => { window.__meows = 0; const m0 = meow; meow = function () { const r = m0.apply(this, arguments); window.__meows++; return r; }; }")
    st = pg.evaluate(ST)
    ok('P1 the jump button is gone', not st['btn'], st)
    ok('P1 not full: no paw, no glow', not st['charged'] and not st['paw'] and not st['full'], st)
    # the bar takes the row up to the level number at its end (V33: the level sits in this row)
    w = pg.evaluate("(() => { const b = document.getElementById('barwrap').getBoundingClientRect(), r = document.getElementById('purrRow').getBoundingClientRect(), l = document.getElementById('level').parentElement.getBoundingClientRect(); return [b.right, l.left, l.right, r.right]; })()")
    ok('P1 the bar takes the row up to the level number', 0 < w[1] - w[0] < 14 and abs(w[2] - w[3]) < 2, w)
    # tapping Freyr while not full only says how many are missing
    pg.click('#mascot'); pg.wait_for_timeout(200); st = pg.evaluate(ST)
    ok('P2 tap while not full: no aiming, a hint', not st['aim'] and 'Cremesnack' in st['bubble'], st)
    # fill it up
    pg.evaluate("() => { purr = PURR_MAX; purrNew = true; drawPurr(); purrNotice(); }"); pg.wait_for_timeout(250)
    ok('P3 stars fly from the bar to Freyr', pg.evaluate("document.querySelectorAll('.pstar').length") >= 5)
    pg.wait_for_timeout(900); st = pg.evaluate(ST)
    ok('P3 full: glow, paw, gold bar with the hint', st['charged'] and st['paw'] and st['full'] and 'Tipp auf Freyr' in st['txt'], st)
    ok('P3 he meows once when it fills up', st['meows'] == 1, st)
    ok('P3 the stars are cleaned up', pg.evaluate("document.querySelectorAll('.pstar').length") == 0)
    box = pg.evaluate("(() => { const p = document.querySelector('.mtap').getBoundingClientRect(), m = mascot.getBoundingClientRect(); return [p.left, p.top, p.right, p.bottom, m.left, m.top, m.right, m.bottom]; })()")
    ok('P3 the paw sits on Freyr', box[0] < box[6] and box[1] < box[7] and box[2] > box[4] and box[3] > box[5], box)
    # a tap on Freyr: aiming
    pg.click('#mascot'); pg.wait_for_timeout(250); st = pg.evaluate(ST)
    ok('P4 a tap on Freyr starts the jump', st['aim'] == 'pounce' and st['aiming'] and not st['paw'] and 'Feld' in st['txt'], st)
    pg.click('#mascot'); pg.wait_for_timeout(250); st = pg.evaluate(ST)
    ok('P4 a second tap puts it back', not st['aim'] and not st['aiming'] and st['paw'], st)
    pg.click('#mascot'); pg.wait_for_timeout(250)
    cell = pg.evaluate("(() => { for (let r = 2; r < N - 2; r++) for (let c = 2; c < N - 2; c++) if (mask[r][c] && grid[r][c]) return [r, c]; return [3, 3]; })()")
    pg.evaluate(f"doAim({cell[0]}, {cell[1]})"); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(400); st = pg.evaluate(ST)
    ok('P5 the jump happens, the meter is empty again', st['purr'] < 15 and not st['charged'] and not st['paw'] and not st['aiming'], st)
    # reminder: full meter, two moves without using it
    pg.evaluate("() => { window.__rem = 0; const r0 = purrRemind; purrRemind = function () { window.__rem++; return r0.apply(this, arguments); }; purr = PURR_MAX; drawPurr(); }"); pg.wait_for_timeout(200)
    for i in range(2):
        pg.evaluate("() => { moves = Math.max(moves, 10); updateHud(); const m = bestMove(); return trySwap(m.r, m.c, m.r2, m.c2); }"); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(300)
    st = pg.evaluate(ST)
    ok('P6 after two unused moves Freyr reminds you', 'Tipp auf mich' in st['bubble'] and st['purr'] >= 15, st)
    pg.evaluate("() => { const m = bestMove(); return trySwap(m.r, m.c, m.r2, m.c2); }"); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(300)
    ok('P6 only once per full meter', pg.evaluate('window.__rem') == 1, pg.evaluate('window.__rem'))
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', fails)
