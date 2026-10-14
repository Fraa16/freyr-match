import sys, os, time
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
GAME = 'file://' + D + '/' + (sys.argv[1] if len(sys.argv) > 1 else 'game.html')
H = open(D + '/harness.js').read()
LEVEL = sys.argv[2] if len(sys.argv) > 2 else '1'
LEFT = int(sys.argv[3]) if len(sys.argv) > 3 else 9
SHOTS = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); __import__('veteran').veteran(pg)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(GAME); pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", "{LEVEL}")'); pg.reload(); pg.wait_for_timeout(900)
    pg.evaluate("""async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); if (!document.getElementById('introOv').classList.contains('show')) openLevel(maxLevel); }"""); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(400)
    pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    # win on the next move: goals done, score just under target, some moves left
    pg.evaluate(f'''() => {{ for (const g of goals) if (g.kind === 'collect') g.left = 0;
      for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {{ const x = grid[r][c]; if (x.type === 'box') {{ grid[r][c] = mk(0); }} x.locked = false; }}
      T_setup(1, [[5,1],[5,2],[6,3]]); T_goalNext(); moves = {LEFT + 1}; updateHud(); }}''')
    t0 = time.time()
    pg.evaluate('() => { window.__done = false; trySwap(6,3,5,3).then(() => window.__done = true); }')
    last = 0
    for i, ms in enumerate(SHOTS):
        pg.wait_for_timeout(ms - last); last = ms
        pg.screenshot(path=D + f'/z{i}.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 640})
    pg.wait_for_function('window.__done === true', timeout=60000)
    dt = time.time() - t0
    print('finale took %.1fs' % dt, 'moves now', pg.evaluate('moves'), 'bonus', pg.evaluate('lastBonus'), 'score', pg.evaluate('score'))
    print('end text:', pg.evaluate('document.getElementById("endText").textContent'))
    print('end shown:', pg.evaluate('document.getElementById("endOv").classList.contains("show")'), 'mascot away:', pg.evaluate('mascot.classList.contains("away")'))
    print('runners left:', pg.evaluate('document.querySelectorAll(".runner").length'), 'check:', pg.evaluate('T_check()')[:3])
    print('errors:', errs)
    b.close()
