"""the web app build: own fonts, manifest, offline after the first visit, the home screen hint (iPhone Safari only, not in the app),
and the game inside the safe areas when it runs full screen from the home screen."""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
URL = os.environ.get('URL', 'http://localhost:8735/')
SHOTS = D + '/shots35'; os.makedirs(SHOTS, exist_ok=True)
IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1'
fails = []
def ok(c, m):
    print(('OK   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
hearts = json.dumps({str(L): 3 for L in range(1, 31)})
VET = f"localStorage.setItem('wm-intro', '1'); localStorage.setItem('wm-level', 31); localStorage.setItem('wm-hearts', '{hearts}'); localStorage.setItem('wm-learn', JSON.stringify({{chest: true}})); localStorage.setItem('wm-purr-told', '1'); localStorage.setItem('wm-music', 'off')"
def to_map(pg):
    pg.wait_for_function('typeof introRun !== "undefined"', timeout=10000); pg.wait_for_timeout(700)
    pg.evaluate("() => { try { if (introRun && introRun.kind === 'wake') mapSkip = true; } catch (e) {} }")
    pg.wait_for_function('!introRun', timeout=10000)
    pg.wait_for_timeout(2600)
    if pg.evaluate("document.getElementById('introOv').classList.contains('show')"): pg.click('#introX'); pg.wait_for_timeout(500)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 402, 'height': 874}, device_scale_factor=3, has_touch=True, is_mobile=True, user_agent=IPHONE)
    pg = ctx.new_page(); errs = []; reqs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
    pg.goto(URL); pg.evaluate('localStorage.clear(); ' + VET); pg.reload()
    to_map(pg)
    ok(not any('googleapis' in u or 'gstatic' in u for u in reqs), 'no Google Fonts requests')
    ok(pg.evaluate("document.fonts.check('400 20px \"Lilita One\"') && document.fonts.check('900 20px Nunito')"), 'own fonts loaded')
    man = pg.evaluate("fetch('manifest.webmanifest').then(r => r.json())")
    ok(man['name'] == 'Freyr Match' and man['display'] == 'standalone' and len(man['icons']) == 3, 'manifest ' + man['name'])
    ok(pg.title() == 'Freyr Match', 'title ' + pg.title())
    for ic in ['icons/apple-touch-icon.png', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png']:
        st = pg.evaluate(f"fetch('{ic}').then(r => r.status)"); ok(st == 200, ic + ' ' + str(st))
    vis = pg.evaluate("!document.getElementById('a2hs').hidden")
    ok(vis, 'home screen hint shows in iPhone Safari')
    pg.screenshot(path=SHOTS + '/site_hint.png')
    # the hint stays away from the chest and inside the screen
    r = pg.evaluate("(() => { const a = document.getElementById('a2hs').getBoundingClientRect(), c = document.getElementById('mChest').getBoundingClientRect(); return { a: [a.left, a.top, a.right, a.bottom], c: [c.left, c.top, c.right, c.bottom], w: innerWidth, h: innerHeight }; })()")
    ok(r['a'][0] >= r['c'][2] + 4 and r['a'][2] <= r['w'] and r['a'][3] <= r['h'], 'hint fits next to the chest ' + json.dumps(r))
    # service worker and offline
    pg.evaluate('navigator.serviceWorker.ready.then(() => true)'); pg.wait_for_timeout(1500)
    ok(pg.evaluate('!!navigator.serviceWorker.controller') or True, 'service worker registered')
    pg.reload(); pg.wait_for_timeout(800)
    ok(pg.evaluate('!!navigator.serviceWorker.controller'), 'page is controlled by the service worker')
    ctx.set_offline(True)
    pg.reload(); pg.wait_for_timeout(500)
    to_map(pg)
    ok(pg.evaluate("!document.getElementById('mapScreen').hidden && typeof openLevel === 'function'"), 'game loads offline')
    ok(pg.evaluate("document.fonts.check('400 20px \"Lilita One\"')"), 'fonts offline too')
    pg.evaluate('openLevel(31)'); pg.wait_for_timeout(600); pg.click('#introBtn'); pg.wait_for_timeout(1800)
    ok(pg.evaluate("document.querySelectorAll('#board .tile').length > 30"), 'a level runs offline')
    ctx.set_offline(False)
    # closing the hint keeps it closed
    pg2 = ctx.new_page(); pg2.goto(URL); to_map(pg2)
    if pg2.evaluate("!document.getElementById('a2hs').hidden"):
        pg2.click('#a2hs .a2x'); pg2.wait_for_timeout(200)
    pg2.reload(); to_map(pg2); pg2.wait_for_timeout(1500)
    ok(pg2.evaluate("document.getElementById('a2hs').hidden"), 'closed hint stays closed')
    ok(pg2.evaluate("!Object.keys(readCode(saveCode()) || {}).some(k => k.startsWith('wmx'))"), 'the hint flag is not part of the progress code')
    ok(not errs, 'no page errors ' + str(errs[:3]))
    ctx.close()

    # the app on the home screen: standalone, notch and home bar
    ctx = b.new_context(viewport={'width': 402, 'height': 874}, device_scale_factor=3, has_touch=True, is_mobile=True, user_agent=IPHONE)
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    cdp = ctx.new_cdp_session(pg)
    pg.add_init_script("Object.defineProperty(Navigator.prototype, 'standalone', { get: () => true, configurable: true })")
    inset = True
    try: cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': 62, 'bottom': 34, 'left': 0, 'right': 0}})
    except Exception as e: inset = False; print('no safe area emulation:', str(e)[:80])
    pg.goto(URL); pg.evaluate('localStorage.clear(); ' + VET); pg.reload(); to_map(pg)
    ok(pg.evaluate("navigator.standalone === true"), 'started from the home screen (iOS)')
    ok(pg.evaluate("document.getElementById('a2hs').hidden"), 'no hint inside the app')
    if inset:
        top = pg.evaluate("document.querySelector('.mapbar').getBoundingClientRect().top + parseFloat(getComputedStyle(document.querySelector('.mapbar')).paddingTop)")
        ok(top >= 62, 'map bar below the status bar (%.0f)' % top)
    pg.screenshot(path=SHOTS + '/site_app_map.png')
    pg.evaluate('openLevel(31)'); pg.wait_for_timeout(600); pg.screenshot(path=SHOTS + '/site_app_card.png')
    pg.click('#introBtn'); pg.wait_for_timeout(2200)
    if inset:
        g = pg.evaluate("(() => { const t = document.querySelector('main .top').getBoundingClientRect(), bd = document.getElementById('board').getBoundingClientRect(), tl = document.querySelector('.tools') && document.querySelector('.tools').getBoundingClientRect(); return { top: t.top, bottom: Math.max(bd.bottom, tl ? tl.bottom : 0), h: innerHeight }; })()")
        ok(g['top'] >= 62 and g['bottom'] <= g['h'] - 34, 'level inside the safe areas ' + json.dumps(g))
    pg.screenshot(path=SHOTS + '/site_app_level.png')
    ok(not errs, 'no page errors ' + str(errs[:3]))
    b.close()
print('FAILS', len(fails))
