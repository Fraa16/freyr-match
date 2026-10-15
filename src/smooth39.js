
/* ===================== V39: smooth even in the biggest combos ===================== */
// Measured with a slowed-down CPU: the bowl combos froze the screen in short bursts. What helped:
// treat pictures parsed once and copied after that; the board's place measured at most every 300 ms instead of every frame;
// the little dashing cats moved on the GPU (they used to move with left/top, a layout every frame);
// and when many extras go off at once, only the first few draw the big light beams and rays.
var TPL39;
function iconNode(html) {
  if (!TPL39) TPL39 = new Map();
  let t = TPL39.get(html);
  if (!t) { t = document.createElement('template'); t.innerHTML = html; if (TPL39.size < 400) TPL39.set(html, t); }
  return t.content.cloneNode(true);
}
let BG39 = null, BG39t = 0, MG39 = null, MG39t = 0;
boardGeo = function () {
  const now = performance.now();
  if (!BG39 || now - BG39t > 300) { const br = boardEl.getBoundingClientRect(); BG39 = { left: br.left, top: br.top, w: br.width, h: br.height, cw: br.width / N }; BG39t = now; }
  return BG39;
};
mascotGeo = function () {
  const now = performance.now();
  if (!MG39 || now - MG39t > 300) { const r = mascot.getBoundingClientRect(); MG39 = { left: r.left, top: r.top, width: r.width, height: r.height }; MG39t = now; }
  return MG39;
};
for (const ev of ['resize', 'scroll', 'orientationchange']) addEventListener(ev, () => { BG39 = MG39 = null; }, { passive: true });
// Flitzekatze: the two little cats dash along the line with a transform (no layout while they run)
let dash39 = [];
dashers = function (r, c, dir, d) {
  if (REDUCED) return;
  const now = performance.now() + d; dash39 = dash39.filter(t => t > now - 450);
  if (dash39.length >= 10) return;
  const k0 = r * N + c, ends = dir === 'h' ? [r * N, r * N + N - 1] : [c, (N - 1) * N + c];
  for (const e of ends) {
    if (e === k0) continue;
    dash39.push(now);
    const a = pctPos(k0), b = pctPos(e), cells = dir === 'h' ? Math.abs(e % N - c) : Math.abs((e / N | 0) - r);
    const ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI, tx = ((b.x - a.x) / STEP * 100).toFixed(1), ty = ((b.y - a.y) / STEP * 100).toFixed(1), rot = `rotate(${ang.toFixed(1)}deg)`;
    later(d, () => {
      const el = document.createElement('div'); el.className = 'xdash';
      el.innerHTML = `<div class="xt"></div><div class="xh" style="transform:rotate(${(-ang).toFixed(1)}deg)"></div>`;
      el.lastChild.appendChild(iconNode(CAT_ICON()));
      Object.assign(el.style, { left: a.x + '%', top: a.y + '%', width: STEP + '%', height: STEP + '%', transform: rot });
      boardEl.appendChild(el);
      el.animate([{ transform: `translate(0,0) ${rot}` }, { transform: `translate(${tx}%,${ty}%) ${rot}` }], { duration: 70 + cells * 30, easing: 'linear', fill: 'forwards' }).onfinish = () => {
        const [x, y] = cellXY(e); burst(x, y, 10, 1.3, ['#FF8FC0', '#FFD1E1', '#ffffff'], 'star');
        el.animate([{ opacity: 1, transform: `translate(${tx}%,${ty}%) ${rot}` }, { opacity: 0, transform: `translate(${tx}%,${ty}%) ${rot} scale(.6)` }], { duration: 180, fill: 'forwards' }).onfinish = () => el.remove();
      };
      setTimeout(() => el.remove(), 70 + cells * 30 + 600);
    });
  }
};
// many cats at once (a bowl with a cat): the first five draw their beam of light, the rest only dash and sparkle
let beam39 = [];
const catBeam39 = catBeam;
catBeam = function (r, c, dir, d) {
  const now = performance.now() + d; beam39 = beam39.filter(t => t > now - 500);
  if (beam39.length >= 5) return;
  beam39.push(now);
  return catBeam39.apply(this, arguments);
};
// the Schnurr-Power line is fitted at most once a frame, and only when its text could need a different size
// (it used to be measured on every change of the number, a full layout each time, several times per bowl combo)
const fitPurr39 = fitPurrTxt;
let fp39k = '', fp39raf = 0;
fitPurrTxt = function () {
  if (fp39raf) return;
  fp39raf = requestAnimationFrame(() => {
    fp39raf = 0;
    const t = $('purrTxt'), bw = $('barwrap'), k = (t ? t.textContent.replace(/[0-9]/g, '0') : '') + '|' + (bw ? bw.className : '') + '|' + innerWidth + '|' + (document.documentElement.className || '');
    if (k === fp39k) return;
    fp39k = k; fitPurr39();
  });
};
// rings of light are drawn on the effects canvas (the old ones were page elements with a masked rainbow gradient,
// which a phone has to paint again in every frame while they grow)
ring = function (k, R, d, cls = 'ring') {
  if (REDUCED) return;
  const [x, y, cw] = cellXY(k), r1 = cw * (R + .6);
  if (/rainbow/.test(cls)) { shock(x, y, cw * .3, r1, '#FFB3C9', d, 600, cw * .28); shock(x, y, cw * .25, r1 * .86, '#FFE08A', d + 40, 560, cw * .2); shock(x, y, cw * .2, r1 * .72, '#A8D8FF', d + 80, 520, cw * .16); }
  else if (/white/.test(cls)) shock(x, y, cw * .3, r1, '#ffffff', d, 560, cw * .22);
  else shock(x, y, cw * .3, r1, '#8ED77F', d, 600, cw * .3, 'rgba(142,215,127,1)');
};
// the flare of an extra going off: at most six at once (a bowl with a cat sets off a dozen in one go)
let xf39 = [];
const xflash39 = xflash;
xflash = function (cell, k, d) {
  const now = performance.now() + d; xf39 = xf39.filter(t => t > now - 400);
  if (xf39.length >= 6) return;
  xf39.push(now); return xflash39.apply(this, arguments);
};
// treats flying up to Freyr: fewer when the whole board goes at once
const flyToCat39 = flyToCat;
let fly39 = [];
flyToCat = function (items) {
  const now = performance.now(); fly39 = fly39.filter(t => t > now - 600);
  if (fly39.length >= 8) { if (items.length) setTimeout(catEat, 300); return; }
  fly39.push(now); return flyToCat39.apply(this, arguments);
};
// the board shakes at most once in 400 ms: a bowl with catnip used to start the shake a dozen times in a row,
// and every new start can make the phone paint the whole board again
let shake39 = 0;
const bigShake39 = bigShake, shakePlain39 = shake;
bigShake = function () { const now = performance.now(); if (now - shake39 < 400) return; shake39 = now; return bigShake39.apply(this, arguments); };
shake = function () { const now = performance.now(); if (now - shake39 < 400) return; shake39 = now; return shakePlain39.apply(this, arguments); };
// When a big combo empties the board, the new treats no longer appear all in one frame: they come in column by column,
// 14 ms apart (the phone has to set up and paint every new tile, fifty at once took it up to 200 ms)
let dropBatch39 = null;
const dropIn39 = dropIn;
dropIn = function () { if (dropBatch39) { dropBatch39.push([...arguments]); return; } return dropIn39.apply(this, arguments); };
const gravity39 = gravity;
gravity = function () {
  dropBatch39 = [];
  try { return gravity39.apply(this, arguments); } finally {
    const b = dropBatch39; dropBatch39 = null;
    if (b.length < 16 || REDUCED) b.forEach(a => dropIn39.apply(null, a));
    else {
      for (const a of b) if (a[0]) a[0].style.visibility = 'hidden';
      [...new Set(b.map(a => a[1]))].sort((x, y) => x - y).forEach((col, i) => setTimeout(() => {
        for (const a of b) if (a[1] === col) { if (a[0]) a[0].style.visibility = ''; dropIn39.apply(null, a); }
      }, i * 14));
    }
  }
};
// many catnips or lasers at once: the first four (lasers: five) get the full show, the others a lighter one
let nip39 = [];
const nipFx39 = nipFx;
nipFx = function (cell, k, d) {
  const now = performance.now() + d; nip39 = nip39.filter(t => t > now - 400);
  if (nip39.length >= 4) {
    if (REDUCED) return;
    const [x, y] = cellXY(k); later(d + 120, () => burst(x, y, 6, 1.3, ['#5ED83C', '#8FE870', '#B8F0A8', '#2FA84A'], 'leaf'));
    return;
  }
  nip39.push(now); return nipFx39.apply(this, arguments);
};
let las39 = [];
const laserRun39 = laserRun;
laserRun = function (from, targets, d) {
  const now = performance.now() + (d || 0); las39 = las39.filter(t => t > now - 600);
  if (las39.length >= 5) return;
  las39.push(now); return laserRun39.apply(this, arguments);
};
// The extras become finished pictures too, like the treats already were. On the iPhone the catnip was the worst:
// a dozen catnip drawings (leaves, bow, glow, shadow filter) all popping at once took 150 to 230 ms to paint.
const XBM = new Map(), xbmWant = new Map();
let xbmSize = 0, xbmBusy = false;
function xbmSvg(x) {
  if (typeof PAIR40 !== 'undefined' && PAIR40 && typeof isColx === 'function' && isColx(x) && typeof extraSvg40 === 'function') return ['x' + x.type + x.col + (x.dir || ''), extraSvg40(x)];
  if (x.type === 'nip') return ['nip', NIP_SVG];
  if (x.type === 'laser') return ['laser', LASER_SVG];
  if (x.type === 'bowl') return ['bowl', BOWL_SVG];
  return null;
}
async function xbmRun() {
  if (xbmBusy) return; xbmBusy = true;
  try {
    const T = bmTileSize(), s = Math.min(3, Math.max(1, devicePixelRatio || 1)), size = Math.round(T * 1.28 * s);
    if (!T) return;
    if (Math.abs(size - xbmSize) >= 3) { XBM.clear(); xbmSize = size; }
    for (const [key, svg] of [...xbmWant]) {
      if (XBM.has(key)) { xbmWant.delete(key); continue; }
      try {
        const u = await bmPaint(svg, T, s, false), im = new Image(); im.src = u; try { await im.decode(); } catch (e) {}
        BM.keep.push(im); XBM.set(key, u);
      } catch (e) {}
      xbmWant.delete(key);
      await new Promise(r => setTimeout(r, 30));
    }
  } finally { xbmBusy = false; }
}
// the picture of an extra, or null while it is still being painted (then the drawing is used)
function xbmFor(x) {
  const ks = x && BM.url ? xbmSvg(x) : null;
  if (!ks) return null;
  const u = XBM.get(ks[0]);
  if (u) return '<img class="bm' + (x.type === 'cat' ? ' sprint40' : '') + '" src="' + u + '" alt="" draggable="false">';
  if (!xbmWant.has(ks[0])) { xbmWant.set(ks[0], ks[1]); setTimeout(xbmRun, 50); }
  return null;
}
const iconForX39 = iconFor;
iconFor = function (x) { return xbmFor(x) || iconForX39(x); };
const buildBitmaps39 = buildBitmaps;
buildBitmaps = async function () {
  const r = await buildBitmaps39.apply(this, arguments);
  for (const [k, v] of [['nip', NIP_SVG], ['laser', LASER_SVG], ['bowl', BOWL_SVG]]) if (!XBM.has(k)) xbmWant.set(k, v);
  xbmRun();
  return r;
};
