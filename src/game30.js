
/* ===================== V30: puddles you can tell apart ===================== */
// the single puddle is pale milk; the double one is deep blue with a light ring inside (two layers). After the first match it turns pale.
const MILK_G30 = (a, b, c) => `<radialGradient id="m" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="${a}"/><stop offset=".55" stop-color="${b}"/><stop offset="1" stop-color="${c}"/></radialGradient>`;
const MILK_HL30 = '<ellipse cx="30" cy="26" rx="12" ry="5.5" fill="#fff" opacity=".95" transform="rotate(-25 30 26)"/>';
const MILK_RING30 = (col, w) => `<path d="${SPLASH}" transform="translate(50 50) scale(.82) translate(-50 -50)" fill="none" stroke="${col}" stroke-width="${w}"/>`;
const MILK1_30 = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>${MILK_G30('#FFFFFF', '#EEF7FF', '#C2DFF7')}</defs><path d="${SPLASH}" fill="url(#m)" stroke="#9CC8EE" stroke-width="3.5"/>${MILK_HL30}</svg>`;
const MILK2_30 = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>${MILK_G30('#E4F1FF', '#4E97EA', '#1F58B6')}</defs><path d="${SPLASH}" fill="url(#m)" stroke="#123576" stroke-width="6"/>${MILK_RING30('#BFE0FF', 3)}${MILK_HL30}</svg>`;
const MILK2_ICON30 = `<svg viewBox="0 0 100 100"><path d="${SPLASH}" fill="#4A92E6" stroke="#123576" stroke-width="5.5"/>${MILK_RING30('#CFE7FF', 3.4)}<ellipse cx="30" cy="26" rx="11" ry="5" fill="#fff" transform="rotate(-25 30 26)"/></svg>`;
const setArtPlain30 = setArt;
setArt = function () {
  setArtPlain30.apply(this, arguments);
  const u = svg => 'url("data:image/svg+xml,' + encodeURIComponent(svg) + '")', st = document.documentElement.style;
  st.setProperty('--m1', u(MILK1_30)); st.setProperty('--m2', u(MILK2_30));
};
INTRO.milk2 = () => [MILK2_ICON30, 'Neu: doppelte Pfützen', 'Die dunklen Pfützen brauchen zwei Matches. Nach dem ersten wird die Pfütze hell, nach dem zweiten ist sie weg.'];

