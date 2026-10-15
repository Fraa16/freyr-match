
/* ===================== V41: a letter from Freyr, and a test level for the new extras ===================== */
// Everyone who played before finds a letter on the next start. Freyr holds it up and reads it out, line by line.
// It has no close button: the only way on is the button into a short test level, where the new rule (an extra goes off
// in a match) is shown step by step and then tried alone. Until that level is finished once, the letter comes back.
const NEWS41 = 'wm-news41';
let TRY41 = null;
function news41Done() { try { return localStorage.getItem(NEWS41) === 'done'; } catch (e) { return true; } }
function news41Mark() { try { localStorage.setItem(NEWS41, 'done'); } catch (e) {} }
const PAW41 = `<svg viewBox="0 0 60 46" aria-hidden="true"><path d="M6 31 Q4 13 16 9 Q19 2 26 6 Q30 0 34 6 Q41 2 44 9 Q56 13 54 31 Q54 44 30 44 Q6 44 6 31Z" fill="#fff" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>` +
  `<path d="M22 9 Q23 15 21.5 20 M30 7 V18 M38 9 Q37 15 38.5 20" fill="none" stroke="#E2CFDA" stroke-width="2.4" stroke-linecap="round"/></svg>`;
const PRINT41 = `<svg viewBox="0 0 100 100" aria-hidden="true"><g fill="#F07CA0"><ellipse cx="50" cy="64" rx="20" ry="17"/><ellipse cx="25" cy="42" rx="8.5" ry="10.5"/><ellipse cx="41" cy="27" rx="8.5" ry="10.5"/><ellipse cx="59" cy="27" rx="8.5" ry="10.5"/><ellipse cx="75" cy="42" rx="8.5" ry="10.5"/></g></svg>`;
// the little picture in the letter: a Flitzekatze with two of its treats, in a row
function demo41() {
  const t = 0, tile = (h, cls) => `<span class="n41tile${cls ? ' ' + cls : ''}">${h}</span>`;
  return tile(ICONS[t]) + tile(typeof extraSvg40 === 'function' ? extraSvg40({ type: 'cat', col: t, dir: 'h' }) : iconFor({ type: 'cat', dir: 'h' }), 'x') + tile(ICONS[t]);
}
function letter41() {
  const n = esc(catName);
  return `<h2 class="n41t" id="n41title">Post von ${n}</h2>` +
    `<p class="n41l n41hi">Liebe Ahsi,</p>` +
    `<p class="n41l">ich hab Neuigkeiten für dich!</p>` +
    `<p class="n41l">Extras gehen nicht mehr einfach so los. In jedem Extra steckt jetzt das Leckerli, aus dem du es gebaut hast. Bring es mit zwei gleichen Leckerlis in eine Reihe, dann geht’s los.</p>` +
    `<div class="n41l n41demo" aria-hidden="true">${demo41()}</div>` +
    `<p class="n41l">Zwei Extras miteinander gehen weiterhin immer, und den Napf tauschst du wie bisher mit jedem Leckerli.</p>` +
    `<p class="n41l n41sub">Außerdem neu:</p>` +
    `<ul class="n41list">` + ['neue Geräusche für die Extras', 'ein wilderer Krallenkratzer', 'Napf + Napf = Riesen-Festmahl', 'Sieg im letzten Zug? Überraschung!', 'die Level sind etwas kniffliger']
      .map(t => `<li class="n41l">${PRINT41}${t}</li>`).join('') + `</ul>` +
    `<p class="n41l">Im Testlevel zeig ich dir alles.</p>` +
    `<p class="n41l n41sign">Dein ${n} ${PRINT41}</p>` +
    `<p class="n41l n41ps">PS: Ich hab Hunger.</p>`;
}
// Freyr behind the paper, his paws on its edge
function sheet41(id, body, btn) {
  const ov = document.createElement('div');
  ov.className = 'overlay show n41ov'; ov.id = id;
  ov.innerHTML = `<div class="n41wrap" role="dialog" aria-modal="true" aria-labelledby="n41title">` +
    `<div class="n41letter"><div class="n41face" aria-hidden="true">${CAT_ICON()}</div>` +
    `<div class="n41paper"><div class="n41paws" aria-hidden="true">${PAW41}${PAW41}</div><div class="n41body">${body}</div></div></div>` +
    `<p class="n41hint">Tipp auf den Brief, dann lese ich schneller.</p>` +
    `<button class="btn big n41go" type="button" hidden>${btn}</button></div>`;
  document.body.appendChild(ov);
  return ov;
}
// he reads it out: one line after the other comes up, his mouth moves, his eyes follow the lines
async function read41(ov) {
  const lines = [...ov.querySelectorAll('.n41l')], face = ov.querySelector('.n41face'), body = ov.querySelector('.n41body');
  let fast = REDUCED, wake = null, talking = false;
  const hurry = () => { fast = true; if (wake) wake(); };
  ov.querySelector('.n41paper').addEventListener('click', hurry);
  ov.querySelector('.n41hint').addEventListener('click', hurry);
  const wait = ms => fast ? Promise.resolve() : new Promise(r => { wake = r; setTimeout(r, ms); });
  // more below: the bottom edge of the text fades out
  const cue = () => body.classList.toggle('more', body.scrollTop + body.clientHeight < body.scrollHeight - 6);
  body.addEventListener('scroll', cue, { passive: true });
  const mouth = setInterval(() => face.classList.toggle('eat', talking && Math.random() < .55), 130);
  face.classList.add('read');
  await wait(700);
  for (const el of lines) {
    if (!ov.isConnected) break;
    el.classList.add('on');
    if (fast) continue;
    if (body.scrollHeight > body.clientHeight + 4) { const b = el.getBoundingClientRect(), p = body.getBoundingClientRect(); if (b.bottom > p.bottom - 8) body.scrollTop += b.bottom - p.bottom + 24; }
    cue();
    const dur = Math.max(450, Math.min(2600, el.textContent.length * 26));
    talking = true; await wait(dur); talking = false; face.classList.remove('eat');
    await wait(200);
  }
  clearInterval(mouth); face.classList.remove('eat', 'read');
  lines.forEach(el => el.classList.add('on'));
  if (!ov.isConnected) return;
  cue();
  ov.querySelector('.n41hint').hidden = true;
  const go = ov.querySelector('.n41go'); go.hidden = false; go.classList.add('pop-in');
  try { go.focus({ preventScroll: true }); } catch (e) {}
  if (typeof meow === 'function') meow(.5);
}
function news41Open() {
  if ($('news41') || TRY41) return;
  if (!onMap) showMap();
  const ov = sheet41('news41', letter41(), 'Zum Testlevel');
  ov.querySelector('.n41go').onclick = () => { blip(); try41Start(); };
  read41(ov);
}
// for the preview: the letter again, from the start
function news41Again() {
  try { localStorage.removeItem(NEWS41); } catch (e) {}
  const e1 = $('news41'), e2 = $('news41end'); if (e1) e1.remove(); if (e2) e2.remove();
  if (TRY41 || !onMap) { TRY41 = null; tutAbort(); showMap(); }
  setTimeout(news41Open, 250);
}
// a new player starts with the rule as it is and never gets the letter; everyone else gets it before the wake-up scene
const startGame41 = startGame;
startGame = function () {
  if (!introSeen()) { news41Mark(); return startGame41.apply(this, arguments); }
  if (!news41Done()) { showMap(); return setTimeout(news41Open, 400); }
  return startGame41.apply(this, arguments);
};

