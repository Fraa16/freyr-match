
/* ===================== V33: nothing on top of anything at the top of the screen; the board without its white rim ===================== */
// the level number sits inside the score panel: at the end of the purr row, or (before the purr meter is there) as a small fourth box
const LVBOX = $('level') && $('level').parentElement;
function placeLevel() {
  if (!LVBOX) return;
  const row = $('purrRow'), inRow = row && !row.hidden, hrow = document.querySelector('main .hud-row');
  const to = inRow ? row : hrow;
  if (to && LVBOX.parentElement !== to) to.appendChild(LVBOX);
  LVBOX.classList.toggle('inrow', inRow); LVBOX.classList.toggle('inbox', !inRow);
  if (hrow) hrow.classList.toggle('has-lv', !inRow);
}
const drawPurrPlain33 = drawPurr;
drawPurr = function () { const r = drawPurrPlain33.apply(this, arguments); placeLevel(); return r; };
placeLevel();
// Freyr's bubble: as high as the room above the board allows, so it does not reach over the board when there is room
fitBubble = function () {
  const b = bubble; b.style.fontSize = '';
  if (!b.firstChild) return;
  const room = $('board').getBoundingClientRect().top - b.getBoundingClientRect().top - 14;
  const max = room >= 48 ? Math.min(104, room) : 72;
  let fs = parseFloat(getComputedStyle(b).fontSize); const min = Math.max(11, fs * .74);
  while (b.offsetHeight > max && fs > min) { fs -= .5; b.style.fontSize = fs + 'px'; }
};
// the board's tray: one shape for all cells (no white rim, no seams between the cells), round only where the board ends
function trayPath(cells) {
  const set = new Set(cells.map(([r, c]) => r * N + c)), has = (r, c) => r >= 0 && r < N && c >= 0 && c < N && set.has(r * N + c), R = 18;
  let d = '';
  for (const [r, c] of cells) {
    const n = has(r - 1, c), s = has(r + 1, c), w = has(r, c - 1), e = has(r, c + 1), x0 = c * 100, x1 = x0 + 100, y0 = r * 100, y1 = y0 + 100;
    const tl = !n && !w ? R : 0, tr = !n && !e ? R : 0, br = !s && !e ? R : 0, bl = !s && !w ? R : 0;
    d += `M${x0 + tl} ${y0}H${x1 - tr}` + (tr ? `A${R} ${R} 0 0 1 ${x1} ${y0 + R}` : '') + `V${y1 - br}` + (br ? `A${R} ${R} 0 0 1 ${x1 - R} ${y1}` : '') +
      `H${x0 + bl}` + (bl ? `A${R} ${R} 0 0 1 ${x0} ${y1 - R}` : '') + `V${y0 + tl}` + (tl ? `A${R} ${R} 0 0 1 ${x0 + R} ${y0}` : '') + 'Z';
  }
  return d;
}
// the board's edge alone (not the lines between cells): a thin soft line, so the eye finds where the board ends
function trayEdge(cells) {
  const set = new Set(cells.map(([r, c]) => r * N + c)), has = (r, c) => r >= 0 && r < N && c >= 0 && c < N && set.has(r * N + c), R = 18;
  let d = '';
  for (const [r, c] of cells) {
    const n = has(r - 1, c), s = has(r + 1, c), w = has(r, c - 1), e = has(r, c + 1), x0 = c * 100, x1 = x0 + 100, y0 = r * 100, y1 = y0 + 100;
    const tl = !n && !w ? R : 0, tr = !n && !e ? R : 0, br = !s && !e ? R : 0, bl = !s && !w ? R : 0;
    if (!n) d += `M${x0 + tl} ${y0}H${x1 - tr}`;
    if (tr) d += `M${x1 - R} ${y0}A${R} ${R} 0 0 1 ${x1} ${y0 + R}`;
    if (!e) d += `M${x1} ${y0 + tr}V${y1 - br}`;
    if (br) d += `M${x1} ${y1 - R}A${R} ${R} 0 0 1 ${x1 - R} ${y1}`;
    if (!s) d += `M${x1 - br} ${y1}H${x0 + bl}`;
    if (bl) d += `M${x0 + R} ${y1}A${R} ${R} 0 0 1 ${x0} ${y1 - R}`;
    if (!w) d += `M${x0} ${y1 - bl}V${y0 + tl}`;
    if (tl) d += `M${x0} ${y0 + R}A${R} ${R} 0 0 1 ${x0 + R} ${y0}`;
  }
  return d;
}
// the lines between the cells: softer still than the edge
function trayGrid(cells) {
  const set = new Set(cells.map(([r, c]) => r * N + c)), has = (r, c) => r >= 0 && r < N && c >= 0 && c < N && set.has(r * N + c);
  let d = '';
  for (const [r, c] of cells) {
    if (has(r, c + 1)) d += `M${c * 100 + 100} ${r * 100 + 6}V${r * 100 + 94}`;
    if (has(r + 1, c)) d += `M${c * 100 + 6} ${r * 100 + 100}H${c * 100 + 94}`;
  }
  return d;
}
function drawTray() {
  const wrap = $('boardwrap'); if (!wrap) return;
  wrap.querySelectorAll('.tray').forEach(e => e.remove());
  const kit = cfg && cfg.kit, body = [], blue = [];
  let k = '', kb = '';
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (mask[r][c]) {
    const sl = kit && r <= 2 && (c <= 1 || c >= 6);
    (sl ? blue : body).push([r, c]);
    if ((r + c) % 2) { const q = `<rect x="${c * 100 + 7}" y="${r * 100 + 7}" width="86" height="86" rx="16"/>`; if (sl) kb += q; else k += q; }
  }
  // the sleeves join the body: one outline for the whole shirt decides which corners are round
  const all = body.concat(blue), shape = list => trayPath(list).length ? trayPath(list) : '';
  const round = trayPath(all);
  wrap.insertAdjacentHTML('afterbegin', `<svg class="tray" viewBox="0 0 800 800" aria-hidden="true">` +
    (kit ? `<clipPath id="trayKit"><path d="${round}"/></clipPath><g clip-path="url(#trayKit)"><path d="${trayPath(body)}" fill="#8C1D40"/><path d="${trayPath(blue)}" fill="#4DA9E0"/></g><g fill="#A12B52">${k}</g><g fill="#6CC4F0">${kb}</g>`
      : `<path d="${round}" fill="var(--trayFill)"/><g fill="var(--trayAlt)">${k}</g>`) +
    `<path class="tgrid" d="${trayGrid(all)}" fill="none" stroke-width="3" stroke-linecap="round"/>` +
    `<path class="tedge" d="${trayEdge(all)}" fill="none" stroke-width="5" stroke-linecap="round"/></svg>`);
}
const renderBoardPlain33 = renderBoard;
renderBoard = function () { const r = renderBoardPlain33.apply(this, arguments); drawTray(); return r; };
