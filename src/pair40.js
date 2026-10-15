
/* ===================== V40 test: extras like in Candy Crush ===================== */
// An extra keeps the colour of the treats it was made from and counts as that treat in a match. It only goes off when it
// is eaten in a match (or caught by another extra). Swapping it with a treat only works if that makes a match.
// The bowl still goes with anything, and two extras swapped together are still a combo. PAIR40 switches the rule.
var PAIR40;
try { PAIR40 = localStorage.getItem('wm-pair40') !== 'off'; } catch (e) { PAIR40 = true; }
function isColx(x) { return !!x && x.col != null && (x.type === 'cat' || x.type === 'nip' || x.type === 'laser'); }
// the kind a tile counts as in a match
function colOf(x) { return !x ? null : PAIR40 && isColx(x) ? x.col : x.type; }
// does swapping these two always do something, match or not?
function powerMove(a, b) {
  if (!PAIR40 || tut) return isPower(a.type) || isPower(b.type);
  const free = x => isPower(x.type) && !isColx(x);
  return (isPower(a.type) && isPower(b.type)) || free(a) || free(b);
}
// a coloured extra shows its treat:
// Flitzekatze: the treat sprints off both ways at once (faded copies and speed lines along its row or column);
// Katzenminze: the treat sits in the mint bouquet, bow in front; Laserpunkt: the treat in the laser's glow and star
const X40 = new Map();
function inner40(col) { const m = String(ICONS[col]).match(/<svg[^>]*>([\s\S]*)<\/svg>/); return m ? m[1] : ''; }
const at40 = (T, x, y, s, o = 1) => `<g${o < 1 ? ` opacity="${o}"` : ''} transform="translate(${x} ${y}) scale(${s}) translate(-50 -50)">${T}</g>`;
const SPEED40 = `<g stroke-linecap="round"><g stroke="#FF4F9A" stroke-width="7" opacity=".55"><path d="M5 34 H24"/><path d="M3 50 H20"/><path d="M5 66 H24"/><path d="M95 34 H76"/><path d="M97 50 H80"/><path d="M95 66 H76"/></g>` +
  `<g stroke="#fff" stroke-width="3"><path d="M5 34 H24"/><path d="M3 50 H20"/><path d="M5 66 H24"/><path d="M95 34 H76"/><path d="M97 50 H80"/><path d="M95 66 H76"/></g></g>`;
function extraSvg40(x) {
  const key = x.type + x.col + (x.dir || ''); if (X40.has(key)) return X40.get(key);
  const T = inner40(x.col);
  let out;
  if (x.type === 'cat') {
    const v = x.dir === 'v';
    out = `<svg class="sprint40" viewBox="0 0 100 100">${v ? `<g transform="rotate(90 50 50)">${SPEED40}</g>` : SPEED40}` +
      (v ? at40(T, 50, 29, .54, .3) + at40(T, 50, 71, .54, .3) : at40(T, 29, 50, .54, .3) + at40(T, 71, 50, .54, .3)) + at40(T, 50, 50, .74) + '</svg>';
  } else if (x.type === 'nip') {
    out = `<svg viewBox="0 0 100 100"><path d="M50 84 V24" stroke="#11621F" stroke-width="8" stroke-linecap="round"/><path d="M50 84 V24" stroke="#6EDB4C" stroke-width="3.5" stroke-linecap="round"/>` +
      leaf(50, 68, -74, 1.02) + leaf(50, 68, 74, 1.02) + leaf(50, 46, -46, .95) + leaf(50, 46, 46, .95) + leaf(50, 28, 0, .78) +
      at40(T, 50, 53, .7) +
      `<g fill="url(#gPink)" ${OL('#9E0C57')}><path d="M47.5 81 L40 96 L46 93.5 L49 97.5Z"/><path d="M52.5 81 L60 96 L54 93.5 L51 97.5Z"/>` +
      `<path d="M50 79 Q34 68 30 77 Q30 88 50 81Z"/><path d="M50 79 Q66 68 70 77 Q70 88 50 81Z"/><circle cx="50" cy="80" r="5.5"/></g>` + SPARK(16, 18, .8) + SPARK(85, 14, .62) + '</svg>';
  } else {
    out = `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" fill="url(#gGlow)"/>` +
      `<path d="M50 2 Q54 46 98 50 Q54 54 50 98 Q46 54 2 50 Q46 46 50 2Z" fill="#FFC9D6" opacity=".9"/>` + at40(T, 50, 50, .74) + '</svg>';
  }
  if (X40.size < 200) X40.set(key, out);
  return out;
}
const iconFor40 = iconFor;
iconFor = function (x) { return PAIR40 && isColx(x) ? extraSvg40(x) : iconFor40(x); };
// the tips say how it works now
const PAIR_TIP = {
  cat: () => 'Flitzekatze! Sie hat die Farbe ihrer Leckerlis. Bring sie in ein Match, dann flitzt sie los.',
  nip: () => 'Katzenminze! Mach ein Match mit ihr, dann fliegt alles rundherum weg.',
  laser: () => 'Laserpunkt! Mach ein Match mit ihm, dann jag ich 3 Leckerlis.'
};
for (const k of ['cat', 'nip', 'laser']) { const t0 = EXTRA[k].tip; EXTRA[k].tip = function () { return PAIR40 ? PAIR_TIP[k]() : t0.apply(this, arguments); }; }
// a swap that does nothing now: say once why
let toldPair40 = false;
const trySwap40 = trySwap;
trySwap = async function (r1, c1, r2, c2, free) {
  let warn = false;
  if (PAIR40 && !busy && !tut && !free && inB(r1, c1) && inB(r2, c2)) {
    const a = grid[r1][c1], b = grid[r2][c2];
    if (a && b && canSwap(a) && canSwap(b) && a.type !== 'bell' && b.type !== 'bell' && !powerMove(a, b) && (isColx(a) || isColx(b))) {
      sw(r1, c1, r2, c2); warn = !findMatches().cells.size; sw(r1, c1, r2, c2);
    }
  }
  const res = await trySwap40.apply(this, arguments);
  if (warn && !toldPair40) { toldPair40 = true; say('Extras gehen jetzt nur in einem Match los. Zwei Extras miteinander gehen immer!'); }
  return res;
};