/* ===================== V30: two extras side by side before the combo lesson: explain it right there ===================== */
// what each pair does, said once when it first comes up (the level 12 card and lesson are then left out)
const COMBO_SAY30 = {
  'cat+cat': () => 'Die beiden flitzen dann durch Reihe und Spalte.',
  'cat+nip': () => 'Die Flitzekatze wird dann riesig und räumt drei Reihen und drei Spalten ab.',
  'nip+nip': () => 'Dann fliegt ein riesiges Stück vom Feld weg.',
  'laser+laser': () => catName + ' jagt dann sechs Leckerlis statt drei.',
  'cat+laser': () => 'Drei Leckerlis werden dann zu Flitzekatzen.',
  'laser+nip': () => 'Drei Leckerlis werden dann zu Katzenminze.',
  'bowl+cat': () => 'Alle Leckerlis einer Sorte werden dann zu Flitzekatzen.',
  'bowl+laser': () => 'Alle Leckerlis einer Sorte werden dann zu Laserpunkten.',
  'bowl+nip': () => 'Alle Leckerlis einer Sorte werden dann zu Katzenminze.',
  'bowl+bowl': () => catName + ' frisst dann das ganze Feld leer.'
};
const comboText30 = (a, b) => { const f = COMBO_SAY30[[a, b].sort().join('+')]; return 'Zwei Extras nebeneinander! Tausch sie miteinander, das gibt eine Riesen-Kombi. ' + (f ? f() : ''); };
// two extras next to each other that can be swapped, the pair nearest the middle first
function comboPair30() {
  let best = null;
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const a = grid[r][c]; if (!a || !isPower(a.type) || !canSwap(a)) continue;
    for (const [dr, dc] of [[0, 1], [1, 0]]) {
      const r2 = r + dr, c2 = c + dc; if (!inB(r2, c2)) continue;
      const b = grid[r2][c2]; if (!b || !isPower(b.type) || !canSwap(b)) continue;
      const d = Math.hypot((r + r2) / 2 - 3.5, (c + c2) / 2 - 3.5);
      if (!best || d < best.d) best = { k: [r * N + c, r2 * N + c2], d };
    }
  }
  return best && best.k;
}
function comboLearnt30() { learnt.combo = true; learnt.comboEarly = true; saveLearnt(); }
async function comboLesson30(pair) {
  if (learnt.combo || tut) return;
  const me = tut = { id: 'combo', ctx: {} };
  try {
    const [a, b] = pair, x = grid[a / N | 0][a % N], y = grid[b / N | 0][b % N];
    await tutMove(comboText30(x.type, y.type), [a, b], [a, b]);
  } finally {
    if (tut === me) { tutHide(); tut = null; }
    if (me.shown && !me.aborted) comboLearnt30();
    if (!onMap) resetIdle();
  }
}
// looked at whenever the board is calm again after a turn (resetIdle runs then)
let comboT30 = 0;
function comboCheck30() {
  if (learnt.combo || busy || tut || aim || onMap || ending || winRunning || winShow || moves < 2) return;
  if (document.querySelector('.overlay.show') || $('endOv').classList.contains('show')) return;
  const p = comboPair30(); if (p) comboLesson30(p);
}
const resetIdlePlain30 = resetIdle;
resetIdle = function () {
  const r = resetIdlePlain30.apply(this, arguments);
  if (!learnt.combo) { clearTimeout(comboT30); comboT30 = setTimeout(comboCheck30, 420); }
  return r;
};
// found it out alone: then it counts as learnt as well. And the swap a lesson asked for: the coach steps aside right away,
// so the effect can be seen (it used to stay dimmed over the board until everything had settled)
const trySwapPlain30 = trySwap;
trySwap = function (r1, c1, r2, c2) {
  if (!busy && inB(r1, c1) && inB(r2, c2)) {
    const a = grid[r1][c1], b = grid[r2][c2], can = a && b && canSwap(a) && canSwap(b);
    if (!learnt.combo && !tut && can && isPower(a.type) && isPower(b.type)) comboLearnt30();
    if (tut && can && tut.expect && tut.expect.type === 'turn' && tutEls && !tutEls.root.hidden && tutAllow('swap', r1 * N + c1, r2 * N + c2)) tutHide();
  }
  return trySwapPlain30.apply(this, arguments);
};
// the level 12 card: no "Neu: Kombis" when it was explained before; the tip line knows about combos once they are learnt
const showIntroPlain30 = showIntro;
showIntro = function () {
  const r = showIntroPlain30.apply(this, arguments);
  if (cfg.intro === 'combo' && learnt.comboEarly) $('introNew').innerHTML = '';
  if (learnt.combo && !isUnlocked('combo')) $('tipline').textContent = 'Tausch ein Extra, dann legt es los. Zwei Extras miteinander tauschen gibt eine Riesen-Kombi.';
  return r;
};

