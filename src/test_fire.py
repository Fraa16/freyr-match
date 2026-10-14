import json, sys, os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
GAME = 'file://' + D + '/' + (sys.argv[1] if len(sys.argv) > 1 else 'game.html')
H = open(D + '/harness.js').read()
SHOTS = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else set()

# name, extras [(r,c,kind,dir)], swap, screenshot delay ms
SCEN = [
  ('laser', [(4,4,'laser','')], (4,4,4,5), 330),
  ('cat-h', [(3,3,'cat','h')], (3,3,4,3), 330),
  ('cat-v', [(3,3,'cat','v')], (3,3,3,4), 330),
  ('nip', [(4,3,'nip','')], (4,3,4,4), 360),
  ('bowl', [(4,4,'bowl','')], (4,4,4,5), 420),
  ('cat+cat', [(3,3,'cat','h'),(3,4,'cat','v')], (3,3,3,4), 360),
  ('cat+nip', [(3,3,'cat','h'),(3,4,'nip','')], (3,3,3,4), 380),
  ('nip+nip', [(3,3,'nip',''),(4,3,'nip','')], (3,3,4,3), 420),
  ('laser+laser', [(3,3,'laser',''),(3,4,'laser','')], (3,3,3,4), 520),
  ('laser+cat', [(3,3,'laser',''),(3,4,'cat','v')], (3,3,3,4), 700),
  ('laser+nip', [(3,3,'laser',''),(3,4,'nip','')], (3,3,3,4), 700),
  ('bowl+cat', [(3,3,'bowl',''),(3,4,'cat','h')], (3,3,3,4), 900),
  ('bowl+nip', [(3,3,'bowl',''),(3,4,'nip','')], (3,3,3,4), 900),
  ('bowl+laser', [(3,3,'bowl',''),(3,4,'laser','')], (3,3,3,4), 1500),
  ('bowl+bowl', [(3,3,'bowl',''),(3,4,'bowl','')], (3,3,3,4), 500),
]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); __import__('veteran').veteran(pg)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(GAME); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 40)'); pg.reload(); pg.wait_for_timeout(900)
    pg.evaluate("""async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); if (!document.getElementById('introOv').classList.contains('show')) openLevel(1); }"""); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(400)
    pg.add_script_tag(content=H)
    for name, extras, sw, shot in SCEN:
        pg.evaluate(f'T_setup(0, [], {json.dumps(extras)})')
        pg.evaluate('target = 1e9; moves = 25'); sc0 = pg.evaluate('score')
        pg.evaluate(f'() => {{ window.__done = false; trySwap({sw[0]},{sw[1]},{sw[2]},{sw[3]}).then(() => window.__done = true); }}')
        if name in SHOTS or 'all' in SHOTS:
            pg.wait_for_timeout(shot); pg.screenshot(path=D + '/f_' + name.replace('+', '_') + '.png', clip={'x': 0, 'y': 230, 'width': 390, 'height': 380})
        pg.wait_for_function('window.__done === true', timeout=20000)
        probs = pg.evaluate('T_check()')
        gained = pg.evaluate('score') - sc0
        print(name, 'points=%d' % gained, 'OK' if not probs else 'FAIL', probs[:4])
        # keep the game from ending mid-test
        pg.evaluate('moves = 25; score = 0; for (const g of goals) g.left = 99; document.querySelectorAll(".overlay.show").forEach(o => o.classList.remove("show")); busy = false')
    print('errors:', errs)
    b.close()
