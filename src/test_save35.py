"""V35: the progress code. Export on one 'device', import on a fresh one, everything is back; a broken code is refused; test markers stay."""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
GAME = os.environ.get('GAME', 'game.html')
SHOTS = D + '/shots35'; os.makedirs(SHOTS, exist_ok=True)
fails = []
def ok(c, m):
    print(('OK   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

def boot(pg, state):
    pg.goto('file://' + D + '/' + GAME)
    pg.evaluate('(st) => { localStorage.clear(); for (const [k, v] of Object.entries(st)) localStorage.setItem(k, v); }', state)
    pg.reload(); pg.wait_for_timeout(600); fonts(pg)
    pg.evaluate('mapSkip = true')
    pg.wait_for_function('!introRun', timeout=8000)
    pg.wait_for_timeout(900)
    if pg.evaluate("document.getElementById('introOv').classList.contains('show')"): pg.click('#introX'); pg.wait_for_timeout(400)

hearts = {str(L): (3 if L % 4 else 2) for L in range(1, 47)}
A = {'wm-intro': '1', 'wm-level': '47', 'wm-hearts': json.dumps(hearts), 'wm-treats': '83', 'wm-owned': '["bow","hat"]', 'wm-wear': 'hat',
     'wm-purr-told': '1', 'wm-music': 'off', 'wm-learn': json.dumps({'chest': True}), 'wm-chests': '5', 'wm-test-62': '1'}
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    boot(pg, A)
    pg.click('#mFace'); pg.wait_for_timeout(400)
    ok(pg.is_visible('#saveOpen'), 'link in the outfits card')
    pg.screenshot(path=SHOTS + '/outfits.png')
    pg.click('#saveOpen'); pg.wait_for_timeout(400)
    ok(pg.evaluate("document.getElementById('saveOv').classList.contains('show')"), 'save card opens')
    code = pg.input_value('#saveOut')
    ok(code.startswith('WM1-') and len(code) < 3000, 'code looks right, length %d' % len(code))
    pg.screenshot(path=SHOTS + '/save.png')
    pg.click('#saveCopy'); pg.wait_for_timeout(300)
    clip = pg.evaluate('navigator.clipboard.readText()')
    ok(clip == code, 'copied to the clipboard')
    ok('Kopiert' in pg.inner_text('#saveCopy'), 'button says copied')
    dec = pg.evaluate('(c) => readCode(c)', code)
    ok(dec and dec.get('wm-level') == '47' and 'wm-test-62' not in dec, 'code holds the level, not the test marker')

    # a fresh device: level 1, one test marker
    pg2 = ctx.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)))
    boot(pg2, {'wm-intro': '1', 'wm-level': '3', 'wm-purr-told': '1', 'wm-test-62': 'keep'})
    pg2.click('#mFace'); pg2.wait_for_timeout(300); pg2.click('#saveOpen'); pg2.wait_for_timeout(300)
    pg2.fill('#saveIn', 'WM1-kaputt'); pg2.click('#saveLoad'); pg2.wait_for_timeout(200)
    ok('passt nicht' in pg2.inner_text('#saveMsg'), 'broken code refused')
    pg2.fill('#saveIn', '  ' + code[:40] + '\n' + code[40:] + '  '); pg2.click('#saveLoad'); pg2.wait_for_timeout(200)
    ok('Level 3' in pg2.inner_text('#saveMsg') and 'Level 47' in pg2.inner_text('#saveMsg'), 'asks first: ' + pg2.inner_text('#saveMsg'))
    pg2.screenshot(path=SHOTS + '/confirm.png')
    ok(pg2.evaluate("localStorage.getItem('wm-level')") == '3', 'nothing changed before confirming')
    pg2.click('#saveLoad')
    pg2.wait_for_load_state('load'); pg2.wait_for_timeout(1500)
    st = pg2.evaluate("({ L: localStorage.getItem('wm-level'), t: localStorage.getItem('wm-treats'), w: localStorage.getItem('wm-wear'), m: localStorage.getItem('wm-test-62'), h: JSON.parse(localStorage.getItem('wm-hearts') || '{}')['46'] })")
    ok(st['L'] == '47' and st['t'] == '83' and st['w'] == 'hat' and st['h'] == 3, 'progress arrived ' + json.dumps(st))
    ok(st['m'] == 'keep', 'the test marker of this copy stays')
    ok(pg2.evaluate('maxLevel') == 47 and pg2.evaluate('treats') == 83, 'the game runs with it after the reload')
    ok(not errs, 'no errors ' + str(errs[:3]))
    b.close()
print('FAILS', len(fails))