/* ---------- the test level ---------- */
// a plain open board (level 1's), five kinds of treats, plenty of moves; the goal: set off 3 extras alone at the end
const levelConfig41 = levelConfig;
levelConfig = function (L) {
  if (!(TRY41 && TRY41.building)) return levelConfig41.apply(this, arguments);
  const c = levelConfig41(1), w = levelConfig41(L).world;
  return Object.assign(c, { name: 'Testlevel', world: w, moves: 30, target: 0, gold: false, intro: null, bells: 0, hard: 0, kit: 0, fish: null, goals: [{ kind: 'fire41', n: 3 }] });
};
const remaining41 = remaining, goalText41 = goalText, goalIcon41 = goalIcon;
remaining = function (g) { return g.kind === 'fire41' ? Math.max(0, g.left) : remaining41.apply(this, arguments); };
goalText = function (g, n) { return g.kind === 'fire41' ? n + (n === 1 ? ' Extra' : ' Extras') + ' zünden' : goalText41.apply(this, arguments); };
goalIcon = g => g.kind === 'fire41' ? (typeof extraSvg40 === 'function' ? extraSvg40({ type: 'nip', col: 2 }) : NIP_SVG) : goalIcon41(g);
// every extra that goes off in the free part counts
const fire41 = fire;
fire = function (cell) {
  if (TRY41 && TRY41.count && cell && isPower(cell.type)) { const g = goals.find(x => x.kind === 'fire41'); if (g && g.left > 0) g.left--; }
  return fire41.apply(this, arguments);
};
// nobody loses the test level: out of moves, there are five more
const afterTurn41 = afterTurn;
afterTurn = async function () {
  if (TRY41 && moves <= 0 && !goalsDone()) { moves += 5; updateHud(); say('Hier, noch 5 Züge. Im Testlevel kann man nicht verlieren.'); }
  return afterTurn41.apply(this, arguments);
};
// the level tab says Test
const updateHud41 = updateHud;
updateHud = function () { const r = updateHud41.apply(this, arguments); if (TRY41) $('level').textContent = 'Test'; return r; };
const openPause41 = openPause;
openPause = function () { const r = openPause41.apply(this, arguments); if (TRY41) $('pauseWhere').textContent = 'Testlevel'; return r; };
$('pauseBtn').onclick = openPause;
// leaving it brings the letter back, without a life lost or a loss counted
document.addEventListener('click', e => {
  if (!TRY41 || !e.target.closest || !e.target.closest('#toMap')) return;
  e.stopImmediatePropagation(); e.preventDefault();
  try41Leave();
}, true);
async function try41Leave() {
  $('pauseOv').classList.remove('show');
  for (let i = 0; busy && i < 120; i++) await sleep(50);
  TRY41 = null; tutAbort(); showMap(); setTimeout(news41Open, 450);
}
async function try41Start() {
  const ov = $('news41'); if (ov) ov.remove();
  initAudio(); startMusic(); duck(false);
  pick = null; TRY41 = { count: false, building: true };
  try { startLevel(); } finally { TRY41.building = false; }
  $('introOv').classList.remove('show');
  if (onMap) { hideMap(); render(true); }
  busy = true;
  setTimeout(() => { chime(3); chomp(1); }, 80);
  await sleep(450);
  if (!TRY41) return;
  busy = false; resetIdle();
  say('Mein Testlevel! Ich zeig dir alles.');
  try41Run();
}
const TRY41_STEPS = [
  [{ plant: 'cat' }, { move: d => 'Wisch es ' + d + '. Vier gleiche in einer Reihe ergeben eine Flitzekatze.' }],
  [{ see41: true }, { use: 'colx' }],
  [{ pair: ['cat', 'nip'] }, { move: () => 'Zwei Extras miteinander gehen weiterhin immer, auch ohne Match. Tausch sie!' }],
  [{ pair: ['bowl', 'bowl'] }, { move: () => 'Und jetzt das Beste: zwei Näpfe zusammen. Tausch sie!' }],
  [{ free41: true }]
];
async function try41Run() {
  const me = tut = { id: 'try41', ctx: {} };
  try {
    for (const group of TRY41_STEPS) for (const st of group) {
      if (tut !== me || !TRY41 || onMap) return;
      if (!(await tutStep(st))) break;
    }
  } finally {
    if (tut === me) { tutHide(); tut = null; }
    if (TRY41 && !onMap) { if (!TRY41.count) { TRY41.count = true; updateHud(); } resetIdle(); }
  }
}
const winSequence41 = winSequence;
winSequence = async function () {
  if (!TRY41) return winSequence41.apply(this, arguments);
  cancelAim(true); clearPreview(); clearTimeout(idleTimer); busy = true;
  news41Mark();
  celebrate(); say('Pfotastisch!');
  await sleep(2300);
  if (!TRY41) return;
  const ov = sheet41('news41end', `<h2 class="n41t" id="n41title">Geschafft!</h2><p class="n41l n41hi">Pfotastisch, Ahsi!</p>` +
    `<p class="n41l">Jetzt weißt du, wie die Extras gehen. Viel Spaß beim Weiterspielen!</p><p class="n41l n41sign">Dein ${esc(catName)} ${PRINT41}</p>`, 'Weiterspielen');
  ov.querySelector('.n41go').onclick = () => {
    blip(); ov.remove(); TRY41 = null; showMap();
    setTimeout(() => { if (onMap && !mapAnimating && !introRun && !tut && lives > 0 && !document.querySelector('.overlay.show')) openLevel(maxLevel); }, 750);
  };
  read41(ov);
};

