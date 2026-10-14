/* ===================== V36: three new things for the levels 161-260 ===================== */
// Förderband: a row that moves every treat on it one cell along after each move (what falls off one end comes back at the other).
// Nacht-Felder: dark cells ('d' in the board) hide what lies under them; a match on or right next to one lights it up. Goal: light them all.
// Regenbogen-Fisch: a treat ('r' in the board, or now and then from above) that matches with every kind.
const WILD = 'wild';
let dark = [], darkEls = [], toldBelt = false, toldDark = false, toldWild = false;

const RAIN_SVG = `<svg viewBox="0 0 100 100"><defs><linearGradient id="gRainFish" x1="0" y1=".2" x2="1" y2=".8">` +
  `<stop offset="0" stop-color="#FF5FA8"/><stop offset=".24" stop-color="#FFA23B"/><stop offset=".46" stop-color="#FFE14D"/><stop offset=".68" stop-color="#4CD38E"/><stop offset=".86" stop-color="#3FA7FF"/><stop offset="1" stop-color="#8B5CFF"/></linearGradient></defs>` +
  `<path d="M64 50 L92 29 Q85 50 92 71Z" fill="url(#gRainFish)" ${OL('#5B2A9E')}/>` +
  `<path d="M7 50 Q35 12 72 50 Q35 88 7 50Z" fill="url(#gRainFish)" ${OL('#5B2A9E')}/>` +
  `<path d="M40 30 Q47 50 40 70 M52 34 Q58 50 52 66" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".55"/>` +
  `<path d="M15 45 Q29 25 54 29 Q34 34 20 49Z" fill="#fff" opacity=".45"/>` +
  `<circle cx="25" cy="47" r="6.4" fill="#fff"/><circle cx="26.4" cy="47.8" r="3.7" fill="#2A0F52"/><circle cx="25" cy="46" r="1.3" fill="#fff"/>` +
  `<path class="rspark" d="M80 12 L82.5 19 L89 21.5 L82.5 24 L80 31 L77.5 24 L71 21.5 L77.5 19Z" fill="#FFF7B0" stroke="#E0A800" stroke-width="1.4" stroke-linejoin="round"/></svg>`;
const MOON_ICON = `<svg viewBox="0 0 100 100"><rect x="8" y="8" width="84" height="84" rx="22" fill="#2B2163" stroke="#14103A" stroke-width="4"/>` +
  `<path d="M60 26 A26 26 0 1 0 74 66 A20 20 0 1 1 60 26Z" fill="#FFE27A" stroke="#C99A1C" stroke-width="3" stroke-linejoin="round"/>` +
  `<circle cx="28" cy="28" r="3.2" fill="#fff"/><circle cx="24" cy="70" r="2.4" fill="#fff" opacity=".8"/><circle cx="78" cy="22" r="2.2" fill="#fff" opacity=".8"/></svg>`;
