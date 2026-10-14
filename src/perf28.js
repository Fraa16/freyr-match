
/* ===================== V28: smooth play — tiles glide on the GPU, nothing measures the page in the middle of a move ===================== */

/* ---------- the board's place on screen, measured once and reused for a moment ----------
   Every effect used to ask the browser where the board is. After a change to the page that forces a full layout,
   and a bowl asked 64 times in a row. Now one measurement serves the next two frames. */
let BG = null;
function boardGeo() {
  if (!BG) {
    const br = boardEl.getBoundingClientRect();
    BG = { left: br.left, top: br.top, w: br.width, h: br.height, cw: br.width / N };
    requestAnimationFrame(() => requestAnimationFrame(() => { BG = null; }));
  }
  return BG;
}
let MG = null;
function mascotGeo() {
  if (!MG) {
    const r = mascot.getBoundingClientRect(); MG = { left: r.left, top: r.top, width: r.width, height: r.height };
    requestAnimationFrame(() => requestAnimationFrame(() => { MG = null; }));
  }
  return MG;
}
addEventListener('resize', () => { BG = null; MG = null; });
cellXY = function (k) { const g = boardGeo(); return [g.left + (k % N + .5) * g.cw, g.top + ((k / N | 0) + .5) * g.cw, g.cw]; };

/* ---------- restarting a little animation without stopping the page to measure it ----------
   Drop the class, let one frame pass, add it again. */
function replay(el, cls) {
  if (!el) return;
  if (!el.classList.contains(cls)) { el.classList.add(cls); return; }
  el.classList.remove(cls);
  const tok = el.__rp = (el.__rp || 0) + 1;
  requestAnimationFrame(() => requestAnimationFrame(() => { if (el.__rp === tok) el.classList.add(cls); }));
}

/* ---------- tiles move with transforms: the browser hands the gliding to the graphics chip ----------
   (top/left made it lay out and repaint the whole board in every frame of every fall) */
const TX = !!(window.CSS && CSS.supports && CSS.supports('translate', '1px 1px'));
if (TX) document.documentElement.classList.add('tx');
const placePlain28 = place;
place = function (cell, r, c) {
  if (!TX) return placePlain28(cell, r, c);
  const d = els.get(cell.id); if (!d) return;
  d.style.translate = (c * 100) + '% ' + (r * 100) + '%';
  d.dataset.r = r; d.dataset.c = c;
};
// a new treat falls in from above the board (or fades in where it appears)
function dropIn(d, c, from, r) {
  if (!TX) {
    d.style.transition = 'none'; d.style.left = (c * STEP) + '%'; d.style.top = (from * STEP) + '%';
    void d.offsetWidth; d.style.transition = ''; d.style.left = (c * STEP) + '%'; d.style.top = (r * STEP) + '%';
    return;
  }
  if (from === r) return;
  try {
    d.animate([{ translate: (c * 100) + '% ' + (from * 100) + '%' }, { translate: (c * 100) + '% ' + (r * 100) + '%' }],
      { duration: REDUCED ? 50 : 260, easing: 'cubic-bezier(.35,0,.4,1.2)' });
  } catch (e) {}
}
// the robot rolls the same way
const drawBossPlain28 = drawBoss;
let bossAt = '', bossStill = 0;
drawBoss = function () {
  drawBossPlain28();
  if (!boss || !boss.el) return;
  if (TX) boss.el.style.translate = (boss.c * 50) + '% ' + (boss.r * 50) + '%';
  // the brushes turn while it drives
  const at = boss.r + ',' + boss.c;
  if (at !== bossAt) { const first = !bossAt; bossAt = at; if (!first) { boss.el.classList.add('moving'); clearTimeout(bossStill); const el = boss.el; bossStill = setTimeout(() => el.classList.remove('moving'), 900); } }
};
const renderBossPlain28 = renderBoss;
renderBoss = function () {
  bossAt = '';
  renderBossPlain28();
  if (boss && boss.el && !boss.el.querySelector('.vled2')) boss.el.insertAdjacentHTML('beforeend', '<i class="vled2"></i>');
  if (boss && boss.el) drawBoss();
};

/* ---------- treats as finished pictures ----------
   Each treat used to be a vector drawing with a soft shadow filter, drawn again for every new tile (a full board
   after two bowls). Now each kind is painted once per tile size, shadow included, and a tile just shows that picture. */
