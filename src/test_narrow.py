import os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 320, 'height': 568}, device_scale_factor=2); errs = []; __import__('veteran').veteran(pg)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/' + (__import__('sys').argv[1] if len(__import__('sys').argv) > 1 else 'game.html')); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 9); localStorage.setItem("wm-lives", 3); localStorage.setItem("wm-life-ts", Date.now() - 600000); localStorage.setItem("wm-treats", 128)'); pg.reload(); pg.wait_for_timeout(900)
    pg.screenshot(path=D + '/nar_map.png')
    print('bar overflow:', pg.evaluate('(() => { const b = document.querySelector(".mapbar"); return [b.scrollWidth, b.clientWidth]; })()'), 'page x-scroll', pg.evaluate('document.documentElement.scrollWidth'))
    pg.click('.mnode.cur'); pg.wait_for_timeout(600); pg.screenshot(path=D + '/nar_intro.png')
    pg.click('#introBtn'); pg.wait_for_timeout(1200); pg.screenshot(path=D + '/nar_game.png')
    print('in game: onMap', pg.evaluate('onMap'), 'tiles', pg.evaluate('document.querySelectorAll("#board .tile").length'), 'lives', pg.evaluate('lives'))
    print('errors', errs)
    b.close()
