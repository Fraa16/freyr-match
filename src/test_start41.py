"""V41 fix: no treats in a row at rest. Level start with every start extra (shop, lucky streak, plaster): after the
extras land, nothing may line up (an extra counts as its treat). Also after a reshuffle, and when presents open.
usage: GAME=... python3 test_start41.py [rounds]"""
import os, sys, json, random
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
GAME = os.environ.get('GAME', 'game.html')
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
fails = []
def ok(m, c, info=None):
    print(('OK   ' if c else 'FAIL ') + m + ('' if c or info is None else '  ' + json.dumps(info)[:500]))
    if not c: fails.append(m)
LEARN = json.dumps({k: True for k in ['basics','cat','laser','nip','bowl','combo','purr','chest','boosts','bells','milk','boxes','locks','paw','box2','gold','milk2','hard','hard2','claw','blanket','swap','wet','boss','streak','picnic','box3','order','gift','cukes','clock','feather','turbo','superpounce','goldrush']})
START = """async ([L, boost]) => {
  document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); if (!onMap) showMap();
  lives = 5; treats = 999; winStreak = 5;
  openLevel(L); await new Promise(r => setTimeout(r, 300));
  pick = boost; help = { moves: 3, laser: true };
  $('introBtn').click();
  for (let i = 0; i < 200 && (busy || $('introOv').classList.contains('show')); i++) await new Promise(r => setTimeout(r, 50));
  await new Promise(r => setTimeout(r, 300));
  const m = findMatches(), xs = [];
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const x = grid[r][c]; if (x && isPower(x.type)) xs.push(x.type + (x.col != null ? ':' + x.col : '')); }
  return { L, matches: [...m.cells], extras: xs };
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/' + GAME)
    pg.evaluate("(l) => { localStorage.clear(); localStorage.setItem('wm-intro','1'); localStorage.setItem('wm-news41','done'); localStorage.setItem('wm-level','260'); localStorage.setItem('wm-purr-told','1'); localStorage.setItem('wm-music','off'); localStorage.setItem('wm-sound','off'); localStorage.setItem('wm-learn', l); }", LEARN)
    pg.reload(); pg.wait_for_timeout(800)
    pg.evaluate("() => { try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1500)
    rng = random.Random(41); bad = []; n = 0; nx = 0
    levels = list(range(12, 261, 6))
    for rnd_ in range(ROUNDS):
        for L in levels:
            r = pg.evaluate(START, [L, rng.choice(['cat', 'nip', 'laser', 'bowl'])]); n += 1; nx += len(r['extras'])
            if r['matches']: bad.append(r)
    print('   level starts:', n, 'extras placed:', nx)
    ok('no treats in a row after the start extras (%d starts)' % n, not bad, bad[:3])
    # a reshuffle with coloured extras on the board
    rb = pg.evaluate("""async () => { let bad = 0; for (let i = 0; i < 40; i++) { reshuffle(); if (findMatches().cells.size) bad++; } return bad; }""")
    ok('no treats in a row after 40 reshuffles with extras on the board', rb == 0, rb)
    ok('no page errors', not errs, errs[:3])
    b.close()
print('FAILS', len(fails))
