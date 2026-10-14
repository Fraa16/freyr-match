
/* ===================== V28: one fast layer for every effect ===================== */
// Everything that glows, sparks or flies is drawn on the one effects canvas, from small pictures made once
// (balls of light, stars, shards, hearts ...). Nothing builds gradients while it runs, there is no second canvas
// and no blend mode over the whole screen. Movement is timed by the clock, so a slow frame never slows the effect down,
// and when frames get slow the effects get lighter by themselves.
const TAU = Math.PI * 2;
const easeOut = t => 1 - Math.pow(1 - t, 3);
const RAINBOW = ['#FF4FA3', '#FFA42E', '#FFE14D', '#5FE04A', '#3EB8FF', '#B07CFF'];
const withA = (hex, a) => { const n = parseInt(hex.slice(1), 16); return 'rgba(' + (n >> 16) + ',' + (n >> 8 & 255) + ',' + (n & 255) + ',' + a + ')'; };
// the same colour, fully transparent (gradients fade to it, so no dark rim)
function clear0(col) {
  if (col[0] === '#') return withA(col.length === 4 ? '#' + col[1] + col[1] + col[2] + col[2] + col[3] + col[3] : col, 0);
  const m = col.match(/rgba?\(([^,]+),([^,]+),([^,)]+)/); return m ? 'rgba(' + m[1] + ',' + m[2] + ',' + m[3] + ',0)' : 'rgba(255,255,255,0)';
}

/* ---------- quality: slow frames make the next effects lighter, good frames bring them back ---------- */
const fxq = { q: 1, slow: 0, good: 0 };
const Q = n => n <= 0 ? 0 : Math.max(1, Math.round(n * fxq.q));
function fxRate(dt) {
  if (dt > 25) { fxq.good = 0; if (++fxq.slow >= 10) { fxq.slow = 0; fxq.q = Math.max(.35, fxq.q - .1); } }
  else if (dt < 19) { fxq.slow = Math.max(0, fxq.slow - 1); if (++fxq.good >= 40) { fxq.good = 0; fxq.q = Math.min(1, fxq.q + .1); } }
}

/* ---------- the canvas: 1.5x on sharp screens is plenty for light and flying bits ---------- */
let FXS = 1;
const fxScaleFor = () => { const d = devicePixelRatio || 1; return d < 1.5 ? 1 : fxq.q > .8 ? Math.min(1.5, d) : fxq.q > .55 ? 1.25 : 1; };
sizeFx = function () {
  FXS = fxScaleFor(); dpr = FXS;
  fx.width = Math.round(innerWidth * FXS); fx.height = Math.round(innerHeight * FXS);
  fx.style.width = innerWidth + 'px'; fx.style.height = innerHeight + 'px';
};

