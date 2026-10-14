import os, sys
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
H = open(D + '/harness.js').read()
LV = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else ','.join(str(i) for i in range(1, 21))).split(',')]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=1); __import__('veteran').veteran(pg)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    for L in LV:
        pg.goto('file://' + D + '/game.html'); pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", "{L}")'); pg.reload(); pg.wait_for_timeout(700)
        pg.screenshot(path=D + f'/lv_intro_{L}.png')
        pg.evaluate("""async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); if (!document.getElementById('introOv').classList.contains('show')) openLevel(maxLevel); }"""); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(900)
        pg.add_script_tag(content=H)
        pg.screenshot(path=D + f'/lv_{L}.png')
        print(L, pg.evaluate('cfg.name'), pg.evaluate('JSON.stringify(goals.map(g => g.kind + ":" + remaining(g)))'), 'check', pg.evaluate('T_check()')[:3], 'moves avail', pg.evaluate('hasMove()'))
    print('errors:', errs[:5])
    b.close()
