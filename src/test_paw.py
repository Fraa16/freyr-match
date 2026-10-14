"""V27 bug: the tapping paw stayed at Freyr's empty spot while he ran his zoomies after a win with a full, unused meter"""
import os, sys
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
ST = """() => ({ paw: !document.querySelector('.mtap').hidden, away: mascot.classList.contains('away'), txt: document.getElementById('purrTxt').textContent,
  win: winRunning, purr, full: purr >= PURR_MAX })"""
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); veteran.veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/' + GAME)
    pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 24); localStorage.setItem("wm-purr-told", "1"); localStorage.setItem("wm-purr-keep", "1"); localStorage.setItem("wm-purr", 999)')
    pg.reload(); pg.wait_for_timeout(600); pg.evaluate(WAIT_MAP)
    pg.evaluate('openLevel(23)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500)
    pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    st = pg.evaluate(ST)
    ok('W1 full meter at the start: the paw taps on Freyr', st['full'] and st['paw'] and 'Tipp auf' in st['txt'], st)
    # win without using it, with moves left for the zoomies; sample the state through the whole show
    rc = pg.evaluate("(() => { for (let r = 0; r < N - 1; r++) for (let c = 0; c < N - 2; c++) if (mask[r][c] && mask[r][c+1] && mask[r][c+2] && mask[r+1][c+2]) return [r, c]; })()")
    r0, c0 = rc
    pg.evaluate(f"() => {{ window.__seen = []; T_setup(1, [[{r0},{c0}],[{r0},{c0+1}],[{r0+1},{c0+2}]]); T_goalNext(); moves = 8; updateHud(); trySwap({r0+1},{c0+2},{r0},{c0+2});"
                f" const iv = setInterval(() => {{ window.__seen.push({{ paw: !document.querySelector('.mtap').hidden, away: mascot.classList.contains('away'), win: winRunning,"
                f" txt: document.getElementById('purrTxt').textContent }}); if (document.getElementById('endOv').classList.contains('show')) clearInterval(iv); }}, 40); }}")
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=60000); pg.wait_for_timeout(300)
    seen = pg.evaluate('window.__seen')
    during = [s for s in seen if s['win'] or s['away']]
    ok('W2 the show ran with Freyr away', any(s['away'] for s in seen), len(seen))
    bad = [s for s in during if s['paw']]
    ok('W2 no paw during the win show', not bad and during, bad[:2])
    ok('W2 the bar says the meter is kept', any('nächste Level' in s['txt'] for s in during), [s['txt'] for s in during[:3]])
    st = pg.evaluate(ST)
    ok('W3 the meter is still full after the win', st['full'] and not st['paw'], st)
    # next level: the paw is back
    pg.evaluate("() => { document.getElementById('endOv').classList.remove('show'); showMap(); }"); pg.wait_for_timeout(800); pg.evaluate(WAIT_MAP)
    pg.evaluate('openLevel(24)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500); pg.evaluate('T_waitIdle()')
    st = pg.evaluate(ST)
    ok('W4 the next level: paw back, still full', st['full'] and st['paw'] and 'Tipp auf' in st['txt'], st)
    # it also hides while Freyr is away for any other reason, and comes back
    pg.evaluate("mascot.classList.add('away')"); pg.wait_for_timeout(100)
    ok('W5 away: no paw', not pg.evaluate(ST)['paw'])
    pg.evaluate("mascot.classList.remove('away')"); pg.wait_for_timeout(100)
    ok('W5 back: paw again', pg.evaluate(ST)['paw'])
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', fails)