/* ---------- sprites, made once ---------- */
const SPR = new Map();
function mkCv(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function spr(key, w, h, paint) { let s = SPR.get(key); if (!s) { s = mkCv(w, h); paint(s.getContext('2d'), w, h); SPR.set(key, s); } return s; }
// a ball of light: c0 in the middle, c1 at 28 %, c2 at 62 %, nothing at the rim
const glowSpr = (c0, c1, c2) => spr('g' + c0 + c1 + c2, 128, 128, (c) => {
  const g = c.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, c0); g.addColorStop(.28, c1); g.addColorStop(.62, c2); g.addColorStop(1, clear0(c2)); c.fillStyle = g; c.fillRect(0, 0, 128, 128);
});
// a four-pointed star with a soft glow (base size 28)
const TW = 28;
const twinkleSpr = () => spr('tw', 96, 96, (c) => {
  const x = 48, y = 48, s = TW, g = c.createRadialGradient(x, y, 0, x, y, s * 1.7);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.28, 'rgba(255,244,214,.45)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  c.fillStyle = g; c.beginPath(); c.arc(x, y, s * 1.7, 0, TAU); c.fill();
  c.fillStyle = '#fff'; c.beginPath();
  c.moveTo(x, y - s); c.quadraticCurveTo(x + s * .1, y - s * .1, x + s, y); c.quadraticCurveTo(x + s * .1, y + s * .1, x, y + s);
  c.quadraticCurveTo(x - s * .1, y + s * .1, x - s, y); c.quadraticCurveTo(x - s * .1, y - s * .1, x, y - s); c.fill();
});
// a spark: a short bright streak, 48 long between its round caps
const sparkSpr = col => spr('s' + col, 64, 16, (c) => {
  c.lineCap = 'round'; c.strokeStyle = col; c.lineWidth = 10; c.beginPath(); c.moveTo(8, 8); c.lineTo(56, 8); c.stroke();
  c.strokeStyle = '#fff'; c.lineWidth = 3.6; c.stroke();
});
// the soap bubble round a treat that bursts (radius 40)
const bubbleSpr = () => spr('bub', 96, 96, (c) => {
  c.strokeStyle = 'rgba(255,255,255,.7)'; c.lineWidth = 3.4; c.beginPath(); c.arc(48, 48, 40, 0, TAU); c.stroke();
  c.strokeStyle = 'rgba(255,255,255,.85)'; c.lineWidth = 5.2; c.lineCap = 'round'; c.beginPath(); c.arc(48, 48, 30.4, 3.55, 4.55); c.stroke();
});
// the bowl's turning rainbow ring and the thin white ring that turns the other way (radius 40)
const haloSpr = () => spr('halo', 112, 112, (c) => {
  c.lineCap = 'round'; c.lineWidth = 8.2;
  for (let i = 0; i < 12; i++) { const a0 = i * TAU / 12; c.strokeStyle = RAINBOW[i % 6]; c.globalAlpha = .75; c.beginPath(); c.arc(56, 56, 40, a0, a0 + TAU / 12 * .62); c.stroke(); }
});
const haloWSpr = () => spr('haloW', 112, 112, (c) => { c.lineCap = 'round'; c.globalAlpha = .55; c.strokeStyle = '#fff'; c.lineWidth = 2.6; c.beginPath(); c.arc(56, 56, 47, 0, TAU * .7); c.stroke(); });
// the cat's beam across: a strip that is clear at both edges and full in the middle
const stripSpr = (col, vert) => spr('st' + col + vert, vert ? 64 : 1, vert ? 1 : 64, (c, w, h) => {
  const g = vert ? c.createLinearGradient(0, 0, 64, 0) : c.createLinearGradient(0, 0, 0, 64);
  g.addColorStop(0, clear0(col)); g.addColorStop(.5, col); g.addColorStop(1, clear0(col)); c.fillStyle = g; c.fillRect(0, 0, w, h);
});
// the laser dot: white hot middle, pink glow
const laserDotSpr = () => spr('ldot', 128, 128, (c) => {
  const g = c.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, '#ffffff'); g.addColorStop(.14, '#ffffff'); g.addColorStop(.26, 'rgba(255,80,125,.98)'); g.addColorStop(.5, 'rgba(255,46,99,.45)'); g.addColorStop(1, 'rgba(255,46,99,0)');
  c.fillStyle = g; c.fillRect(0, 0, 128, 128);
});
// flying bits: hearts, stars, kibble, paws, confetti, dots, leaves and shards, one per shape and colour (base size 32 in a 48 box)
function shapePath(c, shape, s) {
  c.beginPath();
  if (shape === 'heart') { c.moveTo(0, s * .7); c.bezierCurveTo(-s * 1.5, -s * .3, -s * .6, -s * 1.4, 0, -s * .45); c.bezierCurveTo(s * .6, -s * 1.4, s * 1.5, -s * .3, 0, s * .7); }
  else if (shape === 'star') { for (let i = 0; i < 10; i++) { const r = i % 2 ? s * .45 : s, a = i * Math.PI / 5 - Math.PI / 2; c.lineTo(Math.cos(a) * r, Math.sin(a) * r); } c.closePath(); }
  else if (shape === 'kibble') {
    const k = s * .5, pts = [-2.62, -.52, 1.57].map(a => [Math.cos(a) * k, Math.sin(a) * k]);
    for (const [x, y] of pts) { c.moveTo(x + k * .8, y); c.arc(x, y, k * .8, 0, TAU); }
    c.moveTo(pts[0][0], pts[0][1]); c.lineTo(pts[1][0], pts[1][1]); c.lineTo(pts[2][0], pts[2][1]); c.closePath();
  } else if (shape === 'paw') {
    c.moveTo(s * .55, s * .3); c.ellipse(0, s * .3, s * .55, s * .45, 0, 0, TAU);
    for (const [x, y] of [[-.62, -.3], [-.22, -.72], [.22, -.72], [.62, -.3]]) { c.moveTo(x * s + s * .22, y * s); c.arc(x * s, y * s, s * .22, 0, TAU); }
  } else if (shape === 'rect') c.rect(-s, -s * .45, s * 2, s * .9);
  else if (shape === 'leaf') { c.moveTo(0, -s); c.quadraticCurveTo(s * .95, 0, 0, s); c.quadraticCurveTo(-s * .95, 0, 0, -s); }
  else if (shape === 'shard') { c.moveTo(-s, -s * .25); c.quadraticCurveTo(-s * .1, -s * 1.15, s, -s * .45); c.lineTo(s * .35, s * .75); c.quadraticCurveTo(-s * .2, s * .2, -s, -s * .25); }
  else c.arc(0, 0, s * .6, 0, TAU);
}
const shapeSpr = (shape, col) => spr('p' + shape + col, 48, 48, (c) => {
  const s = 16; c.translate(24, 24); c.fillStyle = col; shapePath(c, shape, s); c.fill();
  if (shape === 'leaf') { c.strokeStyle = 'rgba(255,255,255,.6)'; c.lineWidth = Math.max(1, s * .14); c.beginPath(); c.moveTo(0, -s * .75); c.lineTo(0, s * .75); c.stroke(); }
  if (shape === 'shard') { c.globalAlpha = .75; c.strokeStyle = 'rgba(255,255,255,.9)'; c.lineWidth = Math.max(1, s * .22); c.lineCap = 'round'; c.beginPath(); c.moveTo(-s * .55, -s * .35); c.quadraticCurveTo(-s * .05, -s * .82, s * .55, -s * .48); c.stroke(); }
});

