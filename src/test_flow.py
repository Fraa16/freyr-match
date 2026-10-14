"""flow edge cases: pause during the win/loss sequence, leaving after a queued loss, settings focus, endless levels,
double taps on end buttons. prints PASS/FAIL per check."""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import veteran
GAME = os.environ.get('GAME', 'game.html')
H = open(D + '/harness.js').read()
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
fails = 0
def ok(name, cond, info=''):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + str(info)), flush=True)
    if not cond: fails += 1
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); veteran.veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    def fresh(ml, extra=''):
        pg.goto('file://' + D + '/' + GAME)
        pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", {ml}); localStorage.setItem("wm-treats", 200); {extra}')
        pg.reload(); pg.wait_for_timeout(600); pg.evaluate(WAIT_MAP)
    def start(L):
        pg.evaluate(f'openLevel({L})'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500)
        pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    shown = lambda id: pg.evaluate(f'document.getElementById("{id}").classList.contains("show")')

    # S1: the pause button and Escape during the win sequence
    fresh(64, 'localStorage.setItem("wm-streak", 2);'); start(64)
    pg.evaluate("() => { T_setup(1, [[5,1],[5,2],[6,3]]); T_goalNext(); moves = 8; updateHud(); trySwap(6,3,5,3); }")
    pg.wait_for_timeout(2600)
    pg.click('#pauseBtn', force=True); pg.wait_for_timeout(300)
    ok('S1 pause blocked during win sequence', not shown('pauseOv'))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    ok('S1 Escape blocked during win sequence', not shown('pauseOv'))
    if shown('pauseOv'):
        pg.click('#toMap'); pg.wait_for_timeout(12000)
        ok('S1b leaving after a win does not ask to give up', not shown('quitOv'))
        if shown('quitOv'):
            pg.click('#quitGo'); pg.wait_for_timeout(800)
            st = pg.evaluate('({streak: winStreak, ml: maxLevel, end: document.getElementById("endOv").classList.contains("show"), map: onMap})')
            ok('S1c a win keeps the streak', st['streak'] >= 3, st)
            ok('S1d no end card over the map', not (st['end'] and st['map']), st)
    else:
        pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=30000)
        ok('S1e end card after the win', shown('endOv'))

    # S2: leaving right after the last move, before the loss card shows
    fresh(40); start(40)
    pg.evaluate("() => { moves = 1; updateHud(); const m = bestMove(); trySwap(m.r, m.c, m.r2, m.c2); }")
    pg.wait_for_timeout(120)
    pg.click('#pauseBtn', force=True); pg.wait_for_timeout(250)
    if shown('pauseOv'):
        pg.click('#toMap'); pg.wait_for_timeout(5000)
    else:
        pg.wait_for_timeout(5000)
    st = pg.evaluate('({end: document.getElementById("endOv").classList.contains("show"), quit: document.getElementById("quitOv").classList.contains("show"), pause: document.getElementById("pauseOv").classList.contains("show")})')
    ok('S2 never two cards at once', sum(st.values()) <= 1, st)
    if st['quit']:
        pg.click('#quitGo'); pg.wait_for_timeout(800)
        st2 = pg.evaluate('({end: document.getElementById("endOv").classList.contains("show"), map: onMap, fails: JSON.parse(localStorage.getItem("wm-fails") || "{}")})')
        ok('S2b no end card left over the map', not (st2['end'] and st2['map']), st2)

    # S3: the clock rings: no pause on top of the loss card
    fresh(73); start(73)
    pg.evaluate("() => { for (const row of grid) for (const x of row) if (x && x.clock != null) x.clock = 1; const m = bestMove(); trySwap(m.r, m.c, m.r2, m.c2); }")
    pg.wait_for_function('clockRang === true', timeout=20000); pg.wait_for_timeout(200)
    pg.click('#pauseBtn', force=True); pg.wait_for_timeout(300)
    pg.wait_for_timeout(2500)
    st = pg.evaluate('({end: document.getElementById("endOv").classList.contains("show"), pause: document.getElementById("pauseOv").classList.contains("show"), rang: clockRang})')
    ok('S3 clock ring: one card only', not (st['end'] and st['pause']), st)

    # S4: the outfits card: no name field, no photo, the jersey hidden until it is won
    fresh(70)
    pg.click('#mFace'); pg.wait_for_timeout(500)
    st = pg.evaluate("({name: !!document.getElementById('nameIn'), photo: !!document.getElementById('photoBtn'), title: document.getElementById('setTitle').textContent, outfits: [...document.querySelectorAll('#outfits .outfit')].map(e => e.dataset.id), cat: catName})")
    ok('S4 no name field, no photo', not st['name'] and not st['photo'] and st['cat'] == 'Freyr', st)
    ok('S4 jersey not listed before it is won', 'trikot' not in st['outfits'], st)
    pg.click('#setDone'); pg.wait_for_timeout(300)
    fresh(70, 'localStorage.setItem("wm-owned", JSON.stringify(["trikot"])); localStorage.setItem("wm-name", "Mieze2"); localStorage.setItem("wm-photo", "data:x");')
    st = pg.evaluate("({cat: catName, photo, ls: [localStorage.getItem('wm-name'), localStorage.getItem('wm-photo')]})")
    ok('S4 old name and photo are dropped', st['cat'] == 'Freyr' and not st['photo'] and st['ls'] == [None, None], st)
    pg.click('#mFace'); pg.wait_for_timeout(500)
    ok('S4 jersey listed once it is won', 'trikot' in pg.evaluate("[...document.querySelectorAll('#outfits .outfit')].map(e => e.dataset.id)"))
    pg.click('#setDone'); pg.wait_for_timeout(300)
    intro = pg.evaluate("() => { const t = INTRO.trabzon(); return t[1] + ' ' + t[2] + ' ' + (t[0].includes('class=\"acc\"') ? 'ACC' : ''); }")
    ok('S4 level 61 does not announce the jersey', 'Trikot' not in intro and 'ACC' not in intro, intro)

    # S5: the mascot's label says what a tap does
    lbl = pg.evaluate('document.getElementById("mascot").getAttribute("aria-label")')
    ok('S5 mascot label is not "Deine Katze einrichten"', lbl != 'Deine Katze einrichten', lbl)
    print('   mascot label:', lbl)

    # S6: endless levels after 160
    for ml in [161, 300]:
        fresh(ml); e0 = len(errs)
        info = pg.evaluate(f'() => {{ openLevel({ml}); return {{ intro: document.getElementById("introOv").classList.contains("show"), title: document.getElementById("introTitle").textContent, world: document.getElementById("introWorld").textContent, goals: goals.length, nodes: document.querySelectorAll(".mnode").length }}; }}')
        ok(f'S6 level {ml} opens', info['intro'] and info['goals'] > 0 and len(errs) == e0, info)
        pg.click('#introBtn'); pg.wait_for_timeout(1500); pg.add_script_tag(content=H)
        pr = pg.evaluate('T_check()'); ok(f'S6 level {ml} board ok', not pr, pr)

    # S7: double tap on "Weiter" after a win: one walk, one level card
    fresh(30); start(30)
    pg.evaluate("() => { T_setup(1, [[5,1],[5,2],[6,3]]); T_goalNext(); moves = 0; updateHud(); trySwap(6,3,5,3); }")
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=30000); pg.wait_for_timeout(600)
    pg.evaluate("() => { const b = document.getElementById('endBtn'); b.click(); b.click(); }")
    pg.wait_for_function('document.getElementById("introOv").classList.contains("show")', timeout=20000); pg.wait_for_timeout(300)
    st = pg.evaluate('({ml: maxLevel, intro: document.getElementById("introOv").classList.contains("show"), title: document.getElementById("introTitle").textContent, walkers: document.querySelectorAll(".mwalker:not([hidden])").length})')
    ok('S7 one level card for level 31', st['ml'] == 31 and st['intro'] and st['title'] == 'Level 31', st)

    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', fails)