/* ===================== V30: every time the game opens, Freyr is asleep in his bed by his level ===================== */
// his bed stands next to the path just before the level he is at. The spot is picked once when the game opens (where it fits best
// between the scenery) and kept for the session, so the bed stays where he slept. null = his bed at the start of the map.
var napAt = null;
// what the bed with Freyr curled up in it covers, in map units from the bed's foot point
const NAP_BOX = { l: -50, r: 50, t: -66, b: 22 };
// two kinds of spots: beside his level ('side', dx/dy from the level button) or on the path just before it ('path', t along it, o across)
function napPoint(geo, at) {
  if (at.dx != null) { const n = geo.node(at.L); return n ? { x: n.x + at.dx, y: n.y + at.dy } : null; }
  const s = geo.seg(at.L - 1); if (!s) return null;
  const q = bez(s, at.t), a = bez(s, Math.max(0, at.t - .01)), b = bez(s, Math.min(1, at.t + .01)), dx = b.x - a.x, dy = b.y - a.y, l = Math.hypot(dx, dy) || 1;
  return { x: q.x - dy / l * at.o, y: q.y + dx / l * at.o };
}
function napGap(p, x, y) {
  const dx = Math.max(p.x + NAP_BOX.l - x, 0, x - p.x - NAP_BOX.r), dy = Math.max(p.y + NAP_BOX.t - y, 0, y - p.y - NAP_BOX.b);
  return Math.hypot(dx, dy);
}
function napPick(geo, decos, L) {
  if (L <= 1 || L - 1 < geo.L0 || L > geo.L1 || !geo.seg(L - 1)) return null;
  const inner = $('mapInner'), k = (inner && inner.offsetWidth || Math.min(480, innerWidth)) / 400;
  // level buttons (the current one with its ring), the hearts under the done ones, Freyr standing on his level, the world banners
  const keep = [];
  for (let n = geo.L0; n <= geo.L1; n++) {
    const p = geo.node(n);
    keep.push([p.x, p.y, (n === L ? 44 : 30) / k]);
    if (n < L) keep.push([p.x, p.y + 44 / k, 30 / k]);
  }
  const c = geo.node(L); keep.push([c.x, c.y - 52 / k, 34 / k]);
  // the world banners are wide: kept as boxes
  const signs = geo.banners.map(b => [b.x - 104, b.x + 104, b.y - 40, b.y + 40]);
  // the road: a bed right on it is fine, but beside it looks more like a nap; never on the way to the next level,
  // Freyr walks there after a win
  const road = geo.samples.filter(q => Math.abs(q.y - c.y) < 220), ahead = [], sa = geo.seg(L);
  if (sa) for (let i = 0; i <= 24; i++) ahead.push(bez(sa, i / 24));
  const inBox = (p, q, m) => q.x > p.x + NAP_BOX.l + m && q.x < p.x + NAP_BOX.r - m && q.y > p.y + NAP_BOX.t + 30 && q.y < p.y + NAP_BOX.b;
  const onRoad = p => road.some(q => inBox(p, q, 8)), onAhead = p => ahead.some(q => inBox(p, q, -6));
  const cands = [];
  for (const dx of [86, 96, 108, 120, 134]) for (const dy of [-24, -12, 0, 12, 24, 36, 48]) for (const sg of [1, -1]) cands.push({ L, dx: sg * dx, dy, base: Math.abs(dx - 96) * .02 + Math.abs(dy - 24) * .025 });
  for (let i = 0; i <= 13; i++) for (const o of [0, 28, -28, 40, -40, 52, -52, 64, -64]) cands.push({ L, t: Math.round((.2 + i * .05) * 100) / 100, o, base: 1 + Math.abs(.2 + i * .05 - .5) * 4 });
  let best = null;
  for (const cd of cands) {
    const p = napPoint(geo, cd);
    if (!p || p.x + NAP_BOX.l < 2 || p.x + NAP_BOX.r > 398) continue;
    if (keep.some(([x, y, r]) => napGap(p, x, y) < r)) continue;
    if (signs.some(([l, r, t, bt]) => p.x + NAP_BOX.r > l && p.x + NAP_BOX.l < r && p.y + NAP_BOX.b > t && p.y + NAP_BOX.t < bt)) continue;
    // cheapest: close by his level, off the road, few things to move out of the way (never a landmark)
    let cost = cd.base + (onAhead(p) ? 12 : onRoad(p) ? 2.5 : 0);
    for (const d of decos) if (napGap(p, d.x, d.y) < d.r + 3) cost += d.r >= 38 ? 30 : 4;
    if (!best || cost < best.cost) { const { base, ...at } = cd; best = { ...at, cost }; }
  }
  return best;
}
function napSpot(geo) {
  if (!napAt || napAt.pick || napAt.L <= 1 || (introRun && introRun.kind !== 'wake')) return null;
  if (napAt.L - 1 < geo.L0 || napAt.L > geo.L1) return null;
  return napPoint(geo, napAt);
}
// called by renderMap with the scenery it placed: the bed goes where Freyr slept, whatever stood right there makes room
function bedDecos(geo, decos) {
  if (napAt && napAt.pick && !(introRun && introRun.kind !== 'wake')) napAt = napPick(geo, decos, napAt.L);
  const at = napSpot(geo);
  if (!at) { if (geo.L0 === 1) decos.push({ k: 'bed', x: geo.pts[0].x, y: geo.pts[0].y, s: 1, r: 50 }); return decos; }
  const out = decos.filter(d => napGap(at, d.x, d.y) >= d.r + 3);
  out.push({ k: 'bed', x: at.x, y: at.y, s: 1, r: 50 });
  return out;
}
function napScene(b) {
  const VB = [-64, -80, 128, 112];
  const box = `left:${((b.x + VB[0]) / 4).toFixed(3)}%;top:${((b.y + VB[1]) / mapGeo.H * 100).toFixed(4)}%;width:${(VB[2] / 4).toFixed(3)}%;aspect-ratio:${VB[2]}/${VB[3]}`;
  const svg = (id, inner) => `<svg class="ibed" id="${id}" style="${box}" viewBox="${VB.join(' ')}" aria-hidden="true">${inner}</svg>`;
  const el = document.createElement('div'); el.id = 'iScene'; el.className = 'asleep shut nap'; el.setAttribute('aria-hidden', 'true');
  el.innerHTML = svg('iBedBack', `<g filter="url(#mGloss)">${bedArt('back')}</g>${curlArt('mid')}`) +
    `<div class="icat" id="iCat" hidden>${introSprite()}</div>` +
    svg('iBedFront', `<g filter="url(#mGloss)">${bedArt('front')}</g>${curlArt('top')}`) +
    `<span class="zzz disp" id="iZzz">z<b>z</b><i>z</i></span>`;
  $('mapInner').appendChild(el);
  iPlace($('iZzz'), b.x + 18, b.y - 52); iPlace($('iCat'), b.x, b.y + BED_FEET);
  return el;
}
const NAP_SAY = ['Ich hab Hunger!', 'Guten Morgen!', 'Frühstück?', 'Weiter geht’s!', 'Ausgeschlafen!'];
let napSaid = -1;
async function playWake() {
  if (introRun) return;
  const run = introRun = { kind: 'wake', dead: false, timers: new Set(), pending: new Set(), cleaned: false, self: true, anim: false, cam: null, fast: false, woke: false, wake: null, skipped: false };
  const inner = $('mapInner'), map = $('map'), screen = $('mapScreen');
  let done = false, bedG = null, catcher = null, keyH = null, poll = 0;
  // waits and tweens that a second tap (or a skip) finishes at once
  const waits = new Set();
  const kick = () => { for (const f of [...waits]) f(); if (run.wake) run.wake(); };
  const wWait = ms => new Promise((res, rej) => {
    if (run.dead) return rej(INTRO_STOP);
    if (run.fast || ms <= 0) return res();
    const fin = () => { clearTimeout(id); run.timers.delete(id); waits.delete(fin); run.pending.delete(rej); res(); };
    const id = setTimeout(fin, ms); run.timers.add(id); waits.add(fin); run.pending.add(rej);
  });
  const wTween = (ms, fn) => new Promise((res, rej) => {
    if (run.dead) return rej(INTRO_STOP);
    run.pending.add(rej);
    const t0 = performance.now();
    const f = now => {
      if (run.dead) return;
      const t = run.fast || ms <= 0 ? 1 : Math.min(1, (now - t0) / ms);
      fn(t);
      if (t < 1) requestAnimationFrame(f); else { run.pending.delete(rej); res(); }
    };
    requestAnimationFrame(f);
  });
  const sound = f => { if (!run.fast && audioOk()) f(actx.currentTime + .01); };
  try {
    showMap(); run.self = false;
    const geo = mapGeo, L = maxLevel, seg = geo.seg(L - 1);
    const b = napSpot(geo) || (L === 1 && geo.L0 === 1 ? geo.pts[0] : null);
    if (!b || !seg) return;
    mapAnimating = true; run.anim = true; mapSkip = false;
    const bedEl = inner.querySelector('.mbed'); bedG = bedEl ? bedEl.parentNode : null;
    if (bedG) bedG.style.visibility = 'hidden';
    $('mFreyr').style.visibility = 'hidden';
    const scene = napScene(b), cat = $('iCat'), spr = cat.querySelector('.fsprite');
    screen.classList.add('intro', 'iquiet');
    screen.insertAdjacentHTML('beforeend', '<div class="ishade" id="iShade"></div><button class="ihint" id="iHint" type="button" tabindex="-1" hidden></button><div class="ibubble" id="iBubble" aria-live="polite"></div>');
    $('iHint').textContent = 'Tippe, um ' + catName + ' zu wecken';
    // every tap lands here: the first one wakes him, the next one skips to the end
    catcher = document.createElement('div'); catcher.id = 'wTap'; catcher.setAttribute('aria-hidden', 'true'); screen.appendChild(catcher);
    const tapped = () => { if (!run.woke) { run.woke = true; if (run.wake) run.wake(); } else if (!run.fast) { run.fast = true; kick(); } };
    catcher.addEventListener('pointerdown', e => { e.stopPropagation(); e.preventDefault(); tapped(); });
    keyH = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); tapped(); } };
    document.addEventListener('keydown', keyH);
    // a skip from outside (mapSkip) ends it without opening the level
    poll = setInterval(() => { if (mapSkip && !run.fast) { run.skipped = true; run.woke = true; run.fast = true; kick(); } }, 60);
    map.style.overflowY = 'hidden'; inner.style.transformOrigin = '0 0'; inner.style.willChange = 'transform';
    let home = null; const setHome = () => { scrollMapTo(L, .62); home = iHome(); };
    setHome();
    const Z0 = REDUCED ? 1 : Math.min(1.8, iZoom0());
    run.onResize = () => { setHome(); if (run.cam) iCam(run, run.cam.fx, run.cam.fy, run.cam.z); };
    addEventListener('resize', run.onResize);
    // the camera looks at the bed with his level in the picture too
    const NL = geo.node(L), mx = Math.max(-1, Math.min(1, (NL.x - b.x) / 120)) * 34;
    let F = { x: b.x + 4 + mx, y: b.y - 22 };
    iCam(run, F.x, F.y, Z0);

    // asleep until someone taps
    const hint = $('iHint');
    const showHint = setTimeout(() => { if (!run.dead && !run.woke) { hint.hidden = false; void hint.offsetWidth; hint.classList.add('show'); } }, 1000);
    run.timers.add(showHint);
    await new Promise((res, rej) => {
      if (run.dead) return rej(INTRO_STOP);
      if (run.woke) return res();
      run.pending.add(rej);
      run.wake = () => { run.pending.delete(rej); run.wake = null; res(); };
    });
    clearTimeout(showHint);
    if (!run.skipped) { initAudio(); loadMeow(); }
    if (REDUCED) run.fast = true;
    hint.classList.remove('show'); hint.hidden = true;
    $('iShade').classList.add('off');
    scene.classList.remove('asleep'); $('iZzz').classList.add('gone');

    // an ear twitch, eyes open, a big yawn
    scene.classList.add('twitch'); await wWait(340); scene.classList.remove('twitch');
    scene.classList.remove('shut'); scene.classList.add('lift'); await wWait(320);
    scene.classList.add('shut', 'yawn'); await wWait(760); scene.classList.remove('yawn', 'shut'); await wWait(150);

    // he stands up in his bed
    scene.classList.add('up'); cat.hidden = false; cat.classList.add('rise');
    sound(t => { tone(392, t, .12, 'triangle', .05); tone(587.33, t + .09, .18, 'triangle', .05); });
    const F1 = { x: b.x + 2 + mx, y: b.y - 36 };
    await wTween(520, t => { const e = smooth(t); iCam(run, F.x + (F1.x - F.x) * e, F.y + (F1.y - F.y) * e, Z0); });
    F = F1; cat.classList.remove('rise');
    await wWait(100);

    // "Miau!"
    const bub = $('iBubble');
    if (!run.fast) {
      cat.classList.add('meow', 'eat'); meow(); buzz(25);
      let i = Math.floor(Math.random() * NAP_SAY.length); if (i === napSaid) i = (i + 1) % NAP_SAY.length; napSaid = i;
      bub.innerHTML = '<b>Miau!</b><span></span>'; bub.querySelector('span').textContent = NAP_SAY[i];
      const h = cat.querySelector('.fhead').getBoundingClientRect(), sb = screen.getBoundingClientRect();
      bub.style.left = (h.left + h.width / 2 - sb.left).toFixed(1) + 'px'; bub.style.top = (h.top - sb.top - 10).toFixed(1) + 'px';
      bub.classList.add('show');
    }
    await wWait(650); cat.classList.remove('eat');
    if (!run.skipped) { startMusic(); duck(false); }
    await wWait(520); bub.classList.remove('show'); if (bub.innerHTML) bub.classList.add('hide'); cat.classList.remove('meow');
    await wWait(160);

    // he turns round and hops out: beside his level straight towards it, on the path a bit further up the path
    const A = { x: b.x, y: b.y + BED_FEET }, N1 = geo.node(L);
    let P, way, len = 0;
    if (napAt && napAt.dx != null && napAt.L === L) {
      const d = Math.hypot(N1.x - A.x, N1.y - A.y) || 1, f = Math.min(.5, 44 / d);
      P = { x: A.x + (N1.x - A.x) * f, y: A.y + (N1.y - A.y) * f };
      way = e => ({ x: P.x + (N1.x - P.x) * e, y: P.y + (N1.y - P.y) * e }); len = d * (1 - f);
    } else {
      const NS = 60, ts = [];
      for (let i = 0; i <= NS; i++) ts.push(bez(seg, i / NS));
      let tb = 0, db = 1e9;
      ts.forEach((q, i) => { const d = Math.hypot(q.x - b.x, q.y - b.y); if (d < db) { db = d; tb = i / NS; } });
      let th = Math.min(.9, tb + .15);
      for (let i = Math.ceil((tb + .04) * NS); i <= NS * .9; i++) if (Math.hypot(ts[i].x - b.x, ts[i].y - b.y) >= 44) { th = i / NS; break; }
      P = bez(seg, th); way = e => bez(seg, th + (1 - th) * e);
      for (let i = Math.round(th * NS) + 1; i <= NS; i++) len += Math.hypot(ts[i].x - ts[i - 1].x, ts[i].y - ts[i - 1].y);
    }
    spr.classList.add('back'); await wWait(180);
    cat.classList.add('jump');
    sound(t => { tone(523.25, t, .1, 'triangle', .045); tone(783.99, t + .07, .14, 'triangle', .04); });
    await wTween(460, t => { const e = ease(t); iPlace(cat, A.x + (P.x - A.x) * e, A.y + (P.y - A.y) * e - 24 * 4 * t * (1 - t)); });
    cat.classList.remove('jump'); cat.classList.add('land');
    await wWait(160); cat.classList.remove('land');

    // and walks up to his level while the camera lets go
    spr.classList.add('walk'); screen.classList.remove('iquiet');
    const dur = Math.max(550, Math.min(1400, len * 10)), Fw = { ...F };
    let lastStep = 0, n = 0;
    await wTween(dur, t => {
      const e = ease(t), q = way(e);
      const lift = 14 * Math.max(0, (e - .86) / .14);
      iPlace(cat, q.x, q.y); cat.style.transform = lift ? `translateY(${(-lift).toFixed(1)}px)` : '';
      const c = smooth(Math.min(1, t / .9)), f0 = smooth(Math.min(1, t / .25));
      const fx = Fw.x + (q.x - Fw.x) * f0, fy = Fw.y + (q.y - 30 - Fw.y) * f0;
      iCam(run, fx + (home.x - fx) * c, fy + (home.y - fy) * c, Z0 * Math.pow(1 / Z0, c));
      const now = performance.now();
      if (now - lastStep > 180 && t < .97) { lastStep = now; sound(tt => tone(n++ % 2 ? 620 : 540, tt, .06, 'triangle', .035)); }
    });
    iCam(run, home.x, home.y, 1);
    spr.classList.remove('walk', 'back');
    if (!run.fast) { void spr.offsetWidth; spr.classList.add('hop'); chime(4); }
    await wWait(420);
    done = true;
  } catch (e) {
    if (e !== INTRO_STOP) console.error(e);
  } finally {
    clearInterval(poll);
    introCleanup(run);
    if (bedG) bedG.style.visibility = '';
    const f = $('mFreyr'); if (f) f.style.visibility = '';
    const sc = $('iScene'); if (sc) sc.remove();
    if (keyH) document.removeEventListener('keydown', keyH);
    // the catcher stays a moment longer, so the tap that skipped does not land on a level button
    if (catcher) { const c = catcher; setTimeout(() => c.remove(), 450); }
  }
  // stopped from outside (a level started): nothing more. Skipped: the map as it always was. Done: his level opens.
  if (!onMap || (!done && !run.skipped)) return;
  setTimeout(async () => {
    if (!onMap || mapAnimating || introRun || document.querySelector('.overlay.show')) return;
    if (isUnlocked('chest') && !learnt.chest) await runLesson('chest');
    if (!run.skipped && onMap && !mapAnimating && !introRun && lives > 0 && !document.querySelector('.overlay.show')) openLevel(maxLevel);
  }, run.skipped ? 700 : 240);
}
const startGamePlain30 = startGame;
startGame = function () {
  if (!introSeen()) return startGamePlain30();
  napAt = { L: maxLevel, pick: true };
  playWake();
};