/* ---------- the loop ---------- */
let vfx = [], lights = [], fxLast = 0, fxMoved = false;
const MAXP = 320, MAXL = 220, MAXV = 240;
function kickFx() { if (!fxRaf) { fxLast = 0; fxRaf = requestAnimationFrame(fxLoop); } }
addPart = function (p) { if (parts.length >= MAXP * fxq.q + 40) return; parts.push(p); kickFx(); };
// a light effect: draw(ctx, t 0..1, now) for dur ms, starting after delay ms
function addVfx(delay, dur, draw) { if (REDUCED || vfx.length >= MAXV) return; vfx.push({ t0: performance.now() + delay, dur, draw }); kickFx(); }
function compact(arr, keep) { let j = 0; for (let i = 0; i < arr.length; i++) { const x = arr[i]; if (keep(x)) arr[j++] = x; } arr.length = j; }
fxLoop = function (ts) {
  const now = performance.now(), c = fctx, S = FXS;
  let dt = fxLast ? now - fxLast : 16.7; fxLast = now;
  if (fxLast && dt < 200) fxRate(dt);
  const k = Math.min(3, Math.max(.25, dt / 16.667));
  c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  c.clearRect(0, 0, fx.width, fx.height);
  // the light first, added up like light
  compact(vfx, v => now < v.t0 + v.dur);
  c.globalCompositeOperation = 'lighter';
  c.setTransform(S, 0, 0, S, 0, 0);
  for (let i = 0; i < vfx.length; i++) {
    const v = vfx[i]; if (now < v.t0) continue;
    c.globalAlpha = 1;
    try { v.draw(c, (now - v.t0) / v.dur, now); } catch (e) { c.setTransform(S, 0, 0, S, 0, 0); }
  }
  compact(lights, l => now < l.t0 + l.dur);
  const tw = twinkleSpr();
  for (let i = 0; i < lights.length; i++) {
    const l = lights[i]; if (now < l.t0) continue;
    const u = (now - l.t0) / l.dur;
    l.vy += l.g * k; l.x += l.vx * k; l.y += l.vy * k; l.vx *= 1 - .04 * k; l.vy *= 1 - .03 * k;
    if (l.kind === 'tw') {
      const s = l.s * Math.sin(Math.PI * Math.min(1, u * 1.15)); if (s <= .3) continue;
      const m = s / TW * S; c.setTransform(m, 0, 0, m, l.x * S, l.y * S); c.globalAlpha = 1 - u * .5; c.drawImage(tw, -48, -48);
    } else {
      const sp = l.spr || (l.spr = sparkSpr(l.col)), len = Math.max(2, l.sp * (1 - u * .6) * 3), th = l.w * 2.2;
      const cs = l.cs, sn = l.sn, sx = len / 48 * S, sy = th / 10 * S;
      c.setTransform(cs * sx, sn * sx, -sn * sy, cs * sy, (l.x - l.vx * 1.5) * S, (l.y - l.vy * 1.5) * S);
      c.globalAlpha = 1 - u; c.drawImage(sp, -32, -8);
    }
  }
  // then the flying bits
  c.globalCompositeOperation = 'source-over';
  const H = innerHeight + 40;
  compact(parts, p => p.life > 0 && p.y < H);
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    p.vy += p.g * k; p.x += p.vx * k; p.y += p.vy * k; p.vx *= 1 - .015 * k; p.rot += p.vr * k; p.life -= p.decay * k;
    const a = p.life * 1.6; if (a <= .01) continue;
    const sp = p.spr || (p.spr = shapeSpr(p.shape || 'dot', p.color)), m = p.size / 32 * S, cs = Math.cos(p.rot) * m, sn = Math.sin(p.rot) * m;
    c.setTransform(cs, sn, -sn, cs, p.x * S, p.y * S); c.globalAlpha = a > 1 ? 1 : a; c.drawImage(sp, -24, -24);
  }
  c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  const more = parts.length || vfx.length || lights.length;
  fxRaf = more ? requestAnimationFrame(fxLoop) : null;
  if (!more) { c.clearRect(0, 0, fx.width, fx.height); fxLast = 0; if (fxScaleFor() !== FXS) sizeFx(); }
};
burst = function (x, y, n, power = 1, cols = PCOL, shape) {
  if (REDUCED) n = Math.ceil(n / 3); else n = Q(n);
  for (let i = 0; i < n; i++) {
    const a = Math.random() * TAU, sp = (1.5 + Math.random() * 3.5) * power, r = Math.random();
    addPart({ x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - 1.5, g: .16, life: 1, decay: .018 + Math.random() * .018,
      size: 5 + Math.random() * 6, rot: Math.random() * 6, vr: (Math.random() - .5) * .3,
      color: !shape && r >= .62 && r < .82 ? '#A9744F' : cols[Math.floor(Math.random() * cols.length)], shape: shape || (r < .35 ? 'heart' : r < .62 ? 'star' : r < .82 ? 'kibble' : 'dot') });
  }
};