const BM = { url: null, size: 0, busy: false, keep: [] };
function bmTileSize() { const g = boardGeo(); return g && g.cw > 12 ? g.cw : 0; }
function bmSvg(str) {
  const defs = document.querySelector('.gdefs defs');
  return str.replace(/^<svg\b/, '<svg xmlns="http://www.w3.org/2000/svg"').replace(/^(<svg[^>]*>)/, '$1' + (defs ? defs.outerHTML : ''));
}
async function bmPaint(str, T, s, gold) {
  const img = new Image();
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(bmSvg(str));
  await img.decode();
  const B = Math.round(T * 1.28 * s), off = T * .14 * s, w = T * s;
  const cvs = () => { const v = document.createElement('canvas'); v.width = v.height = B; return v; };
  // first the drawing alone, without any shadow: Safari would give every shape inside the drawing a shadow of its own
  // (grey smudges under the eyes, the pads, the cream), so the shadow is added afterwards to the finished picture
  const raw = cvs(); raw.getContext('2d').drawImage(img, off, off, w, w);
  let src = raw;
  if (gold) {
    const g = cvs(), gc = g.getContext('2d');
    gc.shadowColor = '#FFD54A'; gc.shadowBlur = 4 * s; gc.drawImage(raw, 0, 0); gc.drawImage(raw, 0, 0);
    src = g;
  }
  const cv = cvs(), c = cv.getContext('2d');
  c.shadowColor = 'rgba(20,8,50,.5)'; c.shadowOffsetY = 3 * s; c.shadowBlur = 1.6 * s;
  c.drawImage(src, 0, 0);
  const blob = await new Promise(res => cv.toBlob(res, 'image/png'));
  if (!blob) throw new Error('no blob');
  return URL.createObjectURL(blob);
}
async function buildBitmaps() {
  const T = bmTileSize(); if (!T || BM.busy) return;
  const s = Math.min(3, Math.max(1, devicePixelRatio || 1)), size = Math.round(T * 1.28 * s);
  if (BM.url && Math.abs(size - BM.size) < 3) return;
  BM.busy = true;
  try {
    const out = {}, keep = [];
    for (let t = 0; t < ICONS.length; t++) for (const gold of [0, 1]) {
      const u = await bmPaint(ICONS[t], T, s, gold); out[t + (gold ? 'g' : '')] = u;
      const im = new Image(); im.src = u; await im.decode(); keep.push(im);   // the picture must load here (else: no pictures at all) and stays decoded
    }
    BM.url = out; BM.size = size; BM.keep = keep;
    // tiles already on the board switch to the pictures too
    for (const row of grid) for (const x of row) if (x && isNormal(x.type)) { const el = els.get(x.id); if (el && !el.classList.contains('pop')) el.innerHTML = iconFor(x); }
  } catch (e) { /* this browser cannot turn the drawings into pictures: the tiles stay drawings */ }
  BM.busy = false;
}
const iconForPlain28 = iconFor;
iconFor = x => {
  if (BM.url && isNormal(x.type)) {
    const u = BM.url[x.type + (x.gold ? 'g' : '')];
    if (u) return '<img class="bm" src="' + u + '" alt="" draggable="false">' + (x.clock != null ? clockHTML(x.clock) : '');
  }
  return iconForPlain28(x);
};
let bmT = 0;
addEventListener('resize', () => { clearTimeout(bmT); bmT = setTimeout(() => { BG = null; if (!onMap) buildBitmaps(); }, 350); });
const startLevelPlain28 = startLevel;
startLevel = function () { const r = startLevelPlain28.apply(this, arguments); BG = null; requestAnimationFrame(() => buildBitmaps()); return r; };

/* ---------- the goals: only the numbers change during a level, so only the numbers are rewritten ---------- */
const drawGoalsPlain28 = drawGoals;
let goalSig = '';
drawGoals = function () {
  const box = $('goals');
  const sig = goals.map(g => g.kind + ':' + g.type + ':' + (g.what || '') + ':' + (g.n || '')).join('|');
  if (box && sig === goalSig && box.children.length === goals.length) {
    goals.forEach((g, i) => {
      const n = remaining(g), ch = box.children[i], b = ch && ch.querySelector('b'); if (!b) return;
      const t = n <= 0 ? '✓' : String(n);
      if (b.textContent !== t) b.textContent = t;
      ch.classList.toggle('done', n <= 0);
    });
    return;
  }
  goalSig = sig; drawGoalsPlain28();
};
const startLevelGoals28 = startLevel;
startLevel = function () { goalSig = ''; return startLevelGoals28.apply(this, arguments); };

/* ---------- the meter is saved when it changes, not on every redraw ---------- */
let purrSaved = null;
const drawPurrPlain28 = drawPurr;
drawPurr = function () {
  const ls = window.localStorage, set = ls && ls.setItem;
  // drawPurr of V27 saves every time; skip the write when nothing changed
  if (purrSaved === purr && ls) { ls.setItem = () => {}; try { drawPurrPlain28(); } finally { ls.setItem = set; } return; }
  drawPurrPlain28(); purrSaved = purr;
};

