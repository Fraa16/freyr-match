import os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}); errs = []; __import__('veteran').veteran(pg)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(600)
    pg.evaluate("async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); if (!document.getElementById('introOv').classList.contains('show')) openLevel(maxLevel); }"); pg.wait_for_timeout(500)
    pg.click('#introBtn'); pg.wait_for_timeout(3000)
    print('t=3s', pg.evaluate('[actx.state, mStep, +(mNext - actx.currentTime).toFixed(3), musicBus.gain.value.toFixed(3)]'))
    for jump, w in [(16 * 12 - 6, 0), (23 * 12 + 2, 0), (39 * 12 + 8, 0), (0, 3), (24 * 12, 2), (16 * 12, 1)]:
        pg.evaluate('([j, w]) => { setMusicWorld(w); mStep = j; }', [jump, w]); pg.wait_for_timeout(2500)
        print('world', w, 'from tick', jump, '->', pg.evaluate('[mStep, +(mNext - actx.currentTime).toFixed(3), mBass]'))
    print('errors:', errs)
    b.close()
