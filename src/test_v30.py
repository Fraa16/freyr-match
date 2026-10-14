"""V30: double puddles you can tell apart, three hearts a bit easier, a combo explained the first time two extras meet
(and the level 12 lesson left out then), and every start Freyr naps in his bed by his level until a tap; earlier levels
stay on the map and playable."""
import os, sys, time, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import veteran
GAME = os.environ.get('GAME', 'game.html')
H = open(D + '/harness.js').read()
fails = 0
def ok(name, cond, info=''):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + str(info)), flush=True)
    if not cond: fails += 1
NOCOMBO = json.dumps({k: True for k in veteran.ALL if k != 'combo'})
ALLL = json.dumps({k: True for k in veteran.ALL})
WSTATE = """() => ({ run: introRun ? (introRun.kind || 'intro') : null, scene: !!document.getElementById('iScene'), cls: (document.getElementById('iScene') || {}).className || '',
  intro: document.getElementById('mapScreen').classList.contains('intro'), bar: getComputedStyle(document.querySelector('.mapbar')).opacity,
  tf: document.getElementById('mapInner').style.transform, anim: mapAnimating, onMap, L0: mapGeo && mapGeo.L0,
  card: document.getElementById('introOv').classList.contains('show'), title: document.getElementById('introTitle').textContent,
  hint: !document.getElementById('iHint') ? 'gone' : document.getElementById('iHint').hidden ? 'hidden' : 'shown',
  freyr: (document.getElementById('mFreyr') || {style: {}}).style.visibility, tap: !!document.getElementById('wTap'),
  bed: (() => { const b = document.querySelector('#mapInner .mbed'); return b ? (b.parentNode.style.visibility || 'shown') : null; })(),
  nap: napAt, lesson: tut ? tut.id : null })"""
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    def page(**kw):
        pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True, **kw)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        return pg, errs
    def fresh(pg, ml, learn=ALLL, extra=''):
        pg.goto('file://' + D + '/' + GAME)
        pg.evaluate(f"localStorage.clear(); localStorage.setItem('wm-intro', '1'); localStorage.setItem('wm-level', {ml}); localStorage.setItem('wm-learn', '{learn}'); localStorage.setItem('wm-purr-told', '1'); {extra}")
        pg.reload(); pg.wait_for_timeout(500)
    def skip(pg):
        pg.evaluate('mapSkip = true'); pg.wait_for_function('!introRun && !mapAnimating', timeout=8000, polling=50); pg.wait_for_timeout(200)
    def start(pg, L):
        pg.evaluate(f'openLevel({L})'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500)
        pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    def tap(pg): vs = pg.viewport_size; pg.mouse.click(vs['width'] // 2, int(vs['height'] * .6))
    card = lambda pg, t=12000: pg.wait_for_function("document.getElementById('introOv').classList.contains('show')", timeout=t, polling=50)

    # ---------- M: puddles ----------
    pg, errs = page(); fresh(pg, 40); skip(pg)
    m = pg.evaluate("({ m1: getComputedStyle(document.documentElement).getPropertyValue('--m1'), m2: getComputedStyle(document.documentElement).getPropertyValue('--m2'), icon: INTRO.milk2()[0], text: INTRO.milk2()[2] })")
    ok('M1 single puddles pale, double ones deep blue with a ring', '%239CC8EE' in m['m1'] and '%23123576' in m['m2'] and 'scale(.82)' in m['m2'].replace('%20', ' ') and m['m1'] != m['m2'], [m['m1'][:80], m['m2'][:80]])
    ok('M1 the card shows the new double puddle and says what happens', '#4A92E6' in m['icon'] and 'hell' in m['text'], m['text'])
    start(pg, 31)
    st = pg.evaluate("(() => { const a = document.querySelector('.milk.m1'), c = document.querySelector('.milk.m2'); return [!!a, !!c, a && getComputedStyle(a).backgroundImage.includes('9CC8EE'), c && getComputedStyle(c).backgroundImage.includes('123576')]; })()")
    ok('M2 level 31 has both kinds and they are drawn differently', all(st), st)
    # ---------- H: hearts ----------
    h = pg.evaluate("(() => { const m = cfg.moves; cfg.moves = 25; const r = [7, 6, 3, 2].map(heartsFor); cfg.moves = 20; r.push(heartsFor(6), heartsFor(5)); cfg.moves = m; return r; })()")
    ok('H1 three hearts from 28% moves left, two from 10%', h == [3, 2, 2, 1, 3, 2], h)
    ok('M/H no page errors', not errs, errs[:3]); pg.close()

    # ---------- C: combos explained when two extras first meet ----------
    pg, errs = page(); fresh(pg, 6, NOCOMBO); skip(pg); start(pg, 6)
    ok('C0 not learnt yet', pg.evaluate('!learnt.combo'))
    pg.evaluate("() => { T_base(2); moves = 20; goals = [{ kind: 'collect', type: 5, n: 999, left: 999 }]; lastRem = []; updateHud(); const a = mk('cat'); a.dir = 'h'; grid[4][3] = a; grid[4][4] = mk('nip'); render(false); resetIdle(); }")
    pg.wait_for_timeout(900)
    st = pg.evaluate("({ tut: tut && tut.id, text: document.querySelector('#coach .ccard p') ? document.querySelector('#coach .ccard p').textContent : '', shown: !document.getElementById('coach').hidden, pair: tut && tut.expect && tut.expect.pair })")
    ok('C1 the coach explains the combo right away', st['tut'] == 'combo' and st['shown'] and 'Riesen-Kombi' in st['text'] and 'drei Reihen' in st['text'] and sorted(st['pair'] or []) == [35, 36], st)
    mv = pg.evaluate('moves'); pg.evaluate('trySwap(0, 3, 1, 3)'); pg.wait_for_timeout(300)
    ok('C1 other swaps wait', pg.evaluate('moves') == mv and pg.evaluate('tut && tut.id') == 'combo')
    pg.evaluate("() => { window.__d = false; trySwap(4, 3, 4, 4).then(() => window.__d = true); }")
    pg.wait_for_function('window.__d === true', timeout=30000); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(300)
    st = pg.evaluate("({ learnt: learnt.combo, early: learnt.comboEarly, saved: JSON.parse(localStorage.getItem('wm-learn')).combo, tut: !!tut, coach: document.getElementById('coach').hidden })")
    ok('C1 after the swap it counts as learnt', st['learnt'] and st['early'] and st['saved'] and not st['tut'] and st['coach'], st)
    pr = pg.evaluate('T_check()'); ok('C1 board consistent', not pr, pr[:3] if pr else pr)
    pg.evaluate("() => { const a = mk('laser'); grid[2][2] = a; grid[2][3] = mk('laser'); render(false); resetIdle(); }"); pg.wait_for_timeout(900)
    ok('C2 only once', not pg.evaluate('!!tut'))
    pg.evaluate("showMap()"); pg.wait_for_timeout(400)
    ok('C3 a card before level 12 mentions combos now', 'Riesen-Kombi' in (pg.evaluate("(() => { openLevel(7); return document.getElementById('tipline').textContent; })()") or ''))
    pg.click('#introX'); pg.wait_for_timeout(300)
    pg.evaluate("maxLevel = 12; saveProgress && saveProgress(); openLevel(12)"); pg.wait_for_timeout(500)
    st = pg.evaluate("({ neu: document.getElementById('introNew').textContent, tip: document.getElementById('tipline').textContent })")
    ok('C4 level 12: no "Neu: Kombis" any more', 'Kombi' not in st['neu'], st)
    pg.click('#introBtn'); pg.wait_for_timeout(1800)
    ok('C4 level 12: no combo lesson', pg.evaluate('!tut'), pg.evaluate('tut && tut.id'))
    ok('C no page errors', not errs, errs[:3]); pg.close()
    # a player who never had the early explanation still gets the level 12 card and lesson
    pg, errs = page(); fresh(pg, 12, NOCOMBO); skip(pg)
    pg.evaluate('openLevel(12)'); pg.wait_for_timeout(500)
    ok('C5 level 12 as before: "Neu: Kombis" on the card', 'Kombis' in pg.evaluate("document.getElementById('introNew').textContent"))
    pg.click('#introBtn'); pg.wait_for_timeout(2200)
    ok('C5 and the lesson', pg.evaluate('tut && tut.id') == 'combo', pg.evaluate('tut && tut.id'))
    pg.close()
    # found out alone (no explanation came because it was the last move but one): learnt as well
    pg, errs = page(); fresh(pg, 8, NOCOMBO); skip(pg); start(pg, 8)
    pg.evaluate("() => { T_base(2); moves = 1; goals = [{ kind: 'collect', type: 5, n: 999, left: 999 }]; lastRem = []; updateHud(); grid[3][3] = mk('nip'); grid[3][4] = mk('nip'); render(false); resetIdle(); }"); pg.wait_for_timeout(800)
    ok('C6 no lesson on the very last move', pg.evaluate('!tut'))
    pg.evaluate("() => { moves = 5; updateHud(); trySwap(3, 3, 3, 4); }"); pg.wait_for_timeout(200)
    ok('C6 swapping two extras alone counts as learnt', pg.evaluate('learnt.combo === true'))
    pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(600)
    ok('C6 and no explanation afterwards', pg.evaluate('!tut'))
    ok('C6 no page errors', not errs, errs[:3]); pg.close()

    # ---------- W: the morning nap by his level ----------
    pg, errs = page(); pg.add_init_script('window.__meowTried = 0;')
    fresh(pg, 31)
    pg.evaluate("() => { const m0 = meow; meow = function () { window.__meowTried++; return m0.apply(this, arguments); }; }")
    st = pg.evaluate(WSTATE)
    ok('W1 every start: Freyr asleep in his bed', st['run'] == 'wake' and st['scene'] and 'asleep' in st['cls'] and st['intro'] and st['anim'] and st['tap'], st)
    ok('W1 the bed is by level 31, the map bed hidden under the scene, the standing Freyr hidden', st['nap'] and st['nap']['L'] == 31 and st['bed'] == 'hidden' and st['freyr'] == 'hidden', st)
    nodes = pg.evaluate("[30, 29, 16, 31, 32].map(L => (document.querySelector('.mnode[data-l=\"' + L + '\"]') || {}).className || '')")
    ok('W1 the earlier levels are on the map as done, 31 is the current one', all('done' in n for n in nodes[:3]) and 'cur' in nodes[3] and 'lock' in nodes[4] and st['L0'] == 16, nodes)
    near = pg.evaluate("(() => { const s = document.getElementById('iBedBack').getBoundingClientRect(), n = document.querySelector('.mnode[data-l=\"31\"]').getBoundingClientRect(); return Math.hypot(s.left + s.width / 2 - n.left - n.width / 2, s.top + s.height / 2 - n.top - n.height / 2) / (n.width / 62); })()")
    ok('W1 right next to his level (on screen)', near < 240, near)
    pg.wait_for_timeout(1300); st = pg.evaluate(WSTATE)
    ok('W1 the hint shows while he sleeps, he sleeps on', st['hint'] == 'shown' and 'asleep' in st['cls'] and not st['card'], st)
    t0 = time.time(); tap(pg); pg.wait_for_timeout(250); st = pg.evaluate(WSTATE)
    ok('W2 a tap wakes him', 'asleep' not in st['cls'] and st['hint'] in ('hidden', 'gone'), st)
    pg.wait_for_function('window.__meowTried > 0', timeout=8000, polling=50)
    ok('W2 he meows', 'Miau' in pg.evaluate("document.getElementById('iBubble') ? document.getElementById('iBubble').textContent : ''"))
    card(pg); dt = time.time() - t0; st = pg.evaluate(WSTATE)
    ok('W2 then his level card', st['card'] and st['title'] == 'Level 31', st)
    ok('W2 short: 3.5-8 s from the tap', 3.5 <= dt <= 8, dt)
    pg.wait_for_timeout(700); st = pg.evaluate(WSTATE)
    ok('W2 everything back to normal', not st['scene'] and not st['intro'] and st['tf'] == '' and not st['anim'] and st['run'] is None and float(st['bar']) > .95 and st['freyr'] != 'hidden', st)
    pg.wait_for_timeout(500)
    ok('W2 the tap layer is gone', not pg.evaluate("!!document.getElementById('wTap')"))
    fr = pg.evaluate("(() => { const f = document.getElementById('mFreyr'), n = document.querySelector('.mnode[data-l=\"31\"]'); const a = f.getBoundingClientRect(), c = n.getBoundingClientRect(); return a.left + a.width / 2 - c.left - c.width / 2; })()")
    ok('W2 Freyr stands on level 31, his bed stays next to it', abs(fr) < 2 and st['bed'] == 'shown', [fr, st['bed']])
    pg.click('#introX'); pg.wait_for_timeout(400)
    pg.click('.mnode[data-l="30"]'); pg.wait_for_timeout(500)
    ok('W3 an earlier level can be played', pg.evaluate("document.getElementById('introOv').classList.contains('show') && document.getElementById('introTitle').textContent") == 'Level 30')
    pg.click('#introX'); pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('map').scrollTop = document.getElementById('map').scrollHeight"); pg.wait_for_timeout(300)
    pg.click('.mnode[data-l="16"]'); pg.wait_for_timeout(500)
    ok('W3 and one further down the map', pg.evaluate("document.getElementById('introTitle').textContent") == 'Level 16')
    pg.click('#introBtn'); pg.wait_for_timeout(1200); pg.evaluate("showMap()"); pg.wait_for_timeout(500)
    st = pg.evaluate(WSTATE)
    ok('W3 back on the map: the bed still where he slept', st['bed'] == 'shown' and st['nap']['L'] == 31 and not st['scene'], st)
    ok('W no page errors', not errs, errs[:3])
    # W4: the next start: again; a second tap skips to the end
    pg.reload(); pg.wait_for_timeout(500); st = pg.evaluate(WSTATE)
    ok('W4 the next start: asleep again', st['run'] == 'wake' and 'asleep' in st['cls'], st)
    t0 = time.time(); tap(pg); pg.wait_for_timeout(350); tap(pg); card(pg, 6000); dt = time.time() - t0
    st = pg.evaluate(WSTATE)
    ok('W4 a second tap skips to the card', dt < 2.5 and st['card'] and st['title'] == 'Level 31' and not st['scene'] and st['freyr'] != 'hidden', [dt, st])
    pg.wait_for_timeout(600)
    ok('W4 the skipping tap did not open another level', pg.evaluate("document.getElementById('introTitle').textContent") == 'Level 31' and pg.evaluate("document.querySelectorAll('.overlay.show').length") == 1)
    ok('W4 no page errors', not errs, errs[:3]); pg.close()

    # W5: stopped half way (the level starts while he walks)
    pg, errs = page(); fresh(pg, 9)
    tap(pg); pg.wait_for_function("document.querySelector('#iCat .fsprite.walk')", timeout=10000, polling=30)
    pg.evaluate('openLevel(9)'); pg.wait_for_timeout(300); pg.click('#introBtn'); pg.wait_for_timeout(800)
    st = pg.evaluate(WSTATE)
    ok('W5 stopped cleanly', st['run'] is None and not st['anim'] and st['tf'] == '' and not st['intro'] and not st['onMap'], st)
    pg.wait_for_timeout(1500); ok('W5 no card later', not pg.evaluate("document.getElementById('introOv').classList.contains('show')"))
    pg.evaluate('showMap()'); pg.wait_for_timeout(500); st = pg.evaluate(WSTATE)
    ok('W5 the map is normal afterwards, the bed visible', not st['scene'] and st['tf'] == '' and st['bed'] == 'shown' and st['freyr'] != 'hidden' and not st['tap'], st)
    ok('W5 no page errors', not errs, errs[:3]); pg.close()

    # W6: Enter wakes him; W7: still at level 1: the bed at home, the walk to level 1
    pg, errs = page(); fresh(pg, 1)
    st = pg.evaluate(WSTATE)
    ok('W7 level 1: his bed at the start of the map', st['run'] == 'wake' and st['nap'] is None and st['scene'], st)
    pg.wait_for_timeout(300); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    ok('W6 Enter wakes him', 'asleep' not in pg.evaluate(WSTATE)['cls'])
    card(pg); ok('W7 then level 1', pg.evaluate("document.getElementById('introTitle').textContent") == 'Level 1')
    ok('W6/7 no page errors', not errs, errs[:3]); pg.close()

    # W8: skipped from outside: the plain map, no card
    pg, errs = page(); fresh(pg, 57); skip(pg); pg.wait_for_timeout(900); st = pg.evaluate(WSTATE)
    ok('W8 a skip: the normal map, no card', st['onMap'] and not st['card'] and not st['scene'] and st['tf'] == '' and st['bed'] == 'shown', st)
    pg.close()

    # W9: no lives: no card at the end
    pg, errs = page(); fresh(pg, 20, extra='localStorage.setItem("wm-lives", 0); localStorage.setItem("wm-life-ts", Date.now());')
    tap(pg); pg.wait_for_function('!introRun', timeout=10000, polling=50); pg.wait_for_timeout(900)
    ok('W9 no lives: the map, no cards', pg.evaluate("onMap && !document.querySelector('.overlay.show')"))
    pg.close()

    # W10: the chest lesson still comes first when it is due
    learn = json.dumps({k: True for k in veteran.ALL if k != 'chest'})
    pg, errs = page(); fresh(pg, 14, learn)
    tap(pg); pg.wait_for_function("tut && tut.id === 'chest'", timeout=10000, polling=50)
    ok('W10 the chest lesson after waking up', True)
    pg.click('#coach .ccard button'); card(pg, 5000)
    ok('W10 then his level', pg.evaluate("document.getElementById('introTitle').textContent") == 'Level 14')
    ok('W10 no page errors', not errs, errs[:3]); pg.close()

    # W11: reduced motion: no zoom, straight to the end after the tap
    pg, errs = page(reduced_motion='reduce'); fresh(pg, 23)
    st = pg.evaluate(WSTATE); ok('W11 reduced motion: no zoom', 'scale(' not in st['tf'] or 'scale(1)' in st['tf'], st)
    t0 = time.time(); tap(pg); card(pg, 5000)
    ok('W11 reduced motion: the card at once', time.time() - t0 < 2.2, time.time() - t0)
    ok('W11 no page errors', not errs, errs[:3]); pg.close()

    # W13: the earlier levels: a sign at the bottom of the map brings back the worlds before
    pg, errs = page(); fresh(pg, 31); skip(pg)
    st = pg.evaluate("({ L0: mapGeo.L0, sign: (document.querySelector('.mback') || {}).textContent || '', n1: !!document.querySelector('.mnode[data-l=\"1\"]') })")
    ok('W13 level 31: the map starts at 16, a sign offers 1-15', st['L0'] == 16 and 'Frühere Level' in st['sign'] and '1–15' in st['sign'] and not st['n1'], st)
    top0 = pg.evaluate("(() => { const n = document.querySelector('.mnode[data-l=\"20\"]').getBoundingClientRect(); return n.top; })()")
    pg.evaluate("document.getElementById('map').scrollTop = 1e6"); pg.wait_for_timeout(300)
    pg.click('.mback'); pg.wait_for_timeout(900)
    st = pg.evaluate("({ L0: mapGeo.L0, sign: !!document.querySelector('.mback'), n1: (document.querySelector('.mnode[data-l=\"1\"]') || {}).className || '', beds: document.querySelectorAll('#mapInner .mbed').length, nap: napAt })")
    ok('W13 after the tap: levels 1-15 are on the map, done, no sign any more, still one bed (by 31)', st['L0'] == 1 and not st['sign'] and 'done' in st['n1'] and st['beds'] == 1 and st['nap']['L'] == 31, st)
    pg.click('.mnode[data-l="1"]'); pg.wait_for_timeout(500)
    ok('W13 level 1 can be played again', pg.evaluate("document.getElementById('introTitle').textContent") == 'Level 1')
    pg.click('#introX'); pg.wait_for_timeout(300)
    pg.evaluate("openLevel(31)"); pg.wait_for_timeout(400); pg.click('#introBtn'); pg.wait_for_timeout(1000); pg.evaluate('showMap()'); pg.wait_for_timeout(500)
    ok('W13 back from a level: the earlier levels stay for the session', pg.evaluate("mapGeo.L0") == 1)
    ok('W13 no page errors', not errs, errs[:3]); pg.close()
    pg, errs = page(); fresh(pg, 160); skip(pg)
    sign = pg.evaluate("(document.querySelector('.mback') || {}).textContent || ''")
    pg.evaluate("document.getElementById('map').scrollTop = 1e6"); pg.wait_for_timeout(300); pg.click('.mback'); pg.wait_for_timeout(900)
    st = pg.evaluate("({ L0: mapGeo.L0, sign: (document.querySelector('.mback') || {}).textContent || '' })")
    ok('W13 far on (160): 25 more at a time', '116–140' in sign and st['L0'] == 116 and '91–115' in st['sign'], [sign, st])
    ok('W13 160 no page errors', not errs, errs[:3]); pg.close()

    # W12: a phone turned to the side and a small phone: the scene fits
    for vw, vh in [(320, 568), (844, 390)]:
        pg = b.new_page(viewport={'width': vw, 'height': vh}, has_touch=True, is_mobile=True); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        fresh(pg, 44)
        r = pg.evaluate("(() => { const s = document.getElementById('iBedBack').getBoundingClientRect(); return [s.left, s.right, s.top, s.bottom, innerWidth, innerHeight]; })()")
        ok(f'W12 {vw}x{vh}: the bed is on screen', r[0] > -5 and r[1] < r[4] + 5 and r[2] > -5 and r[3] < r[5] + 5, r)
        tap(pg); card(pg); ok(f'W12 {vw}x{vh}: card', pg.evaluate("document.getElementById('introTitle').textContent") == 'Level 44')
        ok(f'W12 {vw}x{vh}: no page errors', not errs, errs[:3]); pg.close()
    b.close()
print('FAILS', fails)
