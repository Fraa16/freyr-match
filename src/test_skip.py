"""the win show cannot be skipped; the boost refund when leaving before the first move"""
import os, sys, time
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
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); veteran.veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    def fresh(ml, extra=''):
        pg.goto('file://' + D + '/' + GAME)
        pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", {ml}); localStorage.setItem("wm-treats", 200); {extra}')
        pg.reload(); pg.wait_for_timeout(600); pg.evaluate(WAIT_MAP)
    def start(L):
        pg.evaluate(f'openLevel({L})'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500)
        pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    # the win show always plays in full: a tap does not cut it short
    fresh(64); start(64)
    pg.evaluate("() => { T_setup(1, [[5,1],[5,2],[6,3]], [[1,1,'nip'],[2,5,'laser'],[0,3,'cat','v']]); T_goalNext(); moves = 13; updateHud(); trySwap(6,3,5,3); }")
    pg.wait_for_function('winRunning === true', timeout=20000, polling=20); pg.wait_for_timeout(2600)
    t0 = time.time(); pg.mouse.click(195, 500); pg.keyboard.press('Space')
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=30000, polling=30)
    dt = time.time() - t0
    ok('a tap does not skip the win show', dt > 3, dt)
    ok('no skip hint on screen', not pg.evaluate('!!document.getElementById("skipHint")'))
    pg.wait_for_timeout(1500); pr = pg.evaluate('T_check()'); ok('board consistent after the show', not pr, pr[:3])
    # leaving before the first move gives back the life and the boost
    fresh(64, 'localStorage.setItem("wm-treats", 100);')
    pg.evaluate('openLevel(64)'); pg.wait_for_timeout(500)
    pg.click('.boost[data-id="laser"]'); pg.wait_for_timeout(200)
    pg.click('#introBtn'); pg.wait_for_timeout(2600)
    t1 = pg.evaluate('treats'); lv1 = pg.evaluate('lives')
    pg.click('#pauseBtn'); pg.wait_for_timeout(400); pg.click('#toMap'); pg.wait_for_timeout(800)
    st = pg.evaluate('({treats, lives, onMap})')
    ok('boost paid then refunded on a free leave', t1 == 88 and st['treats'] == 100 and st['lives'] == lv1 + 1 and st['onMap'], (t1, lv1, st))
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', fails)
