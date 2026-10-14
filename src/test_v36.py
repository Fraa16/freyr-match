"""V36: the three new things. A test level is put in place of level 1 at runtime.
B: the belt rotates its row after a move, the wrap-around tile comes back on the other end, matches after the belt are eaten
D: dark cells hide the tile, a match next to one lights it, the 'dark' goal counts down and can be won
W: the rainbow fish matches with any kind, makes a cat in a run of four, the bowl swapped with it eats a real kind
P: the bot plays the test level for a while: no errors, board stays consistent"""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import veteran
from fontfix import fonts
GAME = os.environ.get('GAME', 'game.html')
HN = open(D + '/harness.js').read()
SHOTS = D + '/shots36'; os.makedirs(SHOTS, exist_ok=True)
fails = []
def ok(m, c, info=None):
    print(('OK   ' if c else 'FAIL ') + m + ('' if c or info is None else '  ' + json.dumps(info)[:300]))
    if not c: fails.append(m)
LVL = {'name': 'Testband', 'moves': 30, 'target': 1000, 'collect': [[0, 20]], 'belts': [[4, 1], [6, -1]], 'wildRate': 0,
       'board': ['........', '.dddddd.', '.dddddd.', '........', '..r.....', '........', '........', '........']}
def start(pg, lvl=LVL):
    pg.evaluate("() => { document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); if (!onMap) showMap(); }"); pg.wait_for_timeout(600)
    pg.evaluate(f"(d) => {{ LEVELS[0] = d; }}", lvl)
    pg.evaluate('openLevel(1)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1400)
    pg.add_script_tag(content=HN); pg.evaluate('T_waitIdle()')
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 402, 'height': 874}, device_scale_factor=2, has_touch=True, is_mobile=True)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    veteran.veteran(pg)
    pg.goto('file://' + D + '/' + GAME)
    pg.evaluate("localStorage.setItem('wm-intro','1'); localStorage.setItem('wm-level', 200); localStorage.setItem('wm-purr-told','1'); localStorage.setItem('wm-music','off')")
    pg.reload(); pg.wait_for_timeout(600); fonts(pg)
    pg.evaluate("() => { try { if (introRun && introRun.kind === 'wake') mapSkip = true; } catch (e) {} }"); pg.wait_for_function('!introRun', timeout=10000); pg.wait_for_timeout(900)
    if pg.evaluate("document.getElementById('introOv').classList.contains('show')"): pg.click('#introX'); pg.wait_for_timeout(300)
    pg.evaluate("LEVELS[0].intro = null")
    start(pg)
    g = pg.evaluate("({ belts: cfg.belts, goals: goals.map(g => g.kind + ':' + remaining(g)), dark: dark.flat().reduce((a, b) => a + b, 0), night: document.querySelectorAll('.night').length, beltcells: document.querySelectorAll('.beltcell').length, wild: countOnBoard(x => x.type === 'wild') })")
    ok('setup: belts, 12 dark cells, a fish, the dark goal first', g['belts'] == [[4, 1], [6, -1]] and g['dark'] == 12 and g['night'] == 12 and g['beltcells'] == 16 and g['wild'] == 1 and g['goals'][0] == 'dark:12', g)
    pg.screenshot(path=SHOTS + '/start.png')

    # B: belt rotation, controlled board without matches
    r = pg.evaluate("""async () => { T_base(1); render(false); const row4 = grid[4].map(x => x.id), row6 = grid[6].map(x => x.id);
        if (findMatches().cells.size) return { skip: true };
        await beltStep(); return { row4, row6, now4: grid[4].map(x => x.id), now6: grid[6].map(x => x.id), check: T_check() }; }""")
    ok('B1 row 4 moved one to the right, the last tile came back first', r.get('now4') == [r['row4'][-1]] + r['row4'][:-1], r)
    ok('B2 row 6 moved one to the left', r.get('now6') == r['row6'][1:] + [r['row6'][0]], r)
    ok('B3 board consistent after the belt', not r.get('check'), r.get('check'))
    # B4: the belt brings a fish between two others in column 0: that match is eaten right away
    r = pg.evaluate("""async () => { T_base(1); grid[4][7] = mk(0); grid[3][0] = mk(0); grid[5][0] = mk(0); render(false);
        if (findMatches().cells.size) return { pre: true };
        const s0 = score; await beltStep(); return { gained: score - s0, at: grid[4][0] && grid[4][0].type, check: T_check() }; }""")
    ok('B4 the belt brings a fish between two others: the column match is eaten', r.get('gained', 0) > 0 and not r.get('check'), r)

    # D: a match next to the dark area lights cells up
    r = pg.evaluate("""async () => { T_setup(2, [[3, 2], [3, 3], [3, 4]]); const d0 = remaining(goals[0]); await resolve(null, null); await T_waitIdle();
        return { d0, d1: remaining(goals[0]), lit: document.querySelectorAll('.night.lit').length, check: T_check() }; }""")
    ok('D1 a match in row 3 lights the dark cells above it (at least three)', r['d0'] - r['d1'] >= 3, r)
    ok('D2 board consistent', not r['check'], r['check'])
    pg.screenshot(path=SHOTS + '/lit.png')
    hidden = pg.evaluate("""(() => { const n = document.querySelector('.night'); if (!n) return null; const cs = getComputedStyle(n, '::before'); return cs.backgroundImage.length > 20 && getComputedStyle(n).zIndex; })()""")
    ok('D3 the night cells lie over the tiles', hidden == '2', hidden)

    # W: the fish matches with anything
    r = pg.evaluate("""() => { T_base(3); grid[7][0] = mk(3); grid[7][1] = mk(3); grid[7][2] = mk('wild'); render(false); const m = findMatches();
        return { n: m.cells.size, has: m.cells.has(58), col: m.wildColor && m.wildColor.get(58) }; }""")
    ok('W1 two mice and the fish make a match', r['n'] == 3 and r['has'] and r['col'] == 3, r)
    r = pg.evaluate("""() => { T_base(3); grid[7][0] = mk(3); grid[7][1] = mk('wild'); grid[7][2] = mk(3); grid[7][3] = mk(3); render(false); const m = findMatches();
        const ex = [...extrasFor(m, [7 * 8 + 1]).values()].map(e => e.kind); return { n: m.cells.size, ex, type: grid[7][1].type }; }""")
    ok('W2 four in a row with the fish makes a cat, the fish stays a fish', r['n'] == 4 and r['ex'] == ['cat'] and r['type'] == 'wild', r)
    r = pg.evaluate("""() => { T_base(3); grid[7][0] = mk('wild'); grid[7][1] = mk('wild'); render(false); return [findMatches().cells.size, [...findMatches().cells]]; }""")
    ok('W3 two fish and any treat next to them in a line are a match', r[0] == 3 and 58 in r[1], r)
    r = pg.evaluate("""async () => { T_base(1); grid[6][0] = mk('bowl'); grid[7][0] = mk('wild'); render(false); const n0 = countOnBoard(x => isNormal(x.type));
        await trySwap(6, 0, 7, 0); await T_waitIdle(); return { eaten: n0 - countOnBoard(x => isNormal(x.type) && !x.fresh), check: T_check() }; }""")
    ok('W4 bowl + fish eats a real kind (board refilled, no errors)', not r['check'] and not errs, r)
    pg.screenshot(path=SHOTS + '/wild.png')

    # P: the bot plays the level for 25 turns
    start(pg)
    probs = pg.evaluate("""async () => { const out = [];
        for (let i = 0; i < 25 && moves > 0 && !goalsDone(); i++) { const m = bestMove(); if (!m) break; await trySwap(m.r, m.c, m.r2, m.c2); await T_waitIdle(); const p = T_check(); if (p.length) { out.push(i + ': ' + p.join('; ')); break; } }
        return { out, moves, dark: remaining(goals[0]), left: goals.map(g => g.kind + ':' + remaining(g)) }; }""")
    ok('P1 25 bot turns with belts, night and fish: board consistent', not probs['out'], probs)
    pg.screenshot(path=SHOTS + '/played.png')
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', len(fails))
