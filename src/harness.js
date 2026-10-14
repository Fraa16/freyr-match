// test helpers injected into the game page
window.T_base = function (T) {
  const others = [0, 1, 2, 3, 4, 5].filter(x => x !== T);
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    grid[r][c] = mask[r][c] ? mk(others[(2 * r + c) % 5]) : null;
  }
};
window.T_setup = function (T, cells, extras) {
  T_base(T);
  for (const [r, c] of cells) if (mask[r][c]) grid[r][c] = mk(T);
  for (const [r, c, kind, dir] of (extras || [])) { const x = mk(kind); if (dir) x.dir = dir; grid[r][c] = x; }
  render(false);
  return findMatches().cells.size;
};
window.T_check = function () {
  const probs = [];
  const tiles = [...boardEl.querySelectorAll('.tile')];
  let cells = 0; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (mask[r][c]) cells++;
  if (tiles.length !== cells) probs.push('tiles in DOM: ' + tiles.length + ' / ' + cells);
  if (els.size !== cells) probs.push('els size: ' + els.size + ' / ' + cells);
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    if (!mask[r][c]) { if (grid[r][c]) probs.push('tile in hole ' + r + ',' + c); continue; }
    const x = grid[r][c];
    if (!x) { probs.push('empty ' + r + ',' + c); continue; }
    const el = els.get(x.id);
    if (!el) { probs.push('no el ' + r + ',' + c); continue; }
    if (!el.isConnected) probs.push('detached ' + r + ',' + c);
    if (+el.dataset.r !== r || +el.dataset.c !== c) probs.push('pos ' + r + ',' + c);
    if (el.classList.contains('pop')) probs.push('popped el still in grid ' + r + ',' + c);
  }
  return probs;
};
window.T_kinds = function () {
  const out = [];
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const x = grid[r][c]; if (x && !isNormal(x.type) && x.type !== 'box') out.push([r, c, x.type, x.dir || '']); }
  return out;
};
window.T_waitIdle = async function (ms = 15000) {
  const t0 = Date.now();
  while (busy && Date.now() - t0 < ms) await new Promise(r => setTimeout(r, 50));
  return !busy;
};
// the next match of T finishes the level (wins are goals-only now)
window.T_goalNext = function (T = 1) { goals = [{ kind: 'collect', type: T, n: 3, left: 3 }]; lastRem = []; updateHud(); };
