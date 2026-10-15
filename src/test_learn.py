"""walk through every lesson the way a player would: real swipes, taps and button clicks through the coach overlay.
usage: python3 test_learn.py [levels comma-separated] [runs] [shots 0/1]"""
import os, sys, json, time
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from fontfix import fonts
H = open(D + '/harness.js').read()
OUT = D + '/ln_'
LEVELS = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 and sys.argv[1] else [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 16, 18, 24, 28, 31, 33, 36, 40, 43, 47, 52, 57, 63, 73, 80, 84, 91, 97]
RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 1
SHOTS = (sys.argv[3] != '0') if len(sys.argv) > 3 else True
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
STATE = """() => {
  if (!tut) return null;
  const e = tut.expect, nx = tutEls && !tutEls.next.hidden && !tutEls.root.hidden;
  return { id: tut.id, type: e && e.type, pair: e && e.pair || null, cell: e && e.cell != null ? e.cell : null, kind: e && e.kind || null,
           next: !!nx, text: tutEls ? tutEls.text.textContent : '', busy };
}"""
def fresh(pg, L, extra=''):
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()')
    got = {k: True for k, u in [('paw', 16), ('claw', 33), ('swap', 43), ('feather', 97)] if u < L}
    tools = json.dumps({'inv': {k: 1 for k in got}, 'got': got})
    pg.evaluate(f"localStorage.setItem('wm-level', {L}); localStorage.setItem('wm-treats', 300); localStorage.setItem('wm-tools', '{tools}'); localStorage.setItem('wm-learn', JSON.stringify({{chest: true}})); localStorage.setItem('wm-news41', 'done'); {extra}")
    pg.reload(); pg.wait_for_timeout(700)
def center(pg, k):
    return pg.evaluate(f"(() => {{ const [x, y] = cellXY({k}); return [x, y]; }})()")
def el_center(pg, sel):
    b = pg.locator(sel).first.bounding_box()
    return [b['x'] + b['width'] / 2, b['y'] + b['height'] / 2]
def wait_state(pg, prev_text, timeout=15):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s, bz = pg.evaluate('() => [(' + STATE + ')(), busy]')
        if s is None and not bz: return None
        if s and not s['busy'] and (s['type'] or s['next']) and s['text'] != prev_text: return s
        pg.wait_for_timeout(120)
    return 'TIMEOUT'
summary = []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    VW, VH = int(os.environ.get('VW', 390)), int(os.environ.get('VH', 844)); OUT = D + '/' + os.environ.get('PFX', 'ln_')
    pg = b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=2 if SHOTS else 1)
    import veteran as _v; _v.seen_intro(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    for L in LEVELS:
        for run in range(RUNS):
            fresh(pg, L)
            if SHOTS and run == 0: fonts(pg)
            pg.evaluate(WAIT_MAP)
            pg.evaluate(f"openLevel({L})"); pg.wait_for_timeout(600)
            intro = pg.evaluate('cfg.intro')
            if SHOTS and run == 0: pg.screenshot(path=f'{OUT}{L:02d}_card.png')
            pg.add_script_tag(content=H)
            pg.click('#introBtn'); pg.wait_for_function('busy || !!tut', timeout=5000)
            s = wait_state(pg, None, 12)
            steps, log, rejected = 0, [], None
            while s and s != 'TIMEOUT' and steps < 12:
                if SHOTS and run == 0: pg.screenshot(path=f'{OUT}{L:02d}_{steps}.png')
                # once per lesson: a tap on a dimmed spot must do nothing
                if rejected is None and s['type'] == 'turn' and s['pair']:
                    mv0 = pg.evaluate('moves'); pg.mouse.click(20, 830); pg.wait_for_timeout(150)
                    far = pg.evaluate("(p) => { const o = []; for (let k = 0; k < N * N; k++) if (mask[k / N | 0][k % N] && grid[k / N | 0][k % N] && !p.includes(k) && k % N < N - 1 && mask[k / N | 0][k % N + 1]) o.push(k); return o; }", s['pair'])
                    # a swipe on a cell that is not part of the shown move
                    ok_far = None
                    for k in far:
                        a = center(pg, k); bb = center(pg, k + 1 if k % 8 < 7 else k - 1)
                        pg.mouse.move(*a); pg.mouse.down(); pg.mouse.move((a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2, steps=3); pg.mouse.move(*bb, steps=3); pg.mouse.up()
                        ok_far = k; break
                    pg.wait_for_timeout(500)
                    rejected = pg.evaluate('moves') == mv0 and pg.evaluate(STATE)['text'] == s['text']
                log.append((s['type'] or 'next') + ('' if not s['kind'] else ':' + s['kind']))
                if s['next']:
                    pg.click('#coach .ccard button')
                elif s['type'] == 'turn' and s['pair']:
                    a, c = center(pg, s['pair'][0]), center(pg, s['pair'][1])
                    pg.mouse.move(*a); pg.mouse.down(); pg.mouse.move((a[0] + c[0]) / 2, (a[1] + c[1]) / 2, steps=4); pg.mouse.move(*c, steps=4); pg.mouse.up()
                elif s['type'] == 'turn' and s['cell'] is not None:
                    a = center(pg, s['cell']); pg.mouse.click(*a)
                elif s['type'] == 'aim':
                    if s['kind'] == 'pounce': pg.mouse.click(*el_center(pg, '#mascot'))
                    else: pg.mouse.click(*el_center(pg, f'#tools [data-id="{s["kind"]}"] .tbtn'))
                steps += 1
                pg.wait_for_timeout(250)
                if SHOTS and run == 0 and s['type'] == 'turn': pg.wait_for_timeout(200); pg.screenshot(path=f'{OUT}{L:02d}_{steps - 1}b.png')
                s = wait_state(pg, s['text'], 15)
            pg.evaluate('T_waitIdle()')
            learnt = pg.evaluate(f"!!learnt[{json.dumps(intro)}]") if intro else None
            probs = pg.evaluate('T_check()')
            res = {'L': L, 'intro': intro, 'run': run, 'steps': steps, 'log': ' '.join(log), 'learnt': learnt, 'timeout': s == 'TIMEOUT',
                   'rejected': rejected, 'coach_left': pg.evaluate("!!document.getElementById('coach') && !document.getElementById('coach').hidden"), 'probs': probs[:3]}
            summary.append(res)
            print(json.dumps(res, ensure_ascii=False), flush=True)
            if SHOTS and run == 0: pg.screenshot(path=f'{OUT}{L:02d}_end.png')
    print('errors:', errs[:8])
    b.close()
