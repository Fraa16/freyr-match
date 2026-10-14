import os, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
H = open(D + '/harness.js').read()
def go(pg, L):
    pg.goto('file://' + D + '/game.html'); pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", {L})'); pg.reload(); pg.wait_for_timeout(800)
    pg.evaluate('openLevel(maxLevel)'); pg.wait_for_timeout(700)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []; __import__('veteran').veteran(pg)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    # blanket intro level
    go(pg, 24); pg.screenshot(path=D + '/f_intro11.png')
    pg.click('#introBtn'); pg.wait_for_timeout(900)
    print('L24 goals', pg.evaluate('JSON.stringify(goals.map(g => [g.kind, remaining(g)]))'))
    pg.add_script_tag(content=H)
    # force a match that includes a covered cell: put three of a kind at row 3 cols 2..4 (3,3 and 3,4 are covered)
    n = pg.evaluate('''() => { T_base(1); grid[3][2] = mk(1); grid[3][3] = mk(1); grid[2][4] = mk(1); render(false); return findMatches().cells.size; }''')
    print('pre-matches', n)
    pg.evaluate('() => { trySwap(2, 4, 3, 4); }'); pg.wait_for_timeout(250); pg.screenshot(path=D + '/f_tuck_mid.png')
    pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(600)
    print('after: cover remaining', pg.evaluate('remaining(goals.find(g => g.kind === "cover"))'), 'check', pg.evaluate('T_check()'))
    pg.screenshot(path=D + '/f_tuck.png')
    # wet food level
    go(pg, 36); pg.screenshot(path=D + '/f_intro16.png')
    pg.click('#introBtn'); pg.wait_for_timeout(900)
    pg.add_script_tag(content=H)
    print('L36 goals', pg.evaluate('JSON.stringify(goals.map(g => [g.kind, remaining(g)]))'))
    # a move far from wet food -> it should spread
    pg.evaluate('''() => { T_base(3); grid[7][0] = mk(3); grid[7][1] = mk(3); grid[6][2] = mk(3); grid[2][2] = {type:'wet', id: ++idc, hp:1, gold:false, locked:false}; grid[2][5] = {type:'wet', id: ++idc, hp:1, gold:false, locked:false}; grid[5][2] = {type:'wet', id: ++idc, hp:1, gold:false, locked:false}; grid[5][5] = {type:'wet', id: ++idc, hp:1, gold:false, locked:false}; render(false); }''')
    w0 = pg.evaluate('countOnBoard(x => x.type === "wet")')
    pg.evaluate('() => { trySwap(6, 2, 7, 2); }'); pg.wait_for_timeout(300); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(300)
    w1 = pg.evaluate('countOnBoard(x => x.type === "wet")')
    pg.screenshot(path=D + '/f_spread.png')
    print('wet before/after a far move:', w0, w1, 'bubble:', pg.evaluate('document.getElementById("bubble").textContent'), 'check', pg.evaluate('T_check()'))
    # a move next to wet food -> clears it, no spread
    pg.evaluate('''() => { const W = () => ({type:'wet', id: ++idc, hp:1, gold:false, locked:false}); T_base(3); grid[2][2] = W(); grid[3][1] = mk(3); grid[3][2] = mk(3); grid[4][3] = mk(3); render(false); }''')
    w0 = pg.evaluate('countOnBoard(x => x.type === "wet")')
    pg.evaluate('() => { trySwap(4, 3, 3, 3); }'); pg.wait_for_timeout(300); pg.evaluate('T_waitIdle()'); pg.wait_for_timeout(300)
    print('wet before/after an adjacent match:', w0, pg.evaluate('countOnBoard(x => x.type === "wet")'), 'check', pg.evaluate('T_check()'))
    # picnic level intro
    go(pg, 38); pg.screenshot(path=D + '/f_intro18.png')
    pg.click('#introBtn'); pg.wait_for_timeout(900); pg.screenshot(path=D + '/f_board18.png')
    print('L38 goals', pg.evaluate('JSON.stringify(goals.map(g => [g.kind, remaining(g)]))'))
    # no lives nap
    pg.goto('file://' + D + '/game.html'); pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 4); localStorage.setItem("wm-lives", 0); localStorage.setItem("wm-life-ts", Date.now() - 60000)'); pg.reload(); pg.wait_for_timeout(800)
    pg.click('.mnode.cur'); pg.wait_for_timeout(700); pg.screenshot(path=D + '/f_nap.png')
    print('errors:', errs)
    b.close()
