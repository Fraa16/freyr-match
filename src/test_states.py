import os, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
H = open(D + '/harness.js').read()
def fresh(pg, setup):
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()'); pg.evaluate(setup); pg.reload(); pg.wait_for_timeout(900)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []; __import__('veteran').veteran(pg)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    # 1 new game
    fresh(pg, '1')
    pg.screenshot(path=D + '/st_new.png')
    # 2 locked tap -> toast
    pg.click('.mnode[data-l="3"]'); pg.wait_for_timeout(400); pg.screenshot(path=D + '/st_toast.png')
    print('toast:', pg.evaluate('document.getElementById("mToast").textContent'))
    # 3 intro over map
    pg.click('.mnode.cur'); pg.wait_for_timeout(700); pg.screenshot(path=D + '/st_intro.png')
    pg.click('#introX'); pg.wait_for_timeout(300)
    print('after X: intro', pg.evaluate('document.getElementById("introOv").classList.contains("show")'), 'onMap', pg.evaluate('onMap'), 'lives', pg.evaluate('lives'))
    # 4 lives clock math
    fresh(pg, 'localStorage.setItem("wm-level", 4); localStorage.setItem("wm-lives", 2); localStorage.setItem("wm-life-ts", Date.now() - 26 * 60000)')
    print('2 lives + 26 min ->', pg.evaluate('[lives, document.getElementById("mLivesT").textContent]'))
    fresh(pg, 'localStorage.setItem("wm-level", 4); localStorage.setItem("wm-lives", 2); localStorage.setItem("wm-life-ts", Date.now() - 80 * 60000)')
    print('2 lives + 80 min ->', pg.evaluate('[lives, document.getElementById("mLivesT").textContent, lifeTs]'))
    fresh(pg, 'localStorage.setItem("wm-level", 4); localStorage.setItem("wm-lives", 0); localStorage.setItem("wm-life-ts", Date.now() - 60000)')
    print('0 lives ->', pg.evaluate('[lives, document.getElementById("mLivesT").textContent]'))
    pg.screenshot(path=D + '/st_zero_map.png')
    pg.click('.mnode.cur'); pg.wait_for_timeout(600); pg.screenshot(path=D + '/st_nolives.png')
    print('nolives shown', pg.evaluate('document.getElementById("livesOv").classList.contains("show")'), pg.evaluate('document.getElementById("livesClock").textContent'))
    # a life comes back while the card is open
    pg.evaluate('lifeTs = Date.now() - LIFE_MS - 10; saveLives();'); pg.wait_for_timeout(1300)
    print('after refill:', pg.evaluate('[lives, document.getElementById("livesTitle").textContent, document.getElementById("livesBtn").textContent]'))
    pg.screenshot(path=D + '/st_back.png')
    pg.click('#livesBtn'); pg.wait_for_timeout(600)
    print('intro after Weiterspielen', pg.evaluate('document.getElementById("introOv").classList.contains("show")'), 'level', pg.evaluate('level'))
    # 5 loss card
    fresh(pg, 'localStorage.setItem("wm-level", 3); localStorage.setItem("wm-lives", 3); localStorage.setItem("wm-life-ts", Date.now() - 5 * 60000)')
    pg.click('.mnode.cur'); pg.wait_for_timeout(600); pg.click('#introBtn'); pg.wait_for_timeout(600)
    print('after Los lives', pg.evaluate('lives'))
    pg.add_script_tag(content=H)
    pg.evaluate('() => { moves = 0; showEnd(false); }'); pg.wait_for_timeout(900)
    pg.screenshot(path=D + '/st_loss.png')
    print('loss: lifeline', pg.evaluate('document.getElementById("endLives").textContent'), '| btn', pg.evaluate('document.getElementById("endBtn").textContent'), '| map btn hidden', pg.evaluate('document.getElementById("endMap").hidden'))
    pg.click('#endBtn'); pg.wait_for_timeout(700)
    print('Nochmal -> onMap', pg.evaluate('onMap'), 'intro', pg.evaluate('document.getElementById("introOv").classList.contains("show")'))
    # 6 quit confirm
    pg.click('#introBtn'); pg.wait_for_timeout(500)
    pg.evaluate('() => { moves = cfg.moves - 1; }')
    pg.click('#pauseBtn'); pg.wait_for_timeout(300); pg.click('#toMap'); pg.wait_for_timeout(500); pg.screenshot(path=D + '/st_quit.png')
    pg.click('#quitGo'); pg.wait_for_timeout(500)
    print('quit -> onMap', pg.evaluate('onMap'), 'lives', pg.evaluate('lives'))
    # free quit before any move
    pg.click('.mnode.cur'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(500)
    l1 = pg.evaluate('lives'); pg.click('#pauseBtn'); pg.wait_for_timeout(300); pg.click('#toMap'); pg.wait_for_timeout(400)
    print('free quit: lives during', l1, 'after', pg.evaluate('lives'), 'onMap', pg.evaluate('onMap'))
    # 7 dark mode map top bar
    pg.emulate_media(color_scheme='dark'); pg.wait_for_timeout(300); pg.screenshot(path=D + '/st_dark.png'); pg.emulate_media(color_scheme='light')
    # 8 far progress
    fresh(pg, 'localStorage.setItem("wm-level", 18)')
    pg.screenshot(path=D + '/st_l18.png')
    fresh(pg, 'localStorage.setItem("wm-level", 23)')
    print('level 23 range', pg.evaluate('[mapGeo.L0, mapGeo.L1, mapGeo.H]'))
    pg.screenshot(path=D + '/st_l23.png')
    print('errors:', errs)
    b.close()
