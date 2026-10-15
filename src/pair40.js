
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
// a coloured extra is the treat itself, changed (like the striped and wrapped candies in Candy Crush):
// Flitzekatze: candy stripes run right through the treat, along its line; Katzenminze: the treat is wrapped in a mint bonbon wrapper;
// Laserpunkt: the treat sits in a glass bubble with a laser-red rim and target marks. Drawn once per kind and colour.
const X40 = new Map();
function inner40(col) { const m = String(ICONS[col]).match(/<svg[^>]*>([\s\S]*)<\/svg>/); return m ? m[1] : ''; }
function extraSvg40(x) {
  const key = x.type + x.col + (x.dir || ''); if (X40.has(key)) return X40.get(key);
  const T = inner40(x.col), c = x.col;
  let out;
  if (x.type === 'cat') {
    const v = x.dir === 'v', bars = [21, 44.5, 68].map(p => v ? `<rect x="${p - 5.5}" y="-5" width="11" height="110" rx="5.5"/>` : `<rect x="-5" y="${p - 5.5}" width="110" height="11" rx="5.5"/>`).join('');
    out = `<svg viewBox="0 0 100 100"><defs><mask id="m40s${c}" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120"><g class="mk40">${T}</g></mask>` +
      `<linearGradient id="g40s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#FFE3F0"/></linearGradient></defs>` +
      `${T}<g mask="url(#m40s${c})"><g fill="url(#g40s)" opacity=".8">${bars}</g><g fill="none" stroke="#FF4F9A" stroke-width="1.6" opacity=".55">${bars}</g></g></svg>`;
  } else if (x.type === 'nip') {
    const end = s => `<g transform="translate(50 50) scale(${s * .93} .93)"><path d="M-31 -9 Q-38 -10 -47 -24 Q-43 -12 -49 -6 Q-44 0 -49 6 Q-43 12 -47 24 Q-38 10 -31 9Z" fill="url(#g40w)" stroke="#239A3C" stroke-width="2.4" stroke-linejoin="round"/>` +
      `<path d="M-35 -6 L-45 -15 M-36 0 L-46 0 M-35 6 L-45 15" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity=".8"/></g>`;
    out = `<svg viewBox="0 0 100 100"><defs><linearGradient id="g40w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9FFDE"/><stop offset=".55" stop-color="#8FE870"/><stop offset="1" stop-color="#3DBB4F"/></linearGradient>` +
      `<linearGradient id="g40c" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".35" stop-color="#fff" stop-opacity=".08"/><stop offset=".7" stop-color="#B8F0A8" stop-opacity=".12"/><stop offset="1" stop-color="#5ED83C" stop-opacity=".35"/></linearGradient></defs>` +
      `${end(1)}${end(-1)}<g transform="translate(50 50) scale(.76) translate(-50 -50)">${T}</g>` +
      `<rect x="17" y="15" width="66" height="70" rx="24" fill="url(#g40c)" stroke="#2FA84A" stroke-width="3"/><rect x="17" y="15" width="66" height="70" rx="24" fill="none" stroke="#DFFFD0" stroke-width="1.2" opacity=".9"/>` +
      `<path d="M27 26 Q34 19 46 19" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" opacity=".85"/></svg>`;
  } else {
    out = `<svg viewBox="0 0 100 100"><defs><radialGradient id="g40b" cx=".42" cy=".38" r=".62"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".72" stop-color="#FFD0DC" stop-opacity=".18"/><stop offset=".93" stop-color="#FF2E63" stop-opacity=".55"/><stop offset="1" stop-color="#C4003A" stop-opacity=".8"/></radialGradient></defs>` +
      `<g transform="translate(50 50) scale(.74) translate(-50 -50)">${T}</g>` +
      `<circle cx="50" cy="50" r="42" fill="url(#g40b)" stroke="#E8194F" stroke-width="3.2"/>` +
      `<g stroke="#fff" stroke-width="4" stroke-linecap="round"><path d="M50 4 V14 M50 86 V96 M4 50 H14 M86 50 H96"/></g><g stroke="#FF2E63" stroke-width="2.2" stroke-linecap="round"><path d="M50 4 V14 M50 86 V96 M4 50 H14 M86 50 H96"/></g>` +
      `<path d="M22 32 Q30 16 50 13" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".8"/><circle cx="71" cy="72" r="3.4" fill="#fff" opacity=".85"/></svg>`;
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