/* ---------- light primitives ---------- */
function twinkle(x, y, s, delay = 0) {
  if (REDUCED || lights.length >= MAXL * fxq.q) return;
  lights.push({ kind: 'tw', x, y, s, vx: (Math.random() - .5) * .5, vy: -.3 - Math.random() * .4, g: .025, t0: performance.now() + delay, dur: 520 + Math.random() * 420 }); kickFx();
}
function sparks(x, y, n, col, speed, delay = 0) {
  if (REDUCED) return;
  n = Math.min(Q(n), Math.max(0, Math.floor(MAXL * fxq.q - lights.length)));
  const t0 = performance.now() + delay;
  for (let i = 0; i < n; i++) {
    const a = Math.random() * TAU, s = speed * (.45 + Math.random() * .9);
    const cs = Math.cos(a), sn = Math.sin(a);
    lights.push({ kind: 'sp', x, y, vx: cs * s, vy: sn * s, cs, sn, sp: s, g: .06, t0, dur: 240 + Math.random() * 220, col, w: 1.1 + Math.random() * 1.3 });
  }
  if (n) kickFx();
}
// a ball of light: white in the middle, then the colour, growing from r0 to r1
function orb(x, y, r0, r1, cols, delay, dur, hold = .3) {
  const sp = glowSpr(cols[0], cols[1], cols[2]);
  addVfx(delay, dur, (c, t) => {
    const r = r0 + (r1 - r0) * easeOut(t), a = t < hold ? 1 : 1 - (t - hold) / (1 - hold);
    if (r <= .5 || a <= 0) return;
    c.globalAlpha = a; c.drawImage(sp, x - r, y - r, r * 2, r * 2);
  });
}
// a shockwave: a bright ring running outwards, optionally over a faint disc
function shock(x, y, r0, r1, col, delay, dur, width, fill) {
  addVfx(delay, dur, (c, t) => {
    const r = r0 + (r1 - r0) * easeOut(t), a = 1 - t, w = Math.max(.5, width * (1 - .65 * t));
    if (fill) { c.globalAlpha = .22 * a; c.fillStyle = fill; c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill(); }
    c.globalAlpha = .85 * a; c.strokeStyle = col; c.lineWidth = w; c.beginPath(); c.arc(x, y, r, 0, TAU); c.stroke();
    c.globalAlpha = .8 * a; c.strokeStyle = '#fff'; c.lineWidth = w * .32; c.stroke();
  });
}
function boardFlash(alpha, delay, dur, col = '#ffffff') {
  addVfx(delay, dur, (c, t) => {
    const b = boardGeo(); c.globalAlpha = alpha * (1 - easeOut(t)); c.fillStyle = col;
    c.beginPath(); if (c.roundRect) c.roundRect(b.left, b.top, b.w, b.h, 18); else c.rect(b.left, b.top, b.w, b.h); c.fill();
  });
}
// lightning: a jagged line that shoots out, crackles (a new shape every few frames) and fades
function boltPts(x1, y1, x2, y2, jag, steps) {
  let pts = [[x1, y1], [x2, y2]], off = Math.hypot(x2 - x1, y2 - y1) * jag;
  for (let it = 0; it < steps; it++) {
    const np = [pts[0]];
    for (let i = 1; i < pts.length; i++) {
      const [ax, ay] = pts[i - 1], [bx, by] = pts[i], dx = bx - ax, dy = by - ay, l = Math.hypot(dx, dy) || 1, o = (Math.random() - .5) * off;
      np.push([(ax + bx) / 2 - dy / l * o, (ay + by) / 2 + dx / l * o], [bx, by]);
    }
    pts = np; off *= .56;
  }
  return pts;
}
function strokePts(c, pts, upto) {
  const n = Math.max(1, Math.round((pts.length - 1) * upto));
  c.beginPath(); c.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i <= n; i++) c.lineTo(pts[i][0], pts[i][1]); c.stroke();
}
function bolt(x1, y1, x2, y2, col, delay, dur, w = 1, light = false) {
  let pts = null, br = [], last = 0;
  const len = Math.hypot(x2 - x1, y2 - y1), dir = Math.atan2(y2 - y1, x2 - x1);
  addVfx(delay, dur, (c, t, now) => {
    if (!pts || now - last > 70) {
      last = now; pts = boltPts(x1, y1, x2, y2, .2, 4); br = [];
      if (!light) for (let b = 0; b < 2 && pts.length > 8; b++) {
        const [bx, by] = pts[3 + Math.floor(Math.random() * (pts.length - 6))], a = dir + (Math.random() - .5) * 1.7, bl = len * (.12 + Math.random() * .2);
        br.push(boltPts(bx, by, bx + Math.cos(a) * bl, by + Math.sin(a) * bl, .3, 3));
      }
    }
    const grow = Math.min(1, t / .22), fade = t < .55 ? 1 : 1 - (t - .55) / .45;
    c.lineJoin = c.lineCap = 'round';
    c.strokeStyle = col; c.globalAlpha = .45 * fade; c.lineWidth = 8 * w; strokePts(c, pts, grow);
    c.strokeStyle = '#fff'; c.globalAlpha = .95 * fade; c.lineWidth = 2 * w; strokePts(c, pts, grow);
    if (grow >= 1) for (const b of br) { c.strokeStyle = col; c.globalAlpha = .7 * fade; c.lineWidth = 2.4 * w; strokePts(c, b, 1); }
  });
}

