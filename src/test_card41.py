"""V41 fix: the level card after a level was played (the extras are pictures by then): the shop and the legend show
the extras at their normal size, the card fits the screen."""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
GAME = os.environ.get('GAME', 'game.html')
fails = []
def ok(m, c, info=None):
    print(('OK   ' if c else 'FAIL ') + m + ('' if c or info is None else '  ' + json.dumps(info)[:400]))
    if not c: fails.append(m)
CHECK = """() => { const card = $('introCard').getBoundingClientRect(), imgs = [...document.querySelectorAll('#introOv img')].map(i => { const r = i.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; });
  return { card: [Math.round(card.left), Math.round(card.right), Math.round(card.width)], vw: innerWidth, imgs, boosts: !$('boostWrap').hidden, xbm: XBM.size }; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for treats, name in [(426, 'shop'), (0, 'legend')]:
        pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=3, has_touch=True, is_mobile=True)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + D + '/' + GAME)
        pg.evaluate("(t) => { localStorage.clear(); localStorage.setItem('wm-intro','1'); localStorage.setItem('wm-news41','done'); localStorage.setItem('wm-level','42'); localStorage.setItem('wm-treats', String(t)); localStorage.setItem('wm-purr-told','1'); localStorage.setItem('wm-music','off'); localStorage.setItem('wm-learn', JSON.stringify({basics:1,cat:1,laser:1,nip:1,bowl:1,combo:1,purr:1,chest:1,boosts:1,bells:1,milk:1,boxes:1,locks:1,paw:1,box2:1,gold:1,milk2:1,hard:1,hard2:1,claw:1,blanket:1,swap:1,wet:1,boss:1,streak:1,picnic:1})); }", treats)
        pg.reload(); pg.wait_for_timeout(800); fonts(pg)
        pg.evaluate("() => { try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1500)
        pg.evaluate("() => { document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); openLevel(42); }"); pg.wait_for_timeout(600)
        pg.click('#introBtn'); pg.wait_for_timeout(2500)   # the level runs: the extras become pictures
        pg.evaluate("() => { $('toMap').click(); }"); pg.wait_for_timeout(1200)
        pg.evaluate("() => { document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); openLevel(42); }"); pg.wait_for_timeout(900)
        r = pg.evaluate(CHECK)
        pg.screenshot(path=D + '/shots41/card-' + name + '.png')
        print('  ', name, r)
        ok(name + ': the card fits the screen', r['card'][0] >= 0 and r['card'][1] <= r['vw'], r)
        ok(name + ': no picture bigger than 90 px on the card', all(w <= 90 and h <= 90 for w, h in r['imgs']), r['imgs'])
        ok(name + ': no page errors', not errs, errs[:2])
        pg.close()
    b.close()
print('FAILS', len(fails))