/* ---------- blinking and tail wagging, set off now and then ---------- */
(function idleLife() {
  if (REDUCED) return;
  const blink = () => {
    if (!document.hidden) document.querySelectorAll(onMap ? '.fsprite .eyes' : '.mascot .eyes').forEach(e => { e.classList.add('bl'); setTimeout(() => e.classList.remove('bl'), 320); });
    setTimeout(blink, 3200 + Math.random() * 3200);
  };
  const wag = () => {
    if (!document.hidden && onMap) document.querySelectorAll('.fsprite:not(.walk) .ftail').forEach(e => { e.classList.remove('wag'); requestAnimationFrame(() => requestAnimationFrame(() => e.classList.add('wag'))); setTimeout(() => e.classList.remove('wag'), 3500); });
    setTimeout(wag, 5000 + Math.random() * 4000);
  };
  setTimeout(blink, 2500); setTimeout(wag, 3000);
})();

/* ---------- small helpers for the hot path ---------- */
// writing the same text again still makes the browser lay the page out again
function setText(el, v) { if (!el) return; v = String(v); if (el.textContent !== v) el.textContent = v; }
// the zoomies runner: placed at its start, then moved with a transform (left/top animated the layout in every frame)
function runAnim(el, from, to, opts) {
  if (!TX) return el.animate([from, to], opts);
  const f = parseFloat, k = 100 / 22;   // the runner is 22 % of the board wide and high
  return el.animate([{ translate: '0% 0%' }, { translate: ((f(to.left) - f(from.left)) * k) + '% ' + ((f(to.top) - f(from.top)) * k) + '%' }], opts);
}
// the walk on the map: the map stands still while Freyr walks, so where a point of the map lands on screen is measured
// once (two points give scale and offset) instead of moving a marker and asking the browser for it in every frame
function walkPlacer(mark, walker, k) {
  mark.style.left = '0px'; mark.style.top = '0px'; const r0 = mark.getBoundingClientRect();
  mark.style.left = '100px'; mark.style.top = '100px'; const r1 = mark.getBoundingClientRect();
  const sb = $('mapScreen').getBoundingClientRect();
  const sx = (r1.left - r0.left) / 100, sy = (r1.top - r0.top) / 100, sc = r0.width / 40;
  const ox = r0.left + r0.width / 2 - sb.left, oy = r0.top + r0.height / 2 - sb.top;
  walker.style.willChange = 'transform';
  return (pt, lift) => {
    const X = ox + pt.x * k * sx, Y = oy + (pt.y * k - lift) * sy;
    walker.style.transform = `translate(${X.toFixed(1)}px,${Y.toFixed(1)}px) scale(${sc.toFixed(3)}) translate(-50%,-100%)`;
  };
}

/* ---------- the map: keep what is drawn, move what changes out of the drawing ---------- */
// the scenery with its glossy filters is costly to draw; when it is the same as last time it stays, and only the
// level buttons, banners and Freyr are built again
let mapSvgCache = '';
function setMapHTML(s, h) {
  const inner = $('mapInner'), svg = inner.querySelector(':scope > svg.mapsvg:not(.pzlayer)');
  if (svg && s === mapSvgCache) {
    for (const el of [...inner.children]) if (el !== svg) el.remove();
    inner.insertAdjacentHTML('beforeend', h);
  } else { inner.innerHTML = s + h; mapSvgCache = s; }
}
// the paw prints that appear while Freyr walks sit on their own layer, so fading them in does not redraw the scenery
function liftPaws() {
  const inner = $('mapInner'), svg = inner.querySelector(':scope > svg.mapsvg:not(.pzlayer)'); if (!svg) return;
  const pz = svg.querySelectorAll('.pz'); if (!pz.length) return;
  const NS = 'http://www.w3.org/2000/svg', ov = document.createElementNS(NS, 'svg'), g = document.createElementNS(NS, 'g');
  ov.setAttribute('viewBox', svg.getAttribute('viewBox')); ov.setAttribute('class', 'mapsvg pzlayer'); ov.setAttribute('aria-hidden', 'true');
  g.setAttribute('fill', '#FF5FA8'); g.setAttribute('opacity', '.85');
  pz.forEach(e => g.appendChild(e)); ov.appendChild(g); svg.after(ov);
  mapSvgCache = '';   // the drawing no longer matches its text
}
const walkToPlain28 = walkTo;
walkTo = function () { liftPaws(); return walkToPlain28.apply(this, arguments); };