/* ---------- every treat that goes: it bursts into pieces in its own colour, in a soap bubble, with a few twinkles ---------- */
const SHARDS = [['#3B9BFF', '#9AD6FF', '#1D5FD0'], ['#FF3D8F', '#FF9CC8', '#C8186A'], ['#FFF3E0', '#FFC992', '#FF7AA8'],
  ['#ECE6FF', '#BBA8F2', '#FF9EC4'], ['#C9702F', '#EDA463', '#8A4518'], ['#8A4BFF', '#C29CFF', '#FFF1C8']];
const XSHARDS = { cat: ['#FFFFFF', '#FFB3C9', '#F07CA0'], nip: ['#5ED83C', '#B8F0A8', '#2FA84A'], laser: ['#FF2E63', '#FF9AB3', '#FFFFFF'], bowl: RAINBOW, bell: ['#FFD23F', '#FFF1A8', '#E09A00'] };
// many treats at once (a bowl, two bowls): fewer pieces each, so the whole board can go without a hitch
let popWin = 0, popN = 0;
function popFx(k, cell, combo, specials) {
  const [x, y, cw] = cellXY(k);
  if (REDUCED) return burst(x, y, 3, 1);
  const now = performance.now(); if (now - popWin > 120) { popWin = now; popN = 0; } popN++;
  const crowd = popN > 24 ? .4 : popN > 12 ? .65 : 1;
  const pal = cell.gold ? ['#FFD23F', '#FFF1A8', '#E09A00'] : SHARDS[cell.type] || XSHARDS[cell.type] || PCOL;
  const n = Q((cell.gold ? 9 : specials ? 7 : 6) * crowd), f = cw / 46;
  for (let i = 0; i < n; i++) {
    const a = -Math.PI / 2 + (Math.random() - .5) * Math.PI * 1.7, sp = (2 + Math.random() * 3.2) * f * (1 + Math.min(combo, 6) * .05);
    addPart({ x: x + Math.cos(a) * cw * .14, y: y + Math.sin(a) * cw * .14, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - 1.4 * f, g: .27 * f, life: 1,
      decay: .021 + Math.random() * .012, size: cw * (.2 + Math.random() * .15), rot: Math.random() * TAU, vr: (Math.random() - .5) * .45, color: pal[i % pal.length], shape: 'shard' });
  }
  const bub = bubbleSpr();
  addVfx(0, 300, (c, t) => { const r = cw * (.36 + .34 * easeOut(t)), m = r / 40; c.globalAlpha = 1 - t; c.drawImage(bub, x - 48 * m, y - 48 * m, 96 * m, 96 * m); });
  const tw = crowd < 1 ? (Math.random() < crowd ? 1 : 0) : 2;
  for (let i = 0; i < (cell.gold ? 4 : tw); i++) twinkle(x + (Math.random() - .5) * cw, y + (Math.random() - .5) * cw, cw * (.15 + Math.random() * .1), 60 + 110 * i);
  if (cell.gold) sparks(x, y, 8, '#FFD23F', cw * .12);
}
// a new extra appears: a flash of light in its colour and a few twinkles
function spawnFx(k, kind) {
  if (REDUCED) return;
  const [x, y, cw] = cellXY(k), col = { cat: '#FF8FC0', nip: '#7CE84F', laser: '#FF2E63', bowl: '#FFD23F' }[kind] || '#ffffff';
  orb(x, y, cw * .2, cw * (kind === 'bowl' ? 1.6 : 1.1), ['#ffffff', withA(col, .9), withA(col, .35)], 0, kind === 'bowl' ? 520 : 380);
  shock(x, y, cw * .3, cw * (kind === 'bowl' ? 1.9 : 1.2), col, 40, 420, cw * .1);
  for (let i = 0; i < Q(kind === 'bowl' ? 7 : 4); i++) twinkle(x + (Math.random() - .5) * cw * 1.4, y + (Math.random() - .5) * cw * 1.4, cw * (.14 + Math.random() * .1), 60 + i * 70);
}

