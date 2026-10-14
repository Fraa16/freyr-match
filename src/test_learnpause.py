import os, sys, json, time
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
H = open(D + '/harness.js').read()
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
def fresh(pg, L):
    got = {k: True for k, u in [('paw', 16), ('claw', 33), ('swap', 43), ('feather', 97)] if u < L}
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()')
    pg.evaluate(f"localStorage.setItem('wm-level', {L}); localStorage.setItem('wm-tools', '{json.dumps({'inv': {}, 'got': got})}'); localStorage.setItem('wm-learn', JSON.stringify({{chest: true}}))")
    pg.reload(); pg.wait_for_timeout(700); pg.evaluate(WAIT_MAP)
def ctr(pg, sel):
    b = pg.locator(sel).first.bounding_box(); return b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
def cell(pg, k): return pg.evaluate(f"cellXY({k}).slice(0, 2)")
def wait(pg, js, t=15000): pg.wait_for_function(js, timeout=t)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844}); errs = []
    import veteran as _v; _v.seen_intro(pg)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    # 1: pause in the middle of the paw lesson, then carry on
    fresh(pg, 16); pg.evaluate('openLevel(16)'); pg.wait_for_timeout(500); pg.click('#introBtn')
    wait(pg, 'tut && tut.expect && tut.expect.type === "aim"')
    pg.mouse.click(*ctr(pg, '#tools [data-id="paw"] .tbtn'))
    wait(pg, 'tut && tut.expect && tut.expect.type === "turn"')
    x, y = ctr(pg, '#pauseBtn')
    print('pause button on top of the coach:', pg.evaluate(f"document.elementFromPoint({x}, {y}).closest('#pauseBtn') !== null"))
    pg.mouse.click(x, y); pg.wait_for_timeout(400)
    print('pause open:', pg.evaluate("document.getElementById('pauseOv').classList.contains('show')"), 'aim kept:', pg.evaluate('aim && aim.kind'))
    pg.click('#pauseGo'); pg.wait_for_timeout(400)
    k = pg.evaluate('tut.expect.cell'); pg.mouse.click(*cell(pg, k))
    wait(pg, '!tut && !busy')
    print('paw lesson finished after pause:', pg.evaluate('learnt.paw'), '| paw left', pg.evaluate('inv.paw'))
    # 2: leave the level during the cat lesson: it comes back next time
    fresh(pg, 2); pg.evaluate('openLevel(2)'); pg.wait_for_timeout(500); pg.click('#introBtn')
    wait(pg, 'tut && tut.expect && tut.expect.type === "turn"')
    pg.mouse.click(*ctr(pg, '#pauseBtn')); pg.wait_for_timeout(400); pg.click('#toMap'); pg.wait_for_timeout(1200)
    print('left to map:', pg.evaluate('onMap'), 'tut', pg.evaluate('tut'), 'learnt.cat', pg.evaluate('!!learnt.cat'), 'coach hidden', pg.evaluate("document.getElementById('coach').hidden"))
    pg.evaluate(WAIT_MAP); pg.evaluate('openLevel(2)'); pg.wait_for_timeout(500); pg.click('#introBtn')
    wait(pg, 'tut && tut.expect')
    print('lesson again on re-entry:', pg.evaluate('tut.id'))
    # 3: a few wrong taps, then the right move
    st = pg.evaluate('({pair: tut.expect.pair, moves})')
    for xy in [(30, 120), (200, 800), (370, 500)]: pg.mouse.click(*xy); pg.wait_for_timeout(120)
    print('wrong taps changed nothing:', pg.evaluate('moves') == st['moves'] and pg.evaluate('tut && tut.expect && tut.expect.pair.join()') == ','.join(map(str, st['pair'])))
    # the tap-tap way instead of a swipe
    a, c = st['pair']; pg.mouse.click(*cell(pg, a)); pg.wait_for_timeout(150); pg.mouse.click(*cell(pg, c))
    wait(pg, 'tut && tut.expect && tut.expect.pair && tut.expect.pair.join() !== "%s"' % ','.join(map(str, st['pair'])))
    print('tap-tap move accepted; next step pair', pg.evaluate('tut.expect.pair'), 'cat on board', pg.evaluate("countOnBoard(x => x.type === 'cat')"))
    print('errors', errs)
    b.close()
