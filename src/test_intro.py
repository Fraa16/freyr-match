"""the intro: Freyr asleep in his bed until a tap, wakes up, meows, walks to level 1, then the level card.
first start, existing players, no lives, replay from his card, stopping half way, sound off, reduced motion."""
import os, sys, time
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
GAME = os.environ.get('GAME', 'game.html')
fails = 0
def ok(name, cond, info=''):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + str(info)), flush=True)
    if not cond: fails += 1
HOOK = """() => { window.__meows = 0; const m0 = meow; meow = function () { const r = m0.apply(this, arguments); window.__meows += r ? 1 : 0; window.__meowTried = (window.__meowTried || 0) + 1; return r; }; }"""
STATE = """() => ({ scene: !!document.getElementById('iScene'), cls: (document.getElementById('iScene') || {}).className || '', intro: document.getElementById('mapScreen').classList.contains('intro'),
  bar: getComputedStyle(document.querySelector('.mapbar')).opacity, tf: document.getElementById('mapInner').style.transform, anim: mapAnimating, run: !!introRun,
  card: document.getElementById('introOv').classList.contains('show'), title: document.getElementById('introTitle').textContent, seen: localStorage.getItem('wm-intro'),
  hint: !document.getElementById('iHint') ? 'gone' : document.getElementById('iHint').hidden ? 'hidden' : 'shown', onMap, L0: mapGeo && mapGeo.L0,
  n1: (document.querySelector('.mnode[data-l="1"]') || {}).className || '', bedHidden: (() => { const b = document.querySelector('#mapInner .mbed'); return b ? b.parentNode.style.visibility === 'hidden' : null; })(),
  freyr: (() => { const f = document.getElementById('mFreyr'); return f ? f.style.visibility : null; })(), chestPill: (() => { const c = document.getElementById('mChest'); return c.hidden ? getComputedStyle(c).display : 'shown'; })() })"""
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    def page(**kw):
        pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True, **kw)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type == 'error' and 'ERR_TUNNEL' not in m.text and 'Failed to load resource' not in m.text and errs.append(m.text))
        return pg, errs
    def fresh(pg, extra=''):
        pg.goto('file://' + D + '/' + GAME); pg.evaluate(f'localStorage.clear(); {extra}'); pg.reload(); pg.wait_for_timeout(500)
    def tap(pg): pg.mouse.click(195, 600)
    card = lambda pg, t=20000: pg.wait_for_function("document.getElementById('introOv').classList.contains('show')", timeout=t, polling=100)

    # I1: a brand-new player
    pg, errs = page(); fresh(pg); pg.evaluate(HOOK)
    pg.wait_for_timeout(400)
    st = pg.evaluate(STATE)
    ok('I1 the intro starts on its own', st['scene'] and st['intro'] and st['run'] and st['anim'], st)
    ok('I1 Freyr asleep, map zoomed in, top bar hidden', 'asleep' in st['cls'] and 'scale(' in st['tf'] and float(st['bar']) < .05, st)
    ok('I1 level 1 still closed, the map bed hidden under the scene, the standing Freyr hidden', 'lock' in st['n1'] and st['bedHidden'] and st['freyr'] == 'hidden', st)
    ok('I1 no empty chest pill in the corner', st['chestPill'] == 'none', st)
    pg.wait_for_timeout(1300); st = pg.evaluate(STATE)
    ok('I1 the hint shows while he sleeps', st['hint'] == 'shown' and 'asleep' in st['cls'], st)
    pg.wait_for_timeout(1500); st = pg.evaluate(STATE)
    ok('I1 he sleeps until someone taps', 'asleep' in st['cls'] and not st['card'], st)
    t0 = time.time(); tap(pg); pg.wait_for_timeout(300); st = pg.evaluate(STATE)
    ok('I1 a tap wakes him', 'asleep' not in st['cls'], st)
    pg.wait_for_function("window.__meowTried > 0", timeout=12000, polling=50)
    ok('I1 his meow plays (from the video)', pg.evaluate('window.__meows') == 1 and pg.evaluate('!!meowBuf'), pg.evaluate('[window.__meows, !!meowBuf]'))
    ok('I1 the speech bubble says Miau', 'Miau' in pg.evaluate("document.getElementById('iBubble').textContent"))
    card(pg); dt = time.time() - t0; st = pg.evaluate(STATE)
    ok('I1 ends with the level 1 card', st['card'] and st['title'] == 'Level 1', st)
    ok('I1 takes 8-14 s from the tap', 8 <= dt <= 14, dt)
    ok('I1 everything back to normal', not st['scene'] and not st['intro'] and st['tf'] == '' and not st['anim'] and not st['run'] and float(st['bar']) > .95, st)
    ok('I1 the intro is remembered', st['seen'] == '1', st)
    fr = pg.evaluate("(() => { const f = document.getElementById('mFreyr'), n = document.querySelector('.mnode[data-l=\"1\"]'); const a = f.getBoundingClientRect(), c = n.getBoundingClientRect(); return [a.left + a.width / 2 - c.left - c.width / 2, f.style.visibility]; })()")
    ok('I1 Freyr stands on level 1', abs(fr[0]) < 2 and fr[1] != 'hidden', fr)
    ok('I1 his bed is on the map, the old name tag is gone', pg.evaluate("!!document.querySelector('#mapInner .mbed') && ![...document.querySelectorAll('#mapInner svg text')].some(t => t.textContent === 'Freyr')"))
    pg.click('#introX'); pg.wait_for_timeout(400)
    pg.reload(); pg.wait_for_timeout(600); st = pg.evaluate(STATE)
    ok('I1 reload: not the intro a second time, he naps by level 1 (V30)', pg.evaluate("introRun && introRun.kind") == 'wake' and 'cur' in st['n1'] and st['onMap'], st)
    ok('I1 no page errors', not errs, errs[:3]); pg.close()

    # I2: someone who already plays (level 37) sees it once too, then is back at their level
    pg, errs = page(); fresh(pg, 'localStorage.setItem("wm-level", 37);')
    st = pg.evaluate(STATE)
    ok('I2 the intro plays on the first map', st['run'] and st['L0'] == 1 and 'lock' in st['n1'], st)
    pg.wait_for_timeout(400); tap(pg); card(pg); pg.wait_for_timeout(300); st = pg.evaluate(STATE)
    ok('I2 then the own level card', st['card'] and st['title'] == 'Level 37' and st['L0'] > 1 and not st['scene'], st)
    ok('I2 no page errors', not errs, errs[:3]); pg.close()

    # I3: no lives left: no card at the end, just the map
    pg, errs = page(); fresh(pg, 'localStorage.setItem("wm-level", 12); localStorage.setItem("wm-lives", 0); localStorage.setItem("wm-life-ts", Date.now());')
    pg.wait_for_timeout(300); tap(pg)
    pg.wait_for_function("!introRun", timeout=20000, polling=100); pg.wait_for_timeout(1200); st = pg.evaluate(STATE)
    ok('I3 no lives: the map, no cards', st['onMap'] and not st['card'] and not pg.evaluate("!!document.querySelector('.overlay.show')") and st['seen'] == '1', st)
    ok('I3 no page errors', not errs, errs[:3]); pg.close()

    # I4: watch it again from Freyr's card
    pg, errs = page(); fresh(pg, 'localStorage.setItem("wm-level", 5); localStorage.setItem("wm-intro", "1");')
    st = pg.evaluate(STATE); ok('I4 seen before: his nap by level 5, not the intro', pg.evaluate("introRun && introRun.kind") == 'wake' and 'lock' not in st['n1'], st)
    pg.evaluate('mapSkip = true'); pg.wait_for_function('!introRun', timeout=6000, polling=50); pg.wait_for_timeout(900)
    pg.click('#mFace'); pg.wait_for_timeout(400)
    ok('I4 the replay button is on his card', pg.is_visible('#setIntro'))
    pg.click('#setIntro'); pg.wait_for_timeout(500); st = pg.evaluate(STATE)
    ok('I4 the intro plays again', st['run'] and st['scene'] and not pg.evaluate("document.getElementById('setOv').classList.contains('show')"), st)
    tap(pg); card(pg); st = pg.evaluate(STATE)
    ok('I4 and ends on the own level', st['title'] == 'Level 5' and not st['scene'], st)
    pg.click('#introBtn'); pg.wait_for_timeout(1500); pg.click('#pauseBtn'); pg.wait_for_timeout(300)
    pg.click('#pCat'); pg.wait_for_timeout(400)
    ok('I4 no replay button inside a level', not pg.is_visible('#setIntro'))
    ok('I4 no page errors', not errs, errs[:3]); pg.close()

    # I5: stopped half way (the level starts while he is walking): nothing stays behind
    pg, errs = page(); fresh(pg)
    pg.wait_for_timeout(300); tap(pg)
    pg.wait_for_function("document.getElementById('iCat') && document.querySelector('#iCat .fsprite.walk')", timeout=15000, polling=50)
    pg.evaluate("openLevel(1)"); pg.wait_for_timeout(300); pg.click('#introBtn'); pg.wait_for_timeout(800)
    st = pg.evaluate(STATE)
    ok('I5 stopped cleanly', not st['run'] and not st['anim'] and st['tf'] == '' and not st['intro'] and not st['onMap'], st)
    pg.wait_for_timeout(2500); st = pg.evaluate(STATE)
    ok('I5 no level card popping up later', not st['card'], st)
    pg.evaluate("showMap()"); pg.wait_for_timeout(500); st = pg.evaluate(STATE)
    ok('I5 the map is normal afterwards', not st['scene'] and st['tf'] == '' and float(st['bar']) > .95, st)
    ok('I5 no page errors', not errs, errs[:3]); pg.close()

    # I6: sound off: no meow sound, everything else the same
    pg, errs = page(); fresh(pg, 'localStorage.setItem("wm-sound", "off");'); pg.evaluate(HOOK)
    pg.wait_for_timeout(300); tap(pg); card(pg); st = pg.evaluate(STATE)
    ok('I6 sound off: silent meow, the card opens', pg.evaluate('window.__meows') == 0 and st['card'] and st['title'] == 'Level 1', [pg.evaluate('window.__meows'), st])
    ok('I6 no page errors', not errs, errs[:3]); pg.close()

    # I7: reduced motion: no zoom, still the whole story
    pg, errs = page(reduced_motion='reduce'); fresh(pg)
    st = pg.evaluate(STATE); ok('I7 reduced motion: no zoom', 'scale(' not in st['tf'] or 'scale(1)' in st['tf'], st)
    pg.wait_for_timeout(300); tap(pg); card(pg, 20000); st = pg.evaluate(STATE)
    ok('I7 reduced motion: ends with the card', st['card'] and st['title'] == 'Level 1' and not st['scene'], st)
    ok('I7 no page errors', not errs, errs[:3]); pg.close()

    # I8: keyboard: Enter wakes him
    pg, errs = page(); fresh(pg)
    pg.wait_for_timeout(1400); pg.keyboard.press('Enter'); pg.wait_for_timeout(300); st = pg.evaluate(STATE)
    ok('I8 Enter wakes him too', 'asleep' not in st['cls'], st)
    pg.close()
    b.close()
print('FAILS', fails)
