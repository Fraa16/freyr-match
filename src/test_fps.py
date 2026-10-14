import os, sys
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
H = open(D + '/harness.js').read()
NOFX = len(sys.argv) > 1
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []; __import__('veteran').veteran(pg)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/game.html')
    pg.evaluate('() => { localStorage.clear(); localStorage.setItem("wm-level", 3); }'); pg.reload(); pg.wait_for_timeout(1200)
    if NOFX: pg.add_style_tag(content='.mapsvg g[filter]{filter:none}')
    pg.evaluate('openLevel(maxLevel)'); pg.wait_for_timeout(600); pg.click('#introBtn'); pg.wait_for_timeout(700)
    pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    pg.evaluate('''() => { T_setup(1, [[5,1],[5,2],[6,3]]); T_goalNext(); moves = 9; goals.forEach(g => { g.left = 0; }); milk = milk.map(r => r.map(() => 0)); for (const row of grid) for (const x of row) if (x && x.type === "box") x.type = 0; updateHud(); trySwap(6,3,5,3); }''')
    pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=60000); pg.wait_for_timeout(1200)
    pg.evaluate('() => { window.__fr = []; const f = t => { window.__fr.push(t); if (window.__fr.length < 600) requestAnimationFrame(f); }; requestAnimationFrame(f); }')
    pg.click('#endBtn'); pg.wait_for_timeout(5500)
    fr = pg.evaluate('window.__fr')
    d = [fr[i + 1] - fr[i] for i in range(len(fr) - 1)]
    span = (fr[-1] - fr[0]) / 1000
    print('nofx' if NOFX else 'gloss', 'frames', len(fr), 'over %.1fs -> %.1f fps, worst frame %.0f ms, frames >50ms: %d' % (span, len(fr) / span, max(d), sum(1 for x in d if x > 50)))
    print('errors', errs)
    b.close()