/* ---------- the coach, for the new rule ---------- */
// the extra stays where it is; two treats of its kind are laid out so that one swap puts all three in a row
function plantPair41(k) {
  const x = grid[k / N | 0][k % N];
  if (!isColx(x) || !COLORS.includes(x.col)) return null;
  const r0 = k / N | 0, c0 = k % N, sh = SHAPES.three, cands = [];
  for (const f of TF) {
    const s = sh.s.map(f), m = f(sh.m), t = f(sh.t);
    for (const an of s) {
      const P = p => [r0 - an[0] + p[0], c0 - an[1] + p[1]];
      const S = s.map(P), M = P(m), T = P(t), O = S.find(([r, c]) => r * N + c !== k);
      cands.push({ S, M, T, O, d: Math.hypot(T[0] - 3.5, T[1] - 3.5) + Math.random() });
    }
  }
  cands.sort((a, b) => a.d - b.d);
  for (const P of cands) if ([P.O, P.M, P.T].every(([r, c]) => plainAt(r, c)) && paintPair41(P, k, x.col)) return P;
  return null;
}
function paintPair41(P, k, col) {
  const { S, M, T, O } = P, key = ([r, c]) => r * N + c, fixed = new Set([...S, M, T].map(key));
  const snap = grid.map(row => row.map(y => y && y.type));
  const free = q => { const y = grid[q / N | 0][q % N]; return !fixed.has(q) && y && isNormal(y.type) && !y.gold; };
  const reroll = q => { if (free(q)) grid[q / N | 0][q % N].type = rnd(); };
  const others = COLORS.filter(t => t !== col);
  for (let attempt = 0; attempt < 12; attempt++) {
    grid[O[0]][O[1]].type = col; grid[M[0]][M[1]].type = col; grid[T[0]][T[1]].type = others[Math.floor(Math.random() * others.length)];
    for (let it = 0; it < 80; it++) {
      const pre = findMatches();
      if (pre.cells.size) { const bad = [...pre.cells].filter(free); if (!bad.length) break; bad.forEach(reroll); continue; }
      sw(M[0], M[1], T[0], T[1]);
      const m = findMatches(), expect = new Set([...S, T].map(key));
      const extra = [...m.cells].filter(q => !expect.has(q)), missing = [...expect].filter(q => !m.cells.has(q));
      const ok = !extra.length && !missing.length && extrasFor(m, [key(T), key(M)]).size === 0;
      sw(M[0], M[1], T[0], T[1]);
      if (ok) { render(false); return true; }
      if (!extra.length || missing.length || extra.some(q => !free(q))) break;
      extra.forEach(reroll);
    }
  }
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (grid[r][c]) grid[r][c].type = snap[r][c];
  return false;
}
// a coloured extra on a free spot, without making a match
function placeExtra41(type) {
  const spots = [];
  for (let r = 1; r < N - 1; r++) for (let c = 1; c < N - 1; c++) if (plainAt(r, c)) spots.push([r, c, Math.hypot(r - 3.5, c - 3.5) + Math.random() * 2.5]);
  spots.sort((a, b) => a[2] - b[2]);
  for (const [r, c] of spots) {
    const old = grid[r][c], x = mk(type);
    if (type === 'cat') x.dir = Math.random() < .5 ? 'h' : 'v';
    for (const col of COLORS.slice().sort(() => Math.random() - .5)) {
      x.col = col; grid[r][c] = x;
      if (!findMatches().cells.size) return r * N + c;
    }
    grid[r][c] = old;
  }
  return null;
}
const nearColx41 = at => {
  let best = null;
  for (let k = 0; k < N * N; k++) { const x = grid[k / N | 0][k % N]; if (isColx(x) && COLORS.includes(x.col)) { const d = at == null ? Math.hypot((k / N | 0) - 3.5, k % N - 3.5) : Math.abs((k / N | 0) - (at / N | 0)) + Math.abs(k % N - at % N); if (!best || d < best.d) best = { k, d }; } }
  return best && best.k;
};
const DER41 = { cat: ['in der Flitzekatze', 'Mit der Flitzekatze sind es drei gleiche, und sie flitzt los!'], laser: ['im Laserpunkt', 'Mit dem Laserpunkt sind es drei gleiche, und ich jage drei Leckerlis!'],
  nip: ['in der Katzenminze', 'Mit der Katzenminze sind es drei gleiche, und alles rundherum fliegt weg!'] };
