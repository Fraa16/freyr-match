import os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    for (w, h) in [(320, 568), (375, 667)]:
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2); errs = []; __import__('veteran').veteran(pg)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 18); localStorage.setItem("wm-treats", 80)'); pg.reload(); pg.wait_for_timeout(1200)
        pg.screenshot(path=D + f'/sm_map_{w}.png')
        pg.evaluate('openLevel(maxLevel)'); pg.wait_for_timeout(800); pg.screenshot(path=D + f'/sm_intro_{w}.png')
        pg.click('#introBtn'); pg.wait_for_timeout(1300); pg.screenshot(path=D + f'/sm_game_{w}.png')
        over = pg.evaluate('''() => { const out = []; for (const e of document.querySelectorAll('main *')) { const r = e.getBoundingClientRect(); if (r.right > innerWidth + 1 && r.width > 0) out.push((e.id || e.className.baseVal || e.className) + ':' + Math.round(r.right)); } return [document.documentElement.scrollWidth, out.slice(0, 6)]; }''')
        print(w, h, 'overflow', over, 'intro fits', pg.evaluate('(() => { const c = document.getElementById("introCard").getBoundingClientRect(); return [Math.round(c.top), Math.round(c.bottom)]; })()'), errs)
        pg.close()
    b.close()
