
/* ===================== V39: the Krallenkratzer and the double Festmahl get their own show ===================== */

/* ---------- every extra that goes off is noted, so its sound can be played (sfx39) ---------- */
const fire39 = fire;
fire = function (cell, k, clear, delay, base, fxq) {
  const had = cell.type === 'laser' ? new Set(clear) : null;
  fire39.apply(this, arguments);
  if (!fxq || !fxq.x) return;
  const e = { type: cell.type, d: base, k, dir: cell.dir, mode: cell.mode, radius: cell.radius, eat: cell.eat };
  if (had) e.hits = [...clear].filter(x => !had.has(x)).map(x => ({ d: delay.get(x) || base, pan: (x % N - 3.5) / 4.5 })).sort((a, b) => a.d - b.d);
  fxq.x.push(e);
};
// a callout can wait for the right moment (the double Festmahl shows its word at the bang, not at the start)
let calloutDelay39 = 0;
const callout39 = callout;
callout = function () {
  const a = arguments;
  if (calloutDelay39 > 0) { const d = calloutDelay39; calloutDelay39 = 0; setTimeout(() => callout39.apply(this, a), d); return; }
  return callout39.apply(this, a);
};

/* ---------- Krallenkratzer: Freyr's paw swipes across the row, claws out, and leaves three glowing scratches ---------- */
const SWIPE_PAW = (() => {
  // the paw seen from below, toes to the right, claws out and curved
  const cx = 44, cy = 50, toes = [-62, -21, 21, 62].map(a => { const r = a * Math.PI / 180; return [cx + 35 * Math.cos(r), cy + 35 * Math.sin(r), a]; });
  const f = v => v.toFixed(1);
  const claw = ([x, y, a]) => {
    const r = a * Math.PI / 180, ux = Math.cos(r), uy = Math.sin(r), px = -uy, py = ux;
    const b1 = [x + ux * 7 + px * 4, y + uy * 7 + py * 4], b2 = [x + ux * 7 - px * 4, y + uy * 7 - py * 4];
    const tip = [x + ux * 27 + px * 7, y + uy * 27 + py * 7], q1 = [x + ux * 20 + px * 7, y + uy * 20 + py * 7], q2 = [x + ux * 19 - px * 1, y + uy * 19 - py * 1];
    return `<path d="M${f(b1[0])} ${f(b1[1])} Q${f(q1[0])} ${f(q1[1])} ${f(tip[0])} ${f(tip[1])} Q${f(q2[0])} ${f(q2[1])} ${f(b2[0])} ${f(b2[1])}Z"/>`;
  };
  const toe = ([x, y, a]) => `<ellipse cx="${f(x)}" cy="${f(y)}" rx="11.5" ry="10" transform="rotate(${a} ${f(x)} ${f(y)})"/>`;
  const bean = ([x, y, a]) => { const r = a * Math.PI / 180, bx = x + Math.cos(r) * 1.5, by = y + Math.sin(r) * 1.5; return `<ellipse cx="${f(bx)}" cy="${f(by)}" rx="5.6" ry="4.6" transform="rotate(${a} ${f(bx)} ${f(by)})"/>`; };
  return `<svg viewBox="-6 -8 126 116"><g fill="#FFFFFF" ${OL('#5B4A8E')}>${toes.map(claw).join('')}</g>` +
    `<path d="M-4 30 Q8 22 20 28 L34 34 L34 66 L20 72 Q8 78 -4 70 Q2 62 -2 56 Q4 50 -2 44 Q3 37 -4 30Z" fill="url(#gWhite)" ${OL('#5B4A8E')}/>` +
    `<g fill="url(#gWhite)" ${OL('#5B4A8E')}><ellipse cx="${cx}" cy="${cy}" rx="25" ry="27"/>${toes.map(toe).join('')}</g>` +
    `<g fill="url(#gPink)">${toes.map(bean).join('')}<path d="M${cx + 13} ${cy} Q${cx + 10} ${cy - 15} ${cx} ${cy - 11} Q${cx - 9} ${cy - 15} ${cx - 10} ${cy} Q${cx - 9} ${cy + 15} ${cx} ${cy + 11} Q${cx + 10} ${cy + 15} ${cx + 13} ${cy}Z"/></g>` +
    `${SHINE(cx - 6, cy - 14, 9, 4)}</svg>`;
})();
function clawSwipe(r, T0, per) {
  if (REDUCED) return;
  const g = boardGeo(), cw = g.cw, y = g.top + (r + .5) * cw, x0 = g.left - cw * .5, x1 = g.left + g.w + cw * .5, size = cw * 2.7;
  const tIn = T0 - per * .5, tOut = T0 + (N - .5) * per, total = tOut + 280;
  // where the claws are at a moment (the paw's centre sits behind them)
  const headX = ms => ms <= tIn ? x0 : ms >= tOut ? x1 : x0 + (x1 - x0) * (ms - tIn) / (tOut - tIn);
  const el = document.createElement('div'); el.className = 'swipe39'; el.innerHTML = SWIPE_PAW;
  Object.assign(el.style, { width: size + 'px', height: size + 'px', left: (-size * .72) + 'px', top: (-size / 2) + 'px' });
  document.body.appendChild(el);
  const kf = [
    [0, x0 - cw * 1.2, y - cw * 1.7, -55, .5, 0],
    [120, x0 - cw * .7, y - cw * 1.1, -32, 1.05, 1],
    [tIn - 30, x0 - cw * 1.0, y - cw * 1.25, -40, 1, 1],
    [tIn, x0, y - cw * .25, -14, 1.04, 1],
    [(tIn + tOut) / 2, (x0 + x1) / 2, y + cw * .05, -2, 1.1, 1],
    [tOut, x1, y - cw * .2, 10, 1.04, 1],
    [total, x1 + cw * 1.3, y - cw * 1.6, 34, .55, 0]
  ];
  const a = el.animate(kf.map(([t, x, yy, rot, s, o]) => ({ offset: t / total, transform: `translate(${x.toFixed(1)}px,${yy.toFixed(1)}px) rotate(${rot}deg) scale(${s})`, opacity: o })),
    { duration: total, fill: 'forwards' });
  a.onfinish = () => el.remove(); setTimeout(() => el.remove(), total + 400);
  // three torn scratches open up behind the claws (an svg over the row: dark gashes with pink edges)
  gashes39(r, tIn, tOut);
  const lines = [-1, 0, 1].map(i => ({ dy: i * cw * .27 }));
  // bits fly off every cell the claws go through
  for (let col = 0; col < N; col++) {
    const at = T0 + col * per, x = g.left + (col + .5) * cw;
    later(at, () => burst(x, y, 7, 1.15, ['#ffffff', '#FFD1E1', '#FF8FC0', '#C9A6F2'], 'dot'));
    for (const L of lines) sparks(x, y + L.dy, 3, '#FFC2DD', cw * .16, at);
  }
  later(tIn + 40, shake);
}
function gashes39(r, tIn, tOut) {
  const W = 800, H = 170, f = v => v.toFixed(1);
  let paths = '';
  [-1, 0, 1].forEach((i, n) => {
    const yc = H / 2 + i * 33, top = [], bot = [], maxW = 22 - Math.abs(i) * 3;
    for (let s = 0; s <= 28; s++) {
      const u = s / 28, x = -10 + u * (W + 20), w = maxW * Math.pow(Math.sin(Math.PI * Math.min(1, u * 1.08)), .55) * (.8 + Math.random() * .35) + .4;
      const y = yc - (u - .5) * 22 + Math.sin(u * 9 + n * 2) * 2.2;
      top.push(f(x) + ' ' + f(y - w / 2)); bot.unshift(f(x) + ' ' + f(y + w / 2));
    }
    const d = 'M' + top.join(' L') + ' L' + bot.join(' L') + 'Z';
    paths += `<path d="${d}" fill="#2A0A33" stroke="#FF5FA8" stroke-width="3.2" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="#fff" stroke-width="1.1" opacity=".8" transform="translate(0 -1.6)"/>`;
  });
  later(tIn - 10, () => {
    const e = document.createElement('div'); e.className = 'gash39';
    e.style.top = ((r - .35) * STEP) + '%'; e.style.height = (1.7 * STEP) + '%';
    e.innerHTML = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${paths}</svg>`;
    boardEl.appendChild(e);
    e.animate([{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)' }], { duration: tOut - tIn, easing: 'linear', fill: 'forwards' });
    e.animate([{ opacity: 1 }, { opacity: 1, offset: .72 }, { opacity: 0 }], { duration: tOut - tIn + 1000, fill: 'forwards' }).onfinish = () => e.remove();
    setTimeout(() => e.remove(), tOut - tIn + 1400);
  });
}
const CLAW39_T0 = 250, CLAW39_PER = 46;
const clawAt39 = clawAt;
clawAt = async function (r) {
  if (!FX39) return clawAt39(r);
  const blast = new Set(), bd = new Map();
  for (let c = 0; c < N; c++) if (mask[r][c]) { blast.add(r * N + c); bd.set(r * N + c, CLAW39_T0 + c * CLAW39_PER); }
  if (audioOk()) SFX.scratch((CLAW39_T0 - CLAW39_PER * .5) / 1000 - .1, N * CLAW39_PER / 1000);
  clawSwipe(r, CLAW39_T0, CLAW39_PER); buzz([20, 30, 20]);
  calloutDelay39 = CLAW39_T0 + N * CLAW39_PER;
  await resolve(blast, null, 'Krallenkratzer!', null, false, bd);
};

/* ---------- two bowls: they melt into one, the board trembles, everything is pulled in; then a bang and a rainbow wave ---------- */
const FEAST39_CH = 620;
// motes of light from all over the board are pulled into the bowl, turning as they go
function suckIn(x, y, cw, d, dur) {
  const g = boardGeo(), motes = [];
  for (let i = 0; i < Q(40); i++) {
    const sx = g.left + Math.random() * g.w, sy = g.top + Math.random() * g.h, col = RAINBOW[i % 6];
    motes.push({ sx, sy, u0: Math.random() * .55, len: .3 + Math.random() * .15, spin: (Math.random() < .5 ? -1 : 1) * (.8 + Math.random() * .8), spr: glowSpr('#ffffff', withA(col, .9), withA(col, .35)) });
  }
  addVfx(d, dur, (c, t) => {
    for (const m of motes) {
      const p = (t - m.u0) / m.len; if (p <= 0 || p >= 1) continue;
      const e = p * p, dx = m.sx - x, dy = m.sy - y, ang = m.spin * e, cs = Math.cos(ang), sn = Math.sin(ang), k = 1 - e;
      const px = x + (dx * cs - dy * sn) * k, py = y + (dx * sn + dy * cs) * k, r = cw * (.32 - .16 * e);
      c.globalAlpha = p < .15 ? p / .15 : 1; c.drawImage(m.spr, px - r, py - r, r * 2, r * 2);
    }
  });
}
// rainbow rays that burst out and turn slowly
function rays39(x, y, cw, d, dur) {
  addVfx(d, dur, (c, t, now) => {
    const L = cw * (1.5 + 9 * easeOut(Math.min(1, t * 1.6))), a = t < .1 ? t / .1 : 1 - (t - .1) / .9, rot = now / 900, n = 14, w = TAU / n * .32;
    for (let i = 0; i < n; i++) {
      const an = rot + i * TAU / n;
      c.globalAlpha = .38 * a; c.fillStyle = RAINBOW[i % 6];
      c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.cos(an - w) * L, y + Math.sin(an - w) * L); c.lineTo(x + Math.cos(an + w) * L, y + Math.sin(an + w) * L); c.closePath(); c.fill();
    }
  });
}
// the board goes a little dark around the bowl while it charges
function dim39(d, dur, x, y) {
  later(d, () => {
    const b = boardEl.getBoundingClientRect(), e = document.createElement('div'); e.className = 'dim39';
    e.style.setProperty('--fx', ((x - b.left) / b.width * 100).toFixed(1) + '%'); e.style.setProperty('--fy', ((y - b.top) / b.height * 100).toFixed(1) + '%');
    boardEl.appendChild(e);
    e.animate([{ opacity: 0 }, { opacity: 1, offset: .85 }, { opacity: 0 }], { duration: dur, fill: 'forwards' }).onfinish = () => e.remove();
    setTimeout(() => e.remove(), dur + 300);
  });
}
function feastFx(k, added, delay, base, clear) {
  const R = k / N | 0, C = k % N, CH = FEAST39_CH, bang = base + CH, [x, y, cw] = cellXY(k);
  // the bowl stays till the bang, the other one flies into it
  delay.set(k, bang);
  let k2 = -1;
  for (const [dr, dc] of D4) { const r2 = R + dr, c2 = C + dc, q = r2 * N + c2; if (inB(r2, c2) && clear.has(q) && grid[r2][c2] && grid[r2][c2].type === 'bowl') { k2 = q; break; } }
  if (k2 >= 0) delay.set(k2, base + Math.round(CH * .5));
  // the wave: every treat goes when the rainbow ring reaches it
  for (const q of added) if (q !== k2) delay.set(q, bang + 50 + Math.round(cellDist(q, k) * 52));
  calloutDelay39 = CH;
  if (audioOk()) SFX.feast(base / 1000);
  if (REDUCED) { later(bang, bigShake); return; }
  const bowl = grid[R][C], elA = bowl && els.get(bowl.id);
  later(base, () => { if (elA) { elA.style.setProperty('--ch', CH + 'ms'); elA.classList.add('feast39'); } boardEl.classList.add('quake39'); });
  later(bang, () => boardEl.classList.remove('quake39'));
  if (k2 >= 0) {
    const b2 = grid[k2 / N | 0][k2 % N], el2 = b2 && els.get(b2.id), dx = (C - k2 % N) * 100, dy = (R - (k2 / N | 0)) * 100;
    later(base, () => { if (el2) { el2.style.zIndex = 6; el2.animate([{ transform: 'none' }, { transform: `translate(${dx * .35}%,${dy * .35}%) rotate(-30deg) scale(1.15)`, offset: .45 }, { transform: `translate(${dx}%,${dy}%) rotate(-200deg) scale(.4)`, opacity: .6 }],
      { duration: CH * .5, easing: 'cubic-bezier(.5,0,.75,.3)', fill: 'forwards' }); } });
    later(base + CH * .5, () => { orb(x, y, cw * .2, cw * 1.5, ['#ffffff', 'rgba(255,238,170,.95)', 'rgba(255,120,200,.5)'], 0, 260, .25); burst(x, y, 14, 1.2, RAINBOW, 'star'); });
  }
  // the charge
  dim39(base, CH + 260, x, y);
  halo(x, y, cw * 1.2, base, CH + 120);
  orb(x, y, cw * .2, cw * 1.9, ['#ffffff', 'rgba(255,238,170,.95)', 'rgba(255,120,200,.5)'], base, CH, .92);
  suckIn(x, y, cw, base, CH);
  vortex(x, y, cw * .45, base + CH * .3, CH * .7 + 120);
  // the bang
  boardFlash(.45, bang, 380);
  orb(x, y, cw * .6, cw * 3.4, ['#ffffff', 'rgba(255,250,220,.95)', 'rgba(255,140,220,.5)'], bang, 520, .2);
  RAINBOW.forEach((col, i) => shock(x, y, cw * .5, cw * (6.5 + i * .4), col, bang + i * 40, 760, cw * .38, i === 0 ? 'rgba(255,255,255,1)' : null));
  rays39(x, y, cw, bang, 1200);
  added.forEach((q, i) => {
    if (q === k2) return;
    const [tx, ty] = cellXY(q), at = delay.get(q), col = RAINBOW[i % 6];
    if (i % 2 === 0) orb(tx, ty, cw * .15, cw * .9, ['#ffffff', withA(col, .9), withA(col, .35)], at - 30, 260, .35);
    if (i % 3 === 0) sparks(tx, ty, 4, col, cw * .15, at);
  });
  for (let i = 0; i < Q(18); i++) twinkle(x + (Math.random() - .5) * cw * 9, y + (Math.random() - .5) * cw * 9, cw * (.16 + Math.random() * .12), bang + 150 + Math.random() * 600);
  later(bang, () => burst(x, y, 34, 2.6, RAINBOW, 'star'));
  later(bang + 10, bigShake); later(bang + 380, bigShake);
}

/* ---------- Nachschlag: the new board swirls round and round into the middle, and Freyr gulps it all down ---------- */
let suck39 = null;
const popFx39 = popFx;
popFx = function (k) { if (suck39 && suck39.has(k)) { suck39.delete(k); return; } return popFx39.apply(this, arguments); };
const nachschlag39 = nachschlag;
nachschlag = async function () {
  if (!FX39) return nachschlag39();
  const mid = (N - 1) / 2, items = [];
  for (let k = 0; k < N * N; k++) { const r = k / N | 0, c = k % N; if (!mask[r][c] || !grid[r][c]) continue; items.push([k, Math.hypot(c - mid, r - mid), Math.atan2(r - mid, c - mid)]); }
  if (!items.length) return;
  const maxR = Math.max(...items.map(i => i[1])) || 1, bd = new Map(), F = 480;
  // the outer ring first, along a turning arm, so it looks like a whirlpool
  for (const [k, rad, ang] of items) {
    const out = 1 - rad / maxR, arm = (((ang + Math.PI) / TAU + out * 1.4) % 1);
    bd.set(k, Math.round(F + 80 + out * 650 + arm * 420));
  }
  // always the same length (1.6 s), so the sound fits
  const mx = Math.max(...bd.values()), s0 = F + 80, LAST = 1600;
  for (const [k, v] of bd) bd.set(k, Math.round(s0 + (v - s0) * (LAST - s0) / Math.max(1, mx - s0)));
  const last = LAST;
  callout('Nachschlag!', 'Noch eine Runde Festmahl'); buzz([40, 60, 40]);
  if (audioOk()) SFX.whirl(.05, 1.66);
  if (!REDUCED) {
    const b = boardGeo(), cw = b.cw, x = b.left + b.w / 2, y = b.top + b.h / 2;
    vortex(x, y, cw, 0, last + 300);
    halo(x, y, cw, 80, last + 200);
    orb(x, y, cw * .3, cw * 1.6, ['#ffffff', 'rgba(255,236,170,.9)', 'rgba(255,120,200,.45)'], 0, last + 60, .9);
    for (const [k] of items) {
      const cell = grid[k / N | 0][k % N], el = cell && els.get(cell.id); if (!el) continue;
      const r = k / N | 0, c = k % N, dx = (mid - c) * 100, dy = (mid - r) * 100, d = bd.get(k), turn = (c - mid) * (r - mid) >= 0 ? 1 : -1;
      // a curved path in: a quarter turn round the middle on the way
      const ang = .9 * turn, mx = dx * .55 * Math.cos(ang) - dy * .55 * Math.sin(ang), my = dx * .55 * Math.sin(ang) + dy * .55 * Math.cos(ang);
      later(d - F, () => el.animate([{ transform: 'none' }, { transform: `translate(${(dx - mx).toFixed(0)}%,${(dy - my).toFixed(0)}%) rotate(${180 * turn}deg) scale(.7)`, offset: .55 },
        { transform: `translate(${dx}%,${dy}%) rotate(${420 * turn}deg) scale(.12)`, opacity: .2 }], { duration: F, easing: 'cubic-bezier(.45,0,.85,.55)', fill: 'forwards' }));
    }
    // the gulp in the middle
    later(last + 40, () => {
      orb(x, y, cw * .4, cw * 3.2, ['#ffffff', 'rgba(255,250,220,.95)', 'rgba(255,140,220,.5)'], 0, 420, .2);
      shock(x, y, cw * .4, cw * 5, '#FFE14D', 0, 560, cw * .3, 'rgba(255,190,255,1)');
      burst(x, y, 30, 2.4, ['#FF6FB5', '#FFB547', '#FFE14D', '#7CDB5A', '#43B6FF', '#B57CFF']); bigShake();
    });
  }
  suck39 = new Set(REDUCED ? [] : items.map(i => i[0]));
  try { await resolve(new Set(items.map(i => i[0])), null, '', null, false, bd); } finally { suck39 = null; }
};

/* ---------- won with the very last move: a heartbeat, then "Auf den letzten Drücker!" slams in ---------- */
let clutch39 = false;
function clutchFx() {
  return new Promise(res => {
    if (REDUCED) { callout('Auf den letzten Drücker!'); return setTimeout(res, 900); }
    const BEAT = 1000;
    if (audioOk()) SFX.clutch(0, BEAT / 1000);
    const v = document.createElement('div'); v.className = 'clutch39'; document.body.appendChild(v);
    v.animate([{ opacity: 0 }, { opacity: 1, offset: .25 }, { opacity: 1, offset: .8 }, { opacity: 0 }], { duration: BEAT + 380, fill: 'forwards' });
    const bw = $('boardwrap'), mv = $('moves');
    [0, 520].forEach(t => setTimeout(() => { bw.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.035)', offset: .25 }, { transform: 'scale(.995)', offset: .55 }, { transform: 'scale(1)' }], { duration: 380 }); buzz(30); }, t));
    if (mv) mv.classList.add('clutch39');
    setTimeout(() => {
      if (mv) mv.classList.remove('clutch39');
      const t = document.createElement('div'); t.className = 'clutchtxt disp'; t.innerHTML = '<span>Auf den letzten</span><span>Drücker!</span>';
      document.body.appendChild(t);
      t.animate([{ transform: 'translate(-50%,-50%) scale(3.2) rotate(-14deg)', opacity: 0 }, { transform: 'translate(-50%,-50%) scale(.88) rotate(3deg)', opacity: 1, offset: .16 },
        { transform: 'translate(-50%,-50%) scale(1.06) rotate(-3deg)', offset: .26 }, { transform: 'translate(-50%,-50%) scale(1) rotate(-2deg)', offset: .36 },
        { transform: 'translate(-50%,-50%) scale(1.04) rotate(-2deg)', offset: .8, opacity: 1 }, { transform: 'translate(-50%,-160%) scale(.7) rotate(-2deg)', opacity: 0 }], { duration: 1500, easing: 'ease-out', fill: 'forwards' })
        .onfinish = () => t.remove();
      setTimeout(() => t.remove(), 2000);
      const b = t.getBoundingClientRect(), x = innerWidth / 2, y = b.top + b.height / 2, cw = Math.min(innerWidth, 480) / 9;
      orb(x, y, cw * .5, cw * 4, ['#ffffff', 'rgba(255,236,150,.95)', 'rgba(255,170,60,.45)'], 0, 420, .2);
      shock(x, y, cw * .5, cw * 6, '#FFD23F', 40, 620, cw * .3, 'rgba(255,230,140,1)');
      shock(x, y, cw * .4, cw * 4.5, '#FF4F9A', 120, 520, cw * .18);
      sparks(x, y, 30, '#FFD23F', cw * .3);
      // confetti cannons from both bottom corners
      const cols = ['#FFD23F', '#FF4F9A', '#43B6FF', '#7CDB5A', '#B57CFF', '#ffffff', '#FF8A3D'];
      for (const side of [-1, 1]) for (let i = 0; i < Q(46); i++) {
        // aimed up and inwards, a little spread
        const sp = 9 + Math.random() * 9, dl = .18 + Math.random() * .5;
        addPart({ x: side < 0 ? 0 : innerWidth, y: innerHeight + 10, vx: -side * Math.sin(dl) * sp, vy: -Math.cos(dl) * sp * 1.25, g: .22, life: 1.3, decay: .008 + Math.random() * .008,
          size: 7 + Math.random() * 7, rot: Math.random() * 6, vr: (Math.random() - .5) * .5, color: cols[i % cols.length], shape: ['shard', 'star', 'heart', 'dot'][i % 4] });
      }
      bigShake(); buzz([50, 40, 80]);
      mascot.animate([{ transform: 'none' }, { transform: 'translateY(-40%) rotate(-180deg) scale(1.1)', offset: .45 }, { transform: 'translateY(0) rotate(-360deg)', offset: .8 }, { transform: 'none' }], { duration: 800, easing: 'cubic-bezier(.3,.7,.4,1)' });
      setTimeout(res, 1250);
    }, BEAT);
  });
}
const winSeq39 = winSequence;
winSequence = async function () {
  clutch39 = false;
  if (FX39 && moves === 0) { clutch39 = true; ending = true; cancelAim(true); await clutchFx(); }
  try { return await winSeq39.apply(this, arguments); } finally { clutch39 = false; }
};
const say39 = say;
say = function (text) { return say39.call(this, clutch39 && text === 'Ich bin satt und glücklich!' ? 'Puh, das war knapp! Aber satt bin ich.' : text); };
const celebrate39 = celebrate;
celebrate = function () {
  const r = celebrate39.apply(this, arguments);
  if (clutch39) { const w = [...document.querySelectorAll('.celebrate .bigwin')].pop(); if (w) w.textContent = 'Puh, geschafft!'; }
  return r;
};
