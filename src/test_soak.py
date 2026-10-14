import json, sys, os, random
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
GAME = 'file://' + D + '/' + (sys.argv[1] if len(sys.argv) > 1 else 'game.html')
H = open(D + '/harness.js').read() + '''
window.T_allMoves = function () {
  const out = [];
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const a = grid[r][c]; if (!canSwap(a)) continue;
    for (const [dr, dc] of [[0, 1], [1, 0]]) {
      const r2 = r + dr, c2 = c + dc;
      if (r2 >= N || c2 >= N || !canSwap(grid[r2][c2])) continue;
      if (isPower(a.type) || isPower(grid[r2][c2].type)) { out.push([r, c, r2, c2]); continue; }
      sw(r, c, r2, c2); const ok = findMatches().cells.size > 0; sw(r, c, r2, c2);
      if (ok) out.push([r, c, r2, c2]);
    }
  }
  return out;
};
window.T_seed = function (kind) {
  const spots = []; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const x = grid[r][c]; if (x && isNormal(x.type) && !x.locked) spots.push([r, c]); }
  const [r, c] = spots[Math.floor(Math.random() * spots.length)];
  const old = grid[r][c], sp = mk(kind); if (kind === 'cat') sp.dir = Math.random() < .5 ? 'h' : 'v';
  els.get(old.id).remove(); els.delete(old.id); grid[r][c] = sp; tileEl(sp); place(sp, r, c);
};
'''
random.seed(7)
LEVELS = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '1,3,4,5,7,9').split(',')]
MOVES = int(sys.argv[3]) if len(sys.argv) > 3 else 14
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}); __import__('veteran').veteran(pg)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    for L in LEVELS:
        pg.goto(GAME); pg.evaluate(f'localStorage.clear(); localStorage.setItem("wm-level", "{L}")'); pg.reload(); pg.wait_for_timeout(800)
        pg.evaluate("async () => { mapSkip = true; for (let i = 0; i < 120 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); if (!document.getElementById('introOv').classList.contains('show')) openLevel(maxLevel); }"); pg.wait_for_timeout(500)
        pg.click('#introBtn'); pg.wait_for_timeout(300)
        pg.add_script_tag(content=H)
        info = pg.evaluate('({goals: goals.map(g => g.kind + (g.type ?? "")), boxes: countOnBoard(x => x.type === "box"), locks: countOnBoard(x => x.locked)})')
        made, bad, kinds = 0, [], {}
        for i in range(MOVES):
            if pg.evaluate('document.querySelector("#endOv.show") !== null'): break
            pg.evaluate('moves = Math.max(moves, 3)')
            if i % 3 == 2: pg.evaluate(f'T_seed("{random.choice(["laser","cat","nip","bowl"])}")')
            mv = pg.evaluate('T_allMoves()')
            if not mv: bad.append('no moves'); break
            # prefer extras sometimes so combos happen
            ext = [m for m in mv if pg.evaluate(f'isPower(grid[{m[0]}][{m[1]}].type) || isPower(grid[{m[2]}][{m[3]}].type)')]
            m = random.choice(ext if ext and random.random() < .6 else mv)
            pg.evaluate(f'() => {{ window.__done = false; trySwap({m[0]},{m[1]},{m[2]},{m[3]}).then(() => window.__done = true); }}')
            pg.wait_for_function('window.__done === true', timeout=30000)
            made += 1
            for k in pg.evaluate('T_kinds()'): kinds[k[2]] = kinds.get(k[2], 0) + 1
            probs = pg.evaluate('T_check()')
            if probs and not pg.evaluate('document.querySelector("#endOv.show") !== null'): bad.append((i, probs[:3]))
        after = pg.evaluate('({boxes: countOnBoard(x => x.type === "box"), locks: countOnBoard(x => x.locked), score, goalsLeft: goals.map(remaining)})')
        print('level', L, info, 'moves made', made, '->', after, 'problems:', bad[:3])
    print('errors:', errs)
    b.close()
