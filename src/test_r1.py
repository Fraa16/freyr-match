import os, sys
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
H = open(D + '/harness.js').read()
OUT = D + '/r1_'
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
def fresh(pg, setup='1'):
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear()'); pg.evaluate(setup); pg.reload(); pg.wait_for_timeout(900)
def start(pg, L=None):
    pg.evaluate(WAIT_MAP)
    pg.evaluate(f"() => {{ if (!document.getElementById('introOv').classList.contains('show')) openLevel({L or 'maxLevel'}); }}")
    pg.wait_for_timeout(600)
def idle(pg):
    pg.evaluate('T_waitIdle(20000)')
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); __import__('veteran').veteran(pg)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    # 1 level 1: card, board, a few hinted moves
    fresh(pg, 'localStorage.setItem("wm-level", 9)')
    start(pg)
    pg.screenshot(path=OUT + 'intro1.png')
    pg.click('#introBtn'); pg.wait_for_timeout(900)
    pg.add_script_tag(content=H)
    pg.evaluate('goals[0].left = 99; updateHud()')
    print('L9 colors', pg.evaluate('COLORS'), 'goals', pg.evaluate('JSON.stringify(goals)'), 'moves', pg.evaluate('moves'), 'busy', pg.evaluate('busy'))
    pg.screenshot(path=OUT + 'game1.png')
    for i in range(4):
        pg.evaluate('(async () => { const m = bestMove(); await trySwap(m.r, m.c, m.r2, m.c2); })()')
        idle(pg)
    print('after 4 moves: moves', pg.evaluate('moves'), 'purr', pg.evaluate('purr'), 'score', pg.evaluate('score'), 'T_check', pg.evaluate('T_check()'))
    # 2 the pounce
    pg.evaluate('() => { purr = PURR_MAX; purrNew = true; updateHud(); purrNotice(); }'); pg.wait_for_timeout(700)
    pg.screenshot(path=OUT + 'charged.png')
    pg.click('#mascot'); pg.wait_for_timeout(300)
    print('aim after mascot click:', pg.evaluate('aim && aim.kind'))
    bb = pg.evaluate('(() => { const b = boardEl.getBoundingClientRect(); return [b.left, b.top, b.width]; })()')
    cx, cy = bb[0] + bb[2] * (3.5 / 8), bb[1] + bb[2] * (4.5 / 8)
    pg.mouse.move(cx, cy); pg.wait_for_timeout(200)
    pg.screenshot(path=OUT + 'aim_pounce.png')
    mv = pg.evaluate('moves')
    pg.mouse.click(cx, cy); pg.wait_for_timeout(250); pg.screenshot(path=OUT + 'pounce_mid.png')
    idle(pg)
    print('pounce: moves before/after', mv, pg.evaluate('moves'), 'purr', pg.evaluate('purr'), 'T_check', pg.evaluate('T_check()'))
    # 3 the pause menu
    pg.click('#pauseBtn'); pg.wait_for_timeout(500); pg.screenshot(path=OUT + 'pause.png')
    pg.click('#pauseGo'); pg.wait_for_timeout(300)
    print('pause closed', not pg.evaluate("document.getElementById('pauseOv').classList.contains('show')"))
    # 4 loss card with streak at stake
    pg.evaluate('() => { winStreak = 4; treats = 70; moves = 0; showEnd(false); }'); pg.wait_for_timeout(900)
    pg.screenshot(path=OUT + 'loss.png')
    pg.click('#rescueBtn'); pg.wait_for_timeout(500)
    print('rescued: moves', pg.evaluate('moves'), 'treats', pg.evaluate('treats'), 'rescues', pg.evaluate('rescues'))
    pg.evaluate('() => { moves = 0; showEnd(false); }'); pg.wait_for_timeout(700)
    print('second rescue label:', pg.evaluate("document.getElementById('rescueBtn').textContent"), 'disabled', pg.evaluate("document.getElementById('rescueBtn').disabled"))
    pg.click('#endMap'); pg.wait_for_timeout(700)
    print('after leaving loss: streak', pg.evaluate('winStreak'), 'fails', pg.evaluate('JSON.stringify(fails)'), 'onMap', pg.evaluate('onMap'))
    # 5 tools: level 12 with all three unlocked
    fresh(pg, 'localStorage.setItem("wm-level", 48); localStorage.setItem("wm-treats", 50); localStorage.setItem("wm-streak", 3)')
    pg.screenshot(path=OUT + 'map12.png')
    start(pg)
    pg.screenshot(path=OUT + 'intro12.png')
    pg.add_script_tag(content=H)
    pg.click('#introBtn'); pg.wait_for_timeout(1400); pg.screenshot(path=OUT + 'gifts12.png')
    idle(pg); pg.wait_for_timeout(600)
    pg.evaluate('goals.forEach(g => { if (g.kind === "bells") { g.left = 99; } }); updateHud()')
    print('inv', pg.evaluate('JSON.stringify(inv)'), 'gifts on board', pg.evaluate('T_kinds().filter(k => ["laser","cat","nip"].includes(k[2])).length'))
    pg.screenshot(path=OUT + 'tools12.png')
    # paw on a cell
    pg.click('.tool[data-id="paw"]'); pg.wait_for_timeout(250)
    print('aim paw', pg.evaluate('aim && aim.kind'))
    cx, cy = bb[0] + bb[2] * (2.5 / 8), bb[1] + bb[2] * (6.5 / 8)
    bb = pg.evaluate('(() => { const b = boardEl.getBoundingClientRect(); return [b.left, b.top, b.width]; })()')
    cx, cy = bb[0] + bb[2] * (2.5 / 8), bb[1] + bb[2] * (6.5 / 8)
    mv = pg.evaluate('moves'); pg.mouse.click(cx, cy); pg.wait_for_timeout(200); pg.screenshot(path=OUT + 'paw_mid.png'); idle(pg)
    print('paw: moves', mv, '->', pg.evaluate('moves'), 'inv', pg.evaluate('JSON.stringify(inv)'), pg.evaluate('T_check()'))
    pg.click('.tool[data-id="claw"]'); pg.wait_for_timeout(200)
    pg.mouse.move(bb[0] + bb[2] * (4.5 / 8), bb[1] + bb[2] * (3.5 / 8)); pg.wait_for_timeout(200); pg.screenshot(path=OUT + 'aim_claw.png')
    pg.mouse.click(bb[0] + bb[2] * (4.5 / 8), bb[1] + bb[2] * (3.5 / 8)); pg.wait_for_timeout(300); pg.screenshot(path=OUT + 'claw_mid.png'); idle(pg)
    print('claw: inv', pg.evaluate('JSON.stringify(inv)'), pg.evaluate('T_check()'))
    # nudge: swap two treats that make no match
    pg.click('.tool[data-id="swap"]'); pg.wait_for_timeout(200)
    pair = pg.evaluate('''(() => { for (let r = 0; r < N; r++) for (let c = 0; c < N - 1; c++) { const a = grid[r][c], b2 = grid[r][c + 1]; if (!canSwap(a) || !canSwap(b2) || !isNormal(a.type) || !isNormal(b2.type) || a.type === b2.type) continue; sw(r, c, r, c + 1); const m = findMatches().cells.size; sw(r, c, r, c + 1); if (!m) return [r, c, a.id, b2.id]; } return null; })()''')
    mv = pg.evaluate('moves')
    pg.evaluate(f'tap({pair[0]}, {pair[1]})'); pg.evaluate(f'tap({pair[0]}, {pair[1] + 1})'); idle(pg)
    print('nudge: moves', mv, '->', pg.evaluate('moves'), 'swapped', pg.evaluate(f'grid[{pair[0]}][{pair[1]}].id === {pair[3]} && grid[{pair[0]}][{pair[1] + 1}].id === {pair[2]}'), 'inv', pg.evaluate('JSON.stringify(inv)'))
    # buying a tool: paw is at 1, use it, then buy one
    pg.evaluate('() => { inv.paw = 0; drawTools(); }')
    pg.click('.tool[data-id="paw"]'); pg.wait_for_timeout(200); pg.screenshot(path=OUT + 'ask.png')
    t0 = pg.evaluate('treats'); pg.click('.tool[data-id="paw"]'); pg.wait_for_timeout(200)
    print('bought paw: treats', t0, '->', pg.evaluate('treats'), 'aim', pg.evaluate('aim && aim.kind'), 'inv', pg.evaluate('JSON.stringify(inv)'))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    print('escape cancels aim:', pg.evaluate('aim'))
    # select an extra: preview
    ex = pg.evaluate('T_kinds().find(k => k[2] === "cat" || k[2] === "nip")')
    if ex:
        pg.evaluate(f'tap({ex[0]}, {ex[1]})'); pg.wait_for_timeout(300); pg.screenshot(path=OUT + 'preview.png')
        print('preview cells', pg.evaluate('pvEls.length'), ex)
        pg.evaluate('clearSel()')
    # hint
    pg.evaluate('showHint()'); pg.wait_for_timeout(200)
    print('hint tiles', pg.evaluate('document.querySelectorAll(".tile.hint").length'))
    # 6 win with streak line
    pg.evaluate('() => { goals.forEach(g => { if (g.kind === "collect" || g.kind === "bells") g.left = 0; }); for (const row of grid) for (const x of row) if (x) { x.locked = false; if (x.type === "box" || x.type === "wet") { x.type = 0; } } for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { milk[r][c] = 0; if (mask[r][c]) cover[r][c] = 1; } render(false); afterTurn(); }')
    pg.wait_for_timeout(9000)
    pg.screenshot(path=OUT + 'win.png')
    print('win: streak', pg.evaluate('winStreak'), 'end title', pg.evaluate("document.getElementById('endTitle').textContent"), 'jar', pg.evaluate("document.getElementById('jarLine').textContent"))
    # 7 map with hard levels and streak badge
    fresh(pg, 'localStorage.setItem("wm-level", 29); localStorage.setItem("wm-streak", 4)')
    pg.evaluate(WAIT_MAP); pg.evaluate('scrollMapTo(30, .5)'); pg.wait_for_timeout(400)
    pg.screenshot(path=OUT + 'map9.png')
    fresh(pg, 'localStorage.setItem("wm-level", 20); localStorage.setItem("wm-streak", 1)')
    pg.evaluate(WAIT_MAP); pg.wait_for_timeout(300); pg.screenshot(path=OUT + 'map20.png')
    start(pg); pg.screenshot(path=OUT + 'intro20.png')
    # 8 plaster after two losses
    fresh(pg, 'localStorage.setItem("wm-level", 6); localStorage.setItem("wm-fails", JSON.stringify({6: 4}))')
    start(pg); pg.screenshot(path=OUT + 'intro_help.png')
    pg.add_script_tag(content=H)
    print('help', pg.evaluate('JSON.stringify(help)'), 'moves', pg.evaluate('moves'), 'cfg.moves', pg.evaluate('cfg.moves'))
    pg.click('#introBtn'); pg.wait_for_timeout(2600)
    print('plaster laser on board', pg.evaluate('T_kinds().filter(k => k[2] === "laser").length'))
    # 9 abandoned try counts as a loss on the next load
    pg.goto('file://' + D + '/game.html'); pg.wait_for_timeout(900)
    print('after reload mid-level: fails', pg.evaluate('JSON.stringify(fails)'), 'try', pg.evaluate('localStorage.getItem("wm-try")'))
    print('errors:', errs)
    b.close()