/* ---------- Laserpunkt: a glowing dot races from treat to treat with a comet tail, Freyr's paw swipes at every landing ---------- */
function claw(x, y, cw, delay, dir) {
  addVfx(delay, 320, (c, t) => {
    const draw = Math.min(1, t / .28), a = t < .45 ? 1 : 1 - (t - .45) / .55;
    c.lineCap = 'round';
    for (let m = -1; m <= 1; m++) {
      const ox = m * cw * .26, len = cw * (m ? .82 : 1);
      const x1 = x + ox - dir * len * .42, y1 = y - len * .5, x2 = x + ox + dir * len * .42, y2 = y + len * .5;
      const qx = x + ox + dir * cw * .1 - m * cw * .04, qy = y - cw * .06;
      const ex = x1 + (x2 - x1) * draw, ey = y1 + (y2 - y1) * draw;
      c.beginPath(); c.moveTo(x1, y1); c.quadraticCurveTo(qx, qy, ex, ey);
      c.globalAlpha = .55 * a; c.strokeStyle = '#FF2E63'; c.lineWidth = cw * .26; c.stroke();
      c.globalAlpha = a; c.strokeStyle = '#ffffff'; c.lineWidth = cw * .07; c.stroke();
    }
  });
}
function laserFx(from, targets, d) {
  if (REDUCED || !targets.length) return;
  const P = [from, ...targets].map(k => cellXY(k)), cw = P[0][2], legs = P.length - 1, total = LEG * legs;
  orb(P[0][0], P[0][1], cw * .1, cw * .85, ['#ffffff', 'rgba(255,96,140,.95)', 'rgba(255,46,99,.45)'], d, 240, .2);
  shock(P[0][0], P[0][1], cw * .2, cw * 1, '#FF4F7E', d + 30, 280, cw * .12);
  const trail = [], dot = laserDotSpr();
  addVfx(d, total + 220, (c, t, now) => {
    const ms = t * (total + 220), alive = ms < total;
    let x, y;
    if (alive) {
      const i = Math.min(legs - 1, Math.floor(ms / LEG)), u = (ms - i * LEG) / LEG, e = u < .5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
      const [ax, ay] = P[i], [bx, by] = P[i + 1], dx = bx - ax, dy = by - ay, l = Math.hypot(dx, dy) || 1, bend = Math.min(cw * 1.3, l * .32) * (i % 2 ? 1 : -1);
      const qx = (ax + bx) / 2 - dy / l * bend, qy = (ay + by) / 2 + dx / l * bend;
      x = (1 - e) * (1 - e) * ax + 2 * (1 - e) * e * qx + e * e * bx; y = (1 - e) * (1 - e) * ay + 2 * (1 - e) * e * qy + e * e * by;
      trail.push([x, y, now]);
    }
    while (trail.length && now - trail[0][2] > 240) trail.shift();
    if (alive && (!trail.sp || now - trail.sp > 34)) { trail.sp = now; sparks(x, y, 2, '#FF9AB3', cw * .05); if (Math.random() < .4) twinkle(x + (Math.random() - .5) * cw * .5, y + (Math.random() - .5) * cw * .5, cw * .12); }
    c.lineCap = 'round';
    for (let j = 1; j < trail.length; j++) {
      const a = j / trail.length;
      c.beginPath(); c.moveTo(trail[j - 1][0], trail[j - 1][1]); c.lineTo(trail[j][0], trail[j][1]);
      c.globalAlpha = .55 * a; c.strokeStyle = '#FF3D74'; c.lineWidth = cw * .6 * a; c.stroke();
      c.globalAlpha = .95 * a; c.strokeStyle = '#FFE3EA'; c.lineWidth = cw * .16 * a; c.stroke();
    }
    if (alive) { const R = cw * (.95 + .12 * Math.sin(now / 35)); c.globalAlpha = 1; c.drawImage(dot, x - R, y - R, R * 2, R * 2); }
  });
  targets.forEach((k, i) => {
    const [x, y] = P[i + 1], at = d + LEG * (i + 1);
    orb(x, y, cw * .25, cw * 1.5, ['#ffffff', 'rgba(255,140,170,.95)', 'rgba(255,46,99,.45)'], at, 320, .22);
    shock(x, y, cw * .3, cw * 1.6, '#FF4F7E', at, 380, cw * .2, 'rgba(255,80,130,1)');
    claw(x, y, cw * 1.25, at + 10, i % 2 ? 1 : -1);
    sparks(x, y, 14, '#FF7096', cw * .2, at);
    for (let j = 0; j < Q(3); j++) twinkle(x + (Math.random() - .5) * cw * 1.4, y + (Math.random() - .5) * cw * 1.4, cw * (.15 + Math.random() * .1), at + 60 + j * 80);
  });
}
laserRun = function (from, targets, d) { laserFx(from, targets, d); };