/* ===================== V30: earlier levels: the map shows the last worlds; a sign at the bottom brings back the ones before ===================== */
var mapBack = 0;   // extra worlds shown below the usual ones, for this session
const DOWN_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8.5l7 7 7-7" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const renderMapPlain30 = renderMap;
renderMap = function () {
  const r = renderMapPlain30.apply(this, arguments), g = mapGeo;
  if (g && g.L0 > 1 && !(introRun && introRun.kind !== 'wake')) {
    const from = Math.max(1, g.L0 - 25), to = g.L0 - 1;
    const btn = document.createElement('button');
    btn.className = 'btn soft mback'; btn.type = 'button';
    btn.innerHTML = '<span>Frühere Level</span><small></small>' + DOWN_SVG;
    btn.querySelector('small').textContent = from + '–' + to;
    btn.setAttribute('aria-label', 'Frühere Level zeigen, ' + from + ' bis ' + to);
    btn.style.top = ((g.H - 70) / g.H * 100).toFixed(4) + '%';
    $('mapInner').appendChild(btn);
  }
  return r;
};
$('mapInner').addEventListener('click', e => {
  const b = e.target.closest('.mback'); if (!b || mapAnimating || introRun) return;
  initAudio(); blip();
  // five worlds more at the bottom; what is on screen stays where it is, then the map slides down to them
  mapBack += 5; renderMap();
  const map = $('map'), from = map.scrollTop, to = Math.min(map.scrollHeight - map.clientHeight, from + map.clientHeight * .62);
  if (REDUCED) { map.scrollTop = to; return; }
  const t0 = performance.now();
  const f = now => { const t = Math.min(1, (now - t0) / 520), e2 = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; map.scrollTop = from + (to - from) * e2; if (t < 1) requestAnimationFrame(f); };
  requestAnimationFrame(f);
});
