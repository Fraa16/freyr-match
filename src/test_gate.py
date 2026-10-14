"""nothing shows up before its lesson: extras, the purr meter, golden treats, tools, boosts, streak, chest"""
import json, os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
H = open(D + '/harness.js').read()
SCEN = [('square', 0, [(2, 2), (2, 3), (3, 2), (4, 3)], (4, 3, 3, 3)),
        ('four', 1, [(5, 1), (5, 2), (5, 4), (4, 3)], (4, 3, 5, 3)),
        ('five', 3, [(6, 0), (6, 1), (6, 3), (6, 4), (5, 2)], (5, 2, 6, 2)),
        ('L', 4, [(1, 1), (2, 1), (3, 2), (3, 3), (4, 1)], (4, 1, 3, 1))]
EXPECT = {1: [None, None, None, None], 2: [None, 'cat', 'cat', None], 3: ['laser', 'cat', 'cat', None],
          5: ['laser', 'cat', 'cat', 'nip'], 7: ['laser', 'cat', 'bowl', 'nip']}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844}); __import__('veteran').veteran(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 1)'); pg.reload(); pg.wait_for_timeout(700)
    pg.evaluate("""async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }""")
    pg.evaluate('openLevel(1)'); pg.wait_for_timeout(400); pg.click('#introBtn'); pg.wait_for_timeout(500)
    pg.add_script_tag(content=H); pg.evaluate('T_waitIdle()')
    pg.evaluate('''() => { const orig = extrasFor; window.T_spawn = []; window.extrasFor = (m, sk) => { const out = orig(m, sk); T_spawn.push([...out].map(([k, v]) => v.kind)); return out; }; }''')
    bad = 0
    for ml, exp in EXPECT.items():
        got = []
        for (name, T, cells, sw) in SCEN:
            pg.evaluate(f'maxLevel = {ml}; moves = 30; goals = [{{kind: "collect", type: 5, n: 99, left: 99}}]; updateHud()')
            pg.evaluate(f'T_setup({T}, {json.dumps(cells)})'); pg.evaluate('T_spawn.length = 0')
            pg.evaluate(f'trySwap({sw[0]},{sw[1]},{sw[2]},{sw[3]})'); pg.wait_for_timeout(80); pg.evaluate('T_waitIdle()')
            first = pg.evaluate('(T_spawn[0] || [])[0] || null'); got.append(first)
        ok = got == exp; bad += not ok
        print('maxLevel', ml, 'square/four/five/L ->', got, 'OK' if ok else 'FAIL expected %s' % exp)
    # the purr meter: off before level 9
    for ml in (8, 9):
        pg.evaluate(f'maxLevel = {ml}; purr = 0; drawPurr()')
        pg.evaluate('T_setup(5, [[5,1],[5,2],[4,3]])'); pg.evaluate('trySwap(4,3,5,3)'); pg.wait_for_timeout(80); pg.evaluate('T_waitIdle()')
        print('maxLevel', ml, 'purr after eating cream snacks:', pg.evaluate('purr'), 'purr row hidden:', pg.evaluate("document.getElementById('purrRow').hidden"))
    pg.evaluate('maxLevel = 8'); pg.evaluate('tryPounce()')
    print('maxLevel 8, tap on Freyr starts aiming?', pg.evaluate('!!aim'))
    # golden treats, tools, boosts on the level card
    for ml in (27, 28):
        pg.evaluate(f'maxLevel = {ml}; level = {ml}; startLevel()')
        print('maxLevel', ml, 'golden treats on:', pg.evaluate('cfg.gold'), 'gold on board:', pg.evaluate('countOnBoard(x => x.gold)'))
    for ml in (15, 16, 33, 43, 97):
        pg.evaluate(f'maxLevel = {ml}; drawTools()')
        print('maxLevel', ml, 'tools shown:', pg.evaluate("[...document.querySelectorAll('#tools .tool')].map(b => b.dataset.id)"))
    pg.evaluate("document.getElementById('introOv').classList.remove('show')")
    for ml in (25, 26):
        pg.evaluate(f'treats = 100; maxLevel = {ml}; level = {ml}; startLevel()'); pg.wait_for_timeout(300)
        print('maxLevel', ml, 'boosts on card:', pg.evaluate("!document.getElementById('boostWrap').hidden"), 'legend:', pg.evaluate("[...document.querySelectorAll('#legend b')].map(b => b.textContent)"))
        pg.evaluate("document.getElementById('introOv').classList.remove('show')")
    for ml in (21, 22):
        pg.evaluate(f'maxLevel = {ml}; winStreak = 0; registerWin({ml})')
        print('maxLevel', ml, 'streak counts a win:', pg.evaluate('winStreak'))
    print('errors:', errs, '| gating failures:', bad)
    b.close()
