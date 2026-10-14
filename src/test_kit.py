"""level 61: the Trabzon level, winning it unlocks the jersey, Freyr can wear it"""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
H = open(D + '/harness.js').read()
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
OUT = D + '/kit_'
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    import veteran as _v; _v.seen_intro(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()')
    learn = {k: True for k in ['basics', 'cat', 'laser', 'milk', 'nip', 'boxes', 'bowl', 'chest']}
    pg.evaluate(f"localStorage.setItem('wm-level', 61); localStorage.setItem('wm-treats', 120); localStorage.setItem('wm-learn', '{json.dumps(learn)}')")
    pg.reload(); pg.wait_for_timeout(800); fonts(pg); pg.evaluate(WAIT_MAP); pg.wait_for_timeout(300)
    pg.evaluate('openLevel(61)'); pg.wait_for_timeout(700); pg.screenshot(path=OUT + 'card.png')
    print('card:', pg.evaluate("document.getElementById('introNew').innerText.replace(/\\n/g, ' | ')"), '| world:', pg.evaluate("document.getElementById('introWorld').textContent"))
    print('goal text:', pg.evaluate('goals.map(g => goalText(g, remaining(g))).join()'))
    pg.click('#introBtn'); pg.wait_for_function('busy || !!tut', timeout=5000); pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(500)
    pg.screenshot(path=OUT + 'board.png')
    # win it: three fish make the last of the 61
    pg.evaluate("() => { goals[0].left = 3; updateHud(); T_setup(0, [[3,1],[3,2],[4,3]]); }")
    pg.evaluate('(async () => { await trySwap(4, 3, 3, 3); })()')
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=60000); pg.wait_for_timeout(1200)
    pg.screenshot(path=OUT + 'win.png')
    print('owned after win:', pg.evaluate('owned'), 'kitNew', pg.evaluate('kitNew'))
    pg.click('#endBtn')
    pg.wait_for_function('document.getElementById("kitOv").classList.contains("show")', timeout=30000); pg.wait_for_timeout(900)
    pg.screenshot(path=OUT + 'reveal.png')
    pg.click('#kitWear'); pg.wait_for_timeout(600)
    print('wearing:', pg.evaluate('wear'), '| saved:', pg.evaluate("localStorage.getItem('wm-wear')"))
    pg.evaluate(WAIT_MAP); pg.wait_for_timeout(1500)
    if pg.evaluate("document.getElementById('introOv').classList.contains('show')"): pg.screenshot(path=OUT + 'next.png'); pg.click('#introX'); pg.wait_for_timeout(500)
    pg.evaluate('scrollMapTo(maxLevel, .5)'); pg.wait_for_timeout(400); pg.screenshot(path=OUT + 'map.png')
    pg.evaluate('openSettings()'); pg.wait_for_timeout(400); pg.screenshot(path=OUT + 'outfits.png')
    print('outfits:', pg.evaluate("[...document.querySelectorAll('.outfit')].map(b => b.dataset.id + ':' + b.querySelector('small').textContent + (b.disabled ? ':disabled' : ''))"))
    # a fresh player does not see the jersey at all (it is a surprise)
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(700)
    pg.evaluate('openSettings()'); pg.wait_for_timeout(300)
    print('fresh outfits:', pg.evaluate("[...document.querySelectorAll('.outfit')].map(b => b.dataset.id + ':' + b.querySelector('small').textContent + (b.disabled ? ':disabled' : ''))"))
    print('errors:', errs)
    b.close()
