import os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
H = open(D + '/harness.js').read()
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); __import__('veteran').veteran(pg)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", "11")'); pg.reload(); pg.wait_for_timeout(800)
    pg.evaluate("""async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); if (!document.getElementById('introOv').classList.contains('show')) openLevel(maxLevel); }"""); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(600)
    pg.add_script_tag(content=H)
    pg.evaluate('T_waitIdle()'); pg.evaluate('moves = 40; updateHud()')
    for step in range(12):
        pos = pg.evaluate('(() => { for (let r = N - 1; r >= 0; r--) for (let c = 0; c < N; c++) if (grid[r][c] && grid[r][c].type === "bell") return [r, c]; return null; })()')
        if not pos: print("no bell", pg.evaluate("JSON.stringify({level, nb: countOnBoard(x => x.type === \"bell\"), busy, onMap})")); break
        r, c = pos
        res = pg.evaluate(f'(async () => {{ const b4 = goals.find(g => g.kind === "bells").left; await trySwap({r}, {c}, {r + 1}, {c}); return [b4, goals.find(g => g.kind === "bells").left, moves]; }})()')
        print('push bell at', pos, '-> bells left before/after, moves:', res, 'check', pg.evaluate('T_check()')[:2])
        if step == 5: pg.screenshot(path=D + '/bell_mid.png')
    print('errors:', errs)
    b.close()