const BELT_ICON = `<svg viewBox="0 0 100 100"><rect x="6" y="30" width="88" height="40" rx="20" fill="#5C5A78" stroke="#2E2C48" stroke-width="4"/>` +
  `<circle cx="26" cy="50" r="11" fill="#8E8CB0" stroke="#2E2C48" stroke-width="3"/><circle cx="74" cy="50" r="11" fill="#8E8CB0" stroke="#2E2C48" stroke-width="3"/>` +
  `<path d="M42 41 L52 50 L42 59 M54 41 L64 50 L54 59" fill="none" stroke="#FFE27A" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

/* ---------- the rainbow fish matches with every kind ---------- */
const hasWild = () => { for (const row of grid) for (const x of row) if (x && x.type === WILD) return true; return false; };
const findMatchesPlain36 = findMatches;
findMatches = function () {
  if (!hasWild()) return findMatchesPlain36();
  const cells = new Set(), runs = [], squares = [], wildColor = new Map();
  const T = (r, c) => { const x = grid[r][c]; return x ? x.type : null; };
  const scan = (line, dir) => {
    const ts = line.map(([r, c]) => T(r, c)), kinds = new Set(ts.filter(isNormal));
    for (const col of kinds) {
      let i = 0;
      while (i < ts.length) {
        if (ts[i] !== col && ts[i] !== WILD) { i++; continue; }
        let e = i, own = false;
        while (e < ts.length && (ts[e] === col || ts[e] === WILD)) { if (ts[e] === col) own = true; e++; }
        if (own && e - i >= 3) {
          const keys = [];
          for (let j = i; j < e; j++) { const k = line[j][0] * N + line[j][1]; keys.push(k); cells.add(k); if (ts[j] === WILD && !wildColor.has(k)) wildColor.set(k, col); }
          runs.push({ keys, dir });
        }
        i = e;
      }
    }
  };
  for (let r = 0; r < N; r++) scan([...Array(N)].map((_, c) => [r, c]), 'h');
  for (let c = 0; c < N; c++) scan([...Array(N)].map((_, r) => [r, c]), 'v');
  for (let r = 0; r < N - 1; r++) for (let c = 0; c < N - 1; c++) {
    const q = [[r, c], [r, c + 1], [r + 1, c], [r + 1, c + 1]], ts = q.map(([a, b]) => T(a, b));
    if (ts.some(t => t !== WILD && !isNormal(t))) continue;
    const own = [...new Set(ts.filter(isNormal))];
    if (own.length !== 1) continue;
    const keys = q.map(([a, b]) => a * N + b);
    keys.forEach((k, j) => { cells.add(k); if (ts[j] === WILD && !wildColor.has(k)) wildColor.set(k, own[0]); });
    squares.push(keys);
  }
  return { cells, runs, squares, wildColor };
};
// which extra a match earns: the fish counts as the kind it matched with
const extrasForPlain36 = extrasFor;
extrasFor = function (m, swapKeys) {
  if (!m.wildColor || !m.wildColor.size) return extrasForPlain36(m, swapKeys);
  const back = [];
  for (const [k, col] of m.wildColor) { const x = grid[k / N | 0][k % N]; if (x && x.type === WILD) { back.push(x); x.type = col; } }
  try { return extrasForPlain36(m, swapKeys); } finally { back.forEach(x => { x.type = WILD; }); }
};
const iconForPlain36 = iconFor;
iconFor = x => x.type === WILD ? RAIN_SVG : iconForPlain36(x);
const labelForPlain36 = labelFor;
labelFor = function (x) { return x.type === WILD ? 'Regenbogen-Fisch, passt zu jeder Sorte' : labelForPlain36(x); };
// the hint and the bot: matches on or next to dark cells are worth more while there is darkness left
const cellWorthPlain36 = cellWorth;
cellWorth = function (k, X) {
  let v = cellWorthPlain36(k, X);
  const r = k / N | 0, c = k % N;
  if (dark.length && goals.some(g => g.kind === 'dark' && remaining(g) > 0)) {
    if (dark[r] && dark[r][c]) v += 1.2;
    for (const [dr, dc] of D4) if (inB(r + dr, c + dc) && dark[r + dr][c + dc]) { v += 2.2; break; }
  }
  return v;
};

/* ---------- the board: dark cells, fish from the level, belts ---------- */
const newGridPlain36 = newGrid;
newGrid = function () {
  const res = newGridPlain36.apply(this, arguments);
  const B = cfg.board;
  dark = B.map(row => [...row].map(ch => (ch === 'd' ? 1 : 0)));
  let fish = 0;
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (B[r][c] === 'r' && grid[r][c] && isNormal(grid[r][c].type)) { grid[r][c].type = WILD; grid[r][c].gold = false; fish++; }
  if (fish) for (let t = 0; t < 80; t++) {
    const m = findMatches(); if (!m.cells.size) break;
    for (const k of m.cells) { const x = grid[k / N | 0][k % N]; if (x && isNormal(x.type)) x.type = rnd(); }
  }
  return res;
};
function drawNight() {
  boardEl.querySelectorAll('.night').forEach(e => e.remove());
  darkEls = [];
  for (let r = 0; r < N; r++) {
    darkEls.push([]);
    for (let c = 0; c < N; c++) {
      let e = null;
      if (dark[r] && dark[r][c] && mask[r][c]) {
        e = document.createElement('div'); e.className = 'night n' + ((r * 3 + c) % 3);
        e.style.top = (r * STEP) + '%'; e.style.left = (c * STEP) + '%'; boardEl.appendChild(e);
      }
      darkEls[r].push(e);
    }
  }
}
function drawBelts() {
  boardEl.querySelectorAll('.beltcell').forEach(e => e.remove());
  for (const [r, dir] of cfg.belts || []) {
    const cols = []; for (let c = 0; c < N; c++) if (mask[r] && mask[r][c]) cols.push(c);
    cols.forEach((c, i) => {
      const e = document.createElement('div');
      e.className = 'beltcell ' + (dir > 0 ? 'br' : 'bl') + (i === 0 ? ' bs' : '') + (i === cols.length - 1 ? ' be' : '');
      e.style.top = (r * STEP) + '%'; e.style.left = (c * STEP) + '%'; boardEl.prepend(e);
    });
  }
}
const renderBoardPlain36 = renderBoard;
renderBoard = function () { const r = renderBoardPlain36.apply(this, arguments); drawBelts(); drawNight(); return r; };

// a match on or next to a dark cell lights it up (called for every cell a match eats)
function lightAt(r, c, d) {
  let n = 0;
  for (const [rr, cc] of [[r, c], [r + 1, c], [r - 1, c], [r, c + 1], [r, c - 1]]) {
    if (!inB(rr, cc) || !dark[rr] || !dark[rr][cc]) continue;
    dark[rr][cc] = 0; n++;
    const el = darkEls[rr] && darkEls[rr][cc]; if (darkEls[rr]) darkEls[rr][cc] = null;
    later(d, () => {
      if (el) { el.classList.add('lit'); setTimeout(() => el.remove(), 520); }
      const [x, y] = cellXY(rr * N + cc); burst(x, y, 8, 1, ['#FFE27A', '#FFF6C8', '#ffffff', '#B9A8FF'], 'star');
    });
  }
  if (n) {
    score += 20 * n;
    later(d, () => sweep(660, 1320, 0, .12, 'sine', .035));
    if (!toldDark) { toldDark = true; later(d + 200, () => say('Licht an! Ich seh im Dunkeln alles, du jetzt auch ein bisschen.')); }
  }
}

/* ---------- the belts move after every move ---------- */
async function beltStep() {
  if (!cfg.belts || !cfg.belts.length) return false;
  let moved = false;
  for (const [r, dir] of cfg.belts) {
    const cols = [];
    for (let c = 0; c < N; c++) { const x = mask[r] && mask[r][c] && grid[r][c]; if (x && !isStatic(x) && x.type !== 'boss') cols.push(c); }
    if (cols.length < 2) continue;
    const tiles = cols.map(c => grid[r][c]);
    const rot = dir > 0 ? [tiles[tiles.length - 1], ...tiles.slice(0, -1)] : [...tiles.slice(1), tiles[0]];
    cols.forEach((c, i) => {
      const x = rot[i]; grid[r][c] = x;
      const el = els.get(x.id), wrap = dir > 0 ? i === 0 : i === cols.length - 1;
      if (el && wrap) { el.classList.remove('beltwrap'); void el.offsetWidth; el.classList.add('beltwrap'); setTimeout(() => el.classList.remove('beltwrap'), 420); }
      place(x, r, c);
    });
    moved = true;
  }
  if (!moved) return false;
  boardEl.querySelectorAll('.beltcell').forEach(e => { e.classList.remove('run'); void e.offsetWidth; e.classList.add('run'); });
  sweep(150, 230, 0, .22, 'triangle', .03);
  if (!toldBelt) { toldBelt = true; say('Das Band läuft! Nach jedem Zug rutscht alles darauf ein Feld weiter.'); }
  await sleep(300);
  if (findMatches().cells.size) await resolve(null, null);
  return true;
}
const afterTurnPlain36 = afterTurn;
afterTurn = async function () {
  if (moves > 0 && cfg.belts && cfg.belts.length && !goalsDone()) { await beltStep(); updateHud(); }
  return afterTurnPlain36.apply(this, arguments);
};

/* ---------- goals, level config ---------- */
const remainingPlain36 = remaining;
remaining = function (g) {
  if (g.kind === 'dark') { let n = 0; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (dark[r] && dark[r][c] && mask[r] && mask[r][c]) n++; return n; }
  return remainingPlain36(g);
};
const goalIconPlain36 = goalIcon;
goalIcon = g => g.kind === 'dark' ? MOON_ICON : goalIconPlain36(g);
const goalTextPlain36 = goalText;
goalText = function (g, n) { return g.kind === 'dark' ? n + (n === 1 ? ' dunkles Feld' : ' dunkle Felder') + ' ins Licht holen' : goalTextPlain36(g, n); };
const levelConfigPlain36 = levelConfig;
levelConfig = function (L) {
  const c = levelConfigPlain36.apply(this, arguments);
  const span = LEVELS.length - 20, def = LEVELS[L > LEVELS.length ? 20 + (L - LEVELS.length - 1) % span : L - 1];
  c.belts = def.belts || null; c.wildRate = def.wildRate || 0;
  if (def.board.some(row => row.includes('d'))) c.goals.unshift({ kind: 'dark' });
  return c;
};

/* ---------- the level cards for the new things ---------- */
Object.assign(INTRO, {
  belt: () => [BELT_ICON, 'Neu: Förderband', 'Nach jedem Zug rutscht alles auf dem Band ein Feld weiter. Was am Ende runterfällt, kommt vorne wieder drauf. Plan deine Matches mit ein!'],
  dark: () => [MOON_ICON, 'Neu: Nacht-Felder', 'Ein Teil des Felds liegt im Dunkeln. Ein Match auf oder direkt neben einem dunklen Feld macht dort Licht.'],
  wild: () => [RAIN_SVG, 'Neu: Regenbogen-Fisch', 'Der Regenbogen-Fisch passt zu jeder Sorte. Leg ihn zu zwei gleichen Leckerlis, schon ist es ein Match.'],
  mix_beltbells: () => [BELT_ICON, 'Glöckchen auf dem Band', 'Das Band nimmt auch Glöckchen mit. Schieb sie dorthin, wo der Weg nach unten frei ist.'],
  mix_beltdark: () => [MOON_ICON, 'Band in der Nacht', 'Das Band schiebt die Leckerlis durchs Dunkle. Was im Dunkeln liegt, siehst du erst, wenn es wieder rauskommt.'],
  mix_darkfish: () => [MOON_ICON, 'Fische im Dunkeln', 'Regenbogen-Fische passen zu allem, auch im Dunkeln. Ein Match mit ihnen macht genauso Licht.'],
  mix_newfinale: () => [CAT_ICON(), 'Das zweite große Finale', 'Band, Nacht und Regenbogen-Fische, alles auf einmal. Zeig, was du gelernt hast!']
});
// the first fish that is eaten
const resolvePlain36 = resolve;
resolve = async function () {
  const before = toldWild ? 0 : countOnBoard(x => x.type === WILD);
  const r = await resolvePlain36.apply(this, arguments);
  if (!toldWild && before && countOnBoard(x => x.type === WILD) < before) { toldWild = true; say('Der Regenbogen-Fisch passt zu allem. Lecker!'); }
  return r;
};
