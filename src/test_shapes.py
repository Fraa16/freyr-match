import json, sys, os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
GAME = 'file://' + D + '/' + (sys.argv[1] if len(sys.argv) > 1 else 'game.html')
H = open(D + '/harness.js').read()

SCEN = [
  # name, T, cells, swap (r1,c1,r2,c2), expected (r,c,kind,dir)
  ('square', 0, [(2,2),(2,3),(3,2),(4,3)], (4,3,3,3), (3,3,'laser','')),
  ('four-h', 1, [(5,1),(5,2),(5,4),(4,3)], (4,3,5,3), (5,3,'cat','h')),
  ('four-v', 2, [(1,6),(2,6),(4,6),(3,5)], (3,5,3,6), (3,6,'cat','v')),
  ('five', 3, [(6,0),(6,1),(6,3),(6,4),(5,2)], (5,2,6,2), (6,2,'bowl','')),
  ('L', 4, [(1,1),(2,1),(3,2),(3,3),(4,1)], (4,1,3,1), (3,1,'nip','')),
  ('T', 5, [(2,4),(2,6),(3,5),(4,5),(1,5)], (1,5,2,5), (2,5,'nip','')),
  ('three', 0, [(6,5),(6,7),(5,6)], (5,6,6,6), None),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); __import__('veteran').veteran(pg)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto(GAME); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 40)'); pg.reload(); pg.wait_for_timeout(900)
    pg.evaluate("""async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); if (!document.getElementById('introOv').classList.contains('show')) openLevel(1); }"""); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(400)
    pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    pg.evaluate('''() => { const orig = extrasFor; window.T_spawnLog = [];
      window.extrasFor = (m, sk) => { const out = orig(m, sk); T_spawnLog.push([...out].map(([k, v]) => [k / N | 0, k % N, v.kind, v.dir || ''])); return out; }; }''')
    res = []
    for name, T, cells, sw, exp in SCEN:
        pre = pg.evaluate(f'T_setup({T}, {json.dumps(cells)})')
        pg.evaluate('T_spawnLog.length = 0')
        pg.evaluate(f'trySwap({sw[0]},{sw[1]},{sw[2]},{sw[3]})')
        pg.wait_for_timeout(120)
        if name == 'five':
            pg.wait_for_timeout(200); pg.screenshot(path=D + '/s_five.png')
        pg.evaluate('T_waitIdle()')
        first = pg.evaluate('T_spawnLog[0] || []')
        probs = pg.evaluate('T_check()')
        ok = (exp is None and first == []) or (exp is not None and [list(exp)] == [x for x in first if x[2] == exp[2]][:1] and len(first) == 1)
        res.append((name, 'pre-matches=%d' % pre, 'first spawn=%s' % first, 'OK' if ok and not probs else 'FAIL', probs[:4]))
    for r in res: print(*r)
    print('errors:', errs)
    b.close()