/* ---------- Festmahl-Napf: the bowl lights up and throws rainbow lightning at every treat it eats ---------- */
function halo(x, y, cw, delay, dur) {
  const h = haloSpr(), hw = haloWSpr(), m = cw * .78 / 40;
  addVfx(delay, dur, (c, t, now) => {
    const a = t < .1 ? t / .1 : t > .8 ? (1 - t) / .2 : 1, rot = now / 260, S = FXS;
    c.globalAlpha = a;
    c.setTransform(Math.cos(rot) * m * S, Math.sin(rot) * m * S, -Math.sin(rot) * m * S, Math.cos(rot) * m * S, x * S, y * S); c.drawImage(h, -56, -56);
    const r2 = -rot * 1.3; c.setTransform(Math.cos(r2) * m * S, Math.sin(r2) * m * S, -Math.sin(r2) * m * S, Math.cos(r2) * m * S, x * S, y * S); c.drawImage(hw, -56, -56);
    c.setTransform(S, 0, 0, S, 0, 0);
  });
}
function vortex(x, y, cw, delay, dur) {
  addVfx(delay, dur, (c, t, now) => {
    const a = t < .15 ? t / .15 : t > .7 ? (1 - t) / .3 : 1, rot = now / 170, R = cw * (2 + 6 * easeOut(t));
    c.lineCap = 'round'; c.lineWidth = cw * .34;
    for (let arm = 0; arm < 6; arm++) {
      c.strokeStyle = RAINBOW[arm]; c.globalAlpha = .5 * a;
      c.beginPath();
      for (let s = 0; s <= 16; s++) { const u = s / 16, ang = rot + arm * TAU / 6 + u * 4.2, rr = R * u; const px = x + Math.cos(ang) * rr, py = y + Math.sin(ang) * rr; if (s) c.lineTo(px, py); else c.moveTo(px, py); }
      c.stroke();
    }
  });
}
function zaps(times) { if (!audioOk()) return; times.slice(0, 14).forEach((at, i) => sweep(3400 - i * 60, 1300, Math.max(0, at) / 1000, .055, 'sawtooth', .014)); }
bowlFx = function (k, targets, delay, d) {
  const [x, y, cw] = cellXY(k), bc = grid[k / N | 0][k % N], all = !!(bc && bc.eat === 'all');
  later(d, () => extraSound('bowl'));
  if (REDUCED) { later(d + 60, bigShake); return; }
  const last = targets.reduce((m, t) => Math.max(m, delay.get(t) || d), d + 280);
  orb(x, y, cw * .25, cw * 2.1, ['#ffffff', 'rgba(255,238,170,.95)', 'rgba(255,120,200,.5)'], d, 460, .25);
  boardFlash(.16, d, 170);
  halo(x, y, cw, d, last - d + 320);
  if (all) vortex(x, y, cw, d, last - d + 500);
  // every treat gets its bolt; on a full board every third one, the others still flash where they go
  const zt = [], step = all && targets.length > 24 ? Math.ceil(targets.length / 22) : 1;
  targets.forEach((t, i) => {
    const [tx, ty] = cellXY(t), at = delay.get(t) || d, col = RAINBOW[i % 6];
    if (i % step === 0) { bolt(x, y, tx, ty, col, Math.max(d + 20, at - 200), 360, all ? .8 : 1, all); zt.push(Math.max(d + 20, at - 200)); }
    orb(tx, ty, cw * .15, cw * .85, ['#ffffff', withA(col, .9), withA(col, .35)], Math.max(d, at - 110), 240, .35);
    sparks(tx, ty, all ? 3 : 5, col, cw * .13, Math.max(d, at - 50));
  });
  zaps(zt);
  shock(x, y, cw * .4, cw * (all ? 8 : 5), '#FFE14D', last + 30, 600, cw * .24, 'rgba(255,190,255,1)');
  shock(x, y, cw * .3, cw * (all ? 6.5 : 4), '#FF7AC6', last + 110, 520, cw * .14);
  for (let i = 0; i < Q(10); i++) twinkle(x + (Math.random() - .5) * cw * 6, y + (Math.random() - .5) * cw * 6, cw * (.15 + Math.random() * .12), last + Math.random() * 300);
  later(d + 60, bigShake); later(last + 40, bigShake);
};

/* ---------- Flitzekatze: a beam of light shoots along the line with the two little cats, with sparks at every cell ---------- */
function catBeam(r, c, dir, d) {
  if (REDUCED) return;
  const k0 = r * N + c, [x0, y0, cw] = cellXY(k0), horiz = dir === 'h', span = N * 30 + 60, b = boardGeo();
  const layers = [[2.2, .22, stripSpr('#FF8FC0', !horiz)], [1, .55, stripSpr('#FFB3D1', !horiz)], [.34, .95, stripSpr('#ffffff', !horiz)]];
  addVfx(d, span + 420, (cx, t) => {
    const ms = t * (span + 420), reach = Math.min(1, ms / span) * N * cw, a = ms < span ? 1 : 1 - (ms - span) / 420;
    const w = cw * (.7 + .25 * Math.sin(ms / 40));
    for (const [f, al, sp] of layers) {
      const ww = w * f; cx.globalAlpha = al * a;
      if (horiz) { const l = Math.max(b.left, x0 - reach), rr = Math.min(b.left + b.w, x0 + reach); if (rr > l) cx.drawImage(sp, l, y0 - ww / 2, rr - l, ww); }
      else { const tp = Math.max(b.top, y0 - reach), bt = Math.min(b.top + b.h, y0 + reach); if (bt > tp) cx.drawImage(sp, x0 - ww / 2, tp, ww, bt - tp); }
    }
  });
  orb(x0, y0, cw * .2, cw * 1.2, ['#ffffff', 'rgba(255,170,210,.95)', 'rgba(255,120,180,.4)'], d, 300, .2);
  for (let i = 0; i < N; i++) {
    const kk = horiz ? r * N + i : i * N + c, dist = horiz ? Math.abs(i - c) : Math.abs(i - r);
    if (!mask[kk / N | 0][kk % N]) continue;
    const [sx, sy] = cellXY(kk); sparks(sx, sy, 4, '#FFC2DD', cw * .13, d + 40 + dist * 30);
  }
}
streak = function (r, c, dir, d) { catBeam(r, c, dir, d); };
lineSparks = function () {};