const pairText41 = (x, d) => 'Wisch dieses Leckerli ' + d + '. ' + DER41[x.type][1];
const tutStep41 = tutStep;
tutStep = async function (st) {
  const ctx = tut && tut.ctx;
  if (st.see41) {
    let k = nearColx41(ctx.at);
    if (k == null) { k = placeExtra41('cat'); if (k != null) render(false); }
    if (k == null) return false;
    ctx.at = k;
    const x = grid[k / N | 0][k % N];
    tutShow({ box: () => cellBox(k), text: 'Schau, ' + DER41[x.type][0] + ' steckt jetzt das Leckerli, aus dem ' + (x.type === 'laser' ? 'er' : 'sie') + ' gebaut ist. Einfach tauschen reicht nicht mehr.', next: true });
    await new Promise(res => { tut.expect = null; tut.res = res; tutEls.next.onclick = () => { blip(); if (tut && tut.res === res) { tut.res = null; res(); } }; });
    return true;
  }
  if (st.free41) {
    const ks = ['laser', 'nip', 'cat'].map(placeExtra41).filter(k => k != null);
    if (ks.length) plantPair41(ks[0]);
    render(false);
    await tutInfo('goals', 'Jetzt du! Zünde 3 Extras ganz allein. Immer mit zwei gleichen Leckerlis in eine Reihe.');
    if (TRY41) { TRY41.count = true; updateHud(); }
    return true;
  }
  // an extra that has a colour goes off in a match: lay out the match and show it
  if (st.use && PAIR40) {
    let k = null;
    if (st.use === 'colx') k = nearColx41(ctx.at);
    else if (st.use !== 'bowl') {
      let best = null;
      for (let q = 0; q < N * N; q++) { const x = grid[q / N | 0][q % N]; if (x && (st.use === 'any' ? isPower(x.type) : x.type === st.use)) { const d = ctx.at == null ? 0 : Math.abs((q / N | 0) - (ctx.at / N | 0)) + Math.abs(q % N - ctx.at % N); if (!best || d < best.d) best = { k: q, d }; } }
      if (best && isColx(grid[best.k / N | 0][best.k % N])) k = best.k;
    }
    if (k != null) {
      const P = plantPair41(k); if (!P) return false;
      const x = grid[k / N | 0][k % N], a = K(P.M), b = K(P.T), area = areaOf(x, k / N | 0, k % N);
      if (area.length) showPreview(area, 'ex');
      const d = dirWord(a, b);
      await tutMove(st.ptext ? st.ptext(x, d) : pairText41(x, d), [a, b], [...P.S, P.M, P.T].map(K).concat(area));
      ctx.at = k;
      return true;
    }
    if (st.use === 'colx') return false;
  }
  const r = await tutStep41.apply(this, arguments);
  // two extras laid next to each other must not make a match with their colours
  if (r && st.pair && PAIR40 && ctx && ctx.P) {
    let changed = false;
    for (const [rr, cc] of [ctx.P.M, ctx.P.T]) {
      const y = grid[rr][cc]; if (!isColx(y)) continue;
      for (const col of [y.col, ...COLORS]) { y.col = col; if (!findMatches().cells.has(rr * N + cc)) break; changed = true; }
    }
    if (changed) render(false);
  }
  return r;
};
