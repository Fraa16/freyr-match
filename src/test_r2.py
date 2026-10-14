import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from fontfix import fonts
H = open(D + '/harness.js').read()
OUT = D + '/r2_'
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
def fresh(pg, setup='1'):
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()'); pg.evaluate(setup); pg.reload(); pg.wait_for_timeout(900); fonts(pg)
def open_level(pg, L=None):
    pg.evaluate(WAIT_MAP)
    pg.evaluate(f"() => {{ if (!document.getElementById('introOv').classList.contains('show')) openLevel({L or 'maxLevel'}); }}"); pg.wait_for_timeout(700)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); __import__('veteran').veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    hearts = json.dumps({str(L): 3 if L % 4 else 2 for L in range(1, 40)})
    fresh(pg, f"localStorage.setItem('wm-level', 40); localStorage.setItem('wm-hearts', '{hearts}'); localStorage.setItem('wm-chests', 3); localStorage.setItem('wm-treats', 30)")
    pg.evaluate(WAIT_MAP); pg.wait_for_timeout(300); pg.screenshot(path=OUT + 'map25.png')
    print('chest ready', pg.evaluate('chestsReady()'), 'hearts', pg.evaluate('heartSum()'), 'loop L61 =', pg.evaluate('levelConfig(61).name'), pg.evaluate('levelConfig(61).boss'), pg.evaluate('levelConfig(65).boss'))
    pg.click('#mChest', force=True); pg.wait_for_timeout(700); pg.screenshot(path=OUT + 'chest_closed.png')
    pg.click('#chestBtn'); pg.wait_for_timeout(1300); pg.screenshot(path=OUT + 'chest_open.png')
    print('after chest: treats', pg.evaluate('treats'), 'inv', pg.evaluate('JSON.stringify(inv)'), 'opened', pg.evaluate('chestsOpened'), 'ready', pg.evaluate('chestsReady()'))
    pg.click('#chestBtn'); pg.wait_for_timeout(500)
    print('chest closed:', not pg.evaluate("document.getElementById('chestOv').classList.contains('show')"), 'button', pg.evaluate("document.getElementById('mChest').textContent"))
    open_level(pg, 40); pg.screenshot(path=OUT + 'intro25.png')
    pg.add_script_tag(content=H)
    pg.click('#introBtn'); pg.wait_for_timeout(600); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(500)
    pg.screenshot(path=OUT + 'game25.png')
    print('boss', pg.evaluate('JSON.stringify({r: boss.r, c: boss.c, hp: boss.hp, dir: boss.dir})'), 'goals', pg.evaluate('JSON.stringify(goals)'))
    for i in range(6):
        pg.evaluate('(async () => { const m = bestMove(); await trySwap(m.r, m.c, m.r2, m.c2); })()'); pg.evaluate('T_waitIdle()')
        print(' move', i, pg.evaluate('JSON.stringify({r: boss.r, c: boss.c, hp: boss.hp, dir: boss.dir, moves})'), pg.evaluate('T_check()')[:3])
        if i == 2: pg.screenshot(path=OUT + 'game25_mid.png')
    # a pounce right through the robot
    pg.evaluate('() => { purr = PURR_MAX; updateHud(); }')
    hp0 = pg.evaluate('boss.hp')
    pg.evaluate('(async () => { aim = { kind: "pounce" }; await doAim(boss.r, boss.c + 1); })()'); pg.evaluate('T_waitIdle()')
    print('pounce on robot: hp', hp0, '->', pg.evaluate('boss.hp'), pg.evaluate('T_check()')[:3])
    # finish it
    pg.evaluate('() => { boss.hp = 1; drawBoss(); }')
    pg.evaluate('(async () => { aim = { kind: "pounce" }; purr = PURR_MAX; await doAim(boss.r, boss.c); })()'); pg.wait_for_timeout(450); pg.screenshot(path=OUT + 'boom.png')
    pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(300)
    print('after finishing: hp', pg.evaluate('boss.hp'), 'robot el', pg.evaluate('!!document.querySelector(".vac")'), 'remaining', pg.evaluate('goals.map(remaining)'), 'end shown', pg.evaluate("document.getElementById('endOv').classList.contains('show')"), pg.evaluate('T_check()')[:3])
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=40000); pg.wait_for_timeout(2500)
    pg.screenshot(path=OUT + 'win25.png')
    print('heart line:', pg.evaluate("document.getElementById('heartTotal').textContent"))
    print('errors:', errs)
    b.close()