/* ---------- Katzenminze: a ball of mint light swells, then bursts in a shockwave of leaves and stars ---------- */
nipFx = function (cell, k, d) {
  const R = cell.radius || 1, [x, y, cw] = cellXY(k);
  later(d, thud); later(d + 60, bigShake);
  if (REDUCED) return;
  orb(x, y, cw * .25, cw * (R + 1.3), ['#ffffff', 'rgba(215,255,190,1)', 'rgba(100,225,60,.7)'], d, 340, .5);
  orb(x, y, cw * .1, cw * (R + .6), ['#ffffff', 'rgba(255,255,255,.9)', 'rgba(200,255,170,.5)'], d + 110, 180, .2);
  shock(x, y, cw * R * .5, cw * (R + 1.8), '#8FE870', d + 130, 480, cw * .22, 'rgba(150,255,120,1)');
  shock(x, y, cw * .3, cw * (R + 1.15), '#ffffff', d + 190, 400, cw * .1);
  later(d + 120, () => {
    burst(x, y, 14 + 6 * R, 1.6 + .35 * R, ['#5ED83C', '#8FE870', '#B8F0A8', '#2FA84A'], 'leaf');
    sparks(x, y, 12 + 5 * R, '#C8FFB0', cw * .22);
  });
  for (let i = 0; i < Q(6 + 3 * R); i++) twinkle(x + (Math.random() - .5) * cw * (2 * R + 1.4), y + (Math.random() - .5) * cw * (2 * R + 1.4), cw * (.14 + Math.random() * .12), d + 160 + Math.random() * 320);
};

/* ---------- the little pictures are made ahead, a few at a time while nothing happens, so no effect stutters the first time ---------- */
(function prewarm() {
  const jobs = [twinkleSpr, bubbleSpr, haloSpr, haloWSpr, laserDotSpr];
  const glow = c => jobs.push(() => glowSpr(c[0], c[1], c[2]));
  for (const col of ['#FF8FC0', '#7CE84F', '#FF2E63', '#FFD23F', '#ffffff', ...RAINBOW]) glow(['#ffffff', withA(col, .9), withA(col, .35)]);
  [['#ffffff', 'rgba(255,96,140,.95)', 'rgba(255,46,99,.45)'], ['#ffffff', 'rgba(255,140,170,.95)', 'rgba(255,46,99,.45)'], ['#ffffff', 'rgba(255,238,170,.95)', 'rgba(255,120,200,.5)'],
   ['#ffffff', 'rgba(255,170,210,.95)', 'rgba(255,120,180,.4)'], ['#ffffff', 'rgba(215,255,190,1)', 'rgba(100,225,60,.7)'], ['#ffffff', 'rgba(255,255,255,.9)', 'rgba(200,255,170,.5)'],
   ['#ffffff', 'rgba(255,236,170,.9)', 'rgba(255,120,200,.45)']].forEach(glow);
  for (const pal of [...SHARDS, ...Object.values(XSHARDS), ['#FFD23F', '#FFF1A8', '#E09A00']]) for (const c of pal) jobs.push(() => shapeSpr('shard', c));
  for (const c of [...PCOL, '#A9744F']) for (const sh of ['heart', 'star', 'kibble', 'dot']) jobs.push(() => shapeSpr(sh, c));
  for (const c of ['#5ED83C', '#8FE870', '#B8F0A8', '#2FA84A']) jobs.push(() => shapeSpr('leaf', c));
  for (const c of ['#FFD23F', '#FF9AB3', '#FF7096', '#FFC2DD', '#C8FFB0', ...RAINBOW]) jobs.push(() => sparkSpr(c));
  for (const c of ['#FF8FC0', '#FFB3D1', '#ffffff']) for (const v of [false, true]) jobs.push(() => stripSpr(c, v));
  const run = () => { const t0 = performance.now(); while (jobs.length && performance.now() - t0 < 6) { try { jobs.shift()(); } catch (e) {} } if (jobs.length) setTimeout(run, 60); };
  setTimeout(run, 1500);
})();
