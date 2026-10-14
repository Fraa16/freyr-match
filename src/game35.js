/* ===================== V35: take your progress along (a code to copy and paste) ===================== */
// everything the game keeps lives in localStorage under "wm-…"; the test copies keep their own "wm-test…" markers out of it
const SAVE_TAG = 'WM1-';
const saveKeys = () => { const k = []; try { for (let i = 0; i < localStorage.length; i++) { const n = localStorage.key(i); if (n && n.startsWith('wm-') && !n.startsWith('wm-test')) k.push(n); } } catch (e) {} return k.sort(); };
const b64enc = str => { const b = new TextEncoder().encode(str); let s = ''; for (let i = 0; i < b.length; i += 0x8000) s += String.fromCharCode.apply(null, b.subarray(i, i + 0x8000)); return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); };
const b64dec = str => { const s = atob(str.replace(/-/g, '+').replace(/_/g, '/')); return new TextDecoder().decode(Uint8Array.from(s, c => c.charCodeAt(0))); };
function saveCode() {
  const o = {}; try { for (const k of saveKeys()) o[k] = localStorage.getItem(k); } catch (e) {}
  return SAVE_TAG + b64enc(JSON.stringify(o));
}
function readCode(txt) {
  const t = String(txt || '').replace(/\s+/g, '');
  const i = t.indexOf(SAVE_TAG); if (i < 0) return null;
  try {
    const o = JSON.parse(b64dec(t.slice(i + SAVE_TAG.length)));
    if (!o || typeof o !== 'object' || Array.isArray(o) || !('wm-level' in o)) return null;
    for (const [k, v] of Object.entries(o)) if (!k.startsWith('wm-') || typeof v !== 'string') return null;
    return o;
  } catch (e) { return null; }
}
function applyCode(o) {
  try {
    for (const k of saveKeys()) localStorage.removeItem(k);
    for (const [k, v] of Object.entries(o)) localStorage.setItem(k, v);
    return true;
  } catch (e) { return false; }
}

(() => {
  const ov = document.createElement('div');
  ov.className = 'overlay'; ov.id = 'saveOv';
  ov.innerHTML = `<div class="card sticker savecard" role="dialog" aria-modal="true" aria-labelledby="saveTitle">
    <h2 class="disp" id="saveTitle">Spielstand</h2>
    <p>Mit diesem Code nimmst du deinen Spielstand mit, zum Beispiel aufs neue Handy oder in die App auf dem Homescreen.</p>
    <div class="field">
      <span class="lbl" id="saveOutL">Dein Code</span>
      <textarea class="savecode" id="saveOut" rows="3" readonly aria-labelledby="saveOutL" spellcheck="false"></textarea>
      <button class="btn soft savebtn" id="saveCopy">Code kopieren</button>
    </div>
    <div class="field">
      <span class="lbl" id="saveInL">Code von woanders laden</span>
      <textarea class="savecode" id="saveIn" rows="3" aria-labelledby="saveInL" placeholder="Code hier einfügen" spellcheck="false" autocapitalize="off" autocomplete="off"></textarea>
      <p class="savemsg" id="saveMsg" role="status"></p>
      <button class="btn soft savebtn" id="saveLoad">Laden</button>
    </div>
    <button class="btn" id="saveDone">Fertig</button>
  </div>`;
  document.body.appendChild(ov);
  const link = document.createElement('button');
  link.className = 'savelink'; link.id = 'saveOpen'; link.type = 'button'; link.textContent = 'Spielstand sichern oder laden';
  $('setDone').before(link);

  let pending = null;
  const msg = (t, bad) => { const m = $('saveMsg'); m.textContent = t; m.classList.toggle('bad', !!bad); };
  const reset = () => { pending = null; $('saveLoad').textContent = 'Laden'; msg(''); };
  const open = () => {
    $('saveOut').value = saveCode(); $('saveIn').value = ''; reset();
    $('saveCopy').textContent = 'Code kopieren';
    ov.classList.add('show'); blip();
  };
  const close = () => { ov.classList.remove('show'); };
  link.onclick = open;
  $('saveDone').onclick = close;
  ov.addEventListener('click', e => { if (e.target === ov) close(); });
  $('saveOut').addEventListener('focus', e => e.target.select());
  $('saveCopy').onclick = async () => {
    const ta = $('saveOut'), code = ta.value; let ok = false;
    try { await navigator.clipboard.writeText(code); ok = true; } catch (e) {}
    if (!ok) { try { ta.focus(); ta.select(); ta.setSelectionRange(0, code.length); ok = document.execCommand('copy'); } catch (e) {} }
    $('saveCopy').textContent = ok ? 'Kopiert!' : 'Markiert, jetzt kopieren';
    if (ok) chime(7);
  };
  $('saveIn').addEventListener('input', reset);
  $('saveLoad').onclick = () => {
    const o = readCode($('saveIn').value);
    if (!o) { pending = null; msg('Der Code passt nicht. Hast du ihn ganz kopiert?', true); nope(); return; }
    if (!pending) {
      pending = o;
      const to = parseInt(o['wm-level'], 10) || 1, from = maxLevel || level;
      msg('Damit wird dein Stand hier (Level ' + from + ') durch Level ' + to + ' ersetzt. Nochmal tippen zum Bestätigen.');
      $('saveLoad').textContent = 'Ja, ersetzen';
      return;
    }
    if (!applyCode(pending)) { msg('Das hat nicht geklappt. Der Speicher ist gesperrt.', true); return; }
    msg('Geladen!'); fanfare();
    setTimeout(() => location.reload(), 600);
  };
})();

/* ===================== V35: tall screens use the extra height (bigger panel and tools, see game35.css) ===================== */
const ROOMY = ['roomy1', 'roomy2'], ROOM_MIN = 150;
const fitLayoutPlain35 = fitLayout;
fitLayout = function () {
  const html = document.documentElement, had = ROOMY.filter(c => html.classList.contains(c)).length;
  html.classList.remove(...ROOMY);
  let changed = fitLayoutPlain35.apply(this, arguments);
  let n = 0;
  const st = document.querySelector('main .stage');
  if (st && fitLv === 0 && !SIDE.matches) {
    for (; n < ROOMY.length; n++) {
      const r = st.getBoundingClientRect();
      if (!r.width || r.height - r.width < ROOM_MIN) break;
      html.classList.add(ROOMY[n]);
      const r2 = st.getBoundingClientRect();
      if (r2.height + 1 < r2.width) { html.classList.remove(ROOMY[n]); break; }
    }
  }
  if (n !== had) { BG = null; if (bubble.firstChild) fitBubble(); changed = true; }
  return changed;
};
fitLayout();

/* ===================== V35: the purr bar text always fits in one line ===================== */
function fitPurrTxt() {
  const t = $('purrTxt'), bw = $('barwrap'); if (!t || !bw || !bw.clientWidth) return;
  t.style.fontSize = '';
  // the text's own width (the box itself always spans the whole bar)
  const avail = bw.clientWidth - 10, rg = document.createRange(), w = () => { rg.selectNodeContents(t); return rg.getBoundingClientRect().width; };
  let fs = parseFloat(getComputedStyle(t).fontSize), n = 0;
  while (w() > avail && fs > 9.5 && n++ < 24) { fs -= .5; t.style.fontSize = fs + 'px'; }
}
new MutationObserver(() => fitPurrTxt()).observe($('purrTxt'), { childList: true, characterData: true, subtree: true });
new MutationObserver(() => fitPurrTxt()).observe($('barwrap'), { attributes: true, attributeFilter: ['class'] });
addEventListener('resize', () => requestAnimationFrame(fitPurrTxt));
if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitPurrTxt);
const fitLayoutPlain35b = fitLayout;
fitLayout = function () { const r = fitLayoutPlain35b.apply(this, arguments); fitPurrTxt(); return r; };

/* ===================== V35: on the win card Freyr winks, then licks his paw (instead of swinging his head) ===================== */
function cheerFace(el) {
  const svg = el && el.querySelector('svg.catsvg'); if (!svg) return;
  const eyes = svg.querySelector('.eyes'), NS = 'http://www.w3.org/2000/svg';
  if (eyes && !eyes.querySelector('.eyeL')) {
    const gL = document.createElementNS(NS, 'g'), gR = document.createElementNS(NS, 'g');
    gL.setAttribute('class', 'eyeL'); gR.setAttribute('class', 'eyeR');
    [...eyes.children].forEach(e => { const x = parseFloat(e.getAttribute('cx')); (x < 50 ? gL : gR).appendChild(e); });
    eyes.append(gL, gR);
  }
  const g = svg.querySelector('g'), tongue = svg.querySelector('.m-y');
  if (g && tongue && !svg.querySelector('.shutL')) {
    // happy closed eyes
    g.insertAdjacentHTML('beforeend',
      '<path class="shut shutL" d="M28.5 57.5 Q36 50.5 43.5 57.5" fill="none" stroke-width="3"/>' +
      '<path class="shut shutR" d="M56.5 57.5 Q64 50.5 71.5 57.5" fill="none" stroke-width="3"/>');
    // the paw that comes up to his mouth: over the face, under the tongue
    tongue.insertAdjacentHTML('beforebegin',
      '<g class="lpaw"><ellipse cx="58" cy="88" rx="11.5" ry="9.5" fill="#fff" stroke-width="3"/>' +
      '<path d="M52.5 84 V88 M58 83 V87.5 M63.5 84 V88" stroke="#E2D3E3" stroke-width="1.8"/>' +
      '<ellipse cx="58" cy="91.5" rx="4.2" ry="3" fill="#FFB3C9" stroke="none"/></g>');
  }
  el.classList.remove('dance', 'cheer'); void el.offsetWidth; el.classList.add('cheer');
}
const showEndPlain35 = showEnd;
showEnd = function (won) {
  const r = showEndPlain35.apply(this, arguments);
  const f = $('endFace');
  if (won) cheerFace(f); else f.classList.remove('cheer');
  return r;
};

/* ===================== V35: now and then a long level (more moves, bigger goals), with a tag on the level card ===================== */
const levelConfigPlain35 = levelConfig;
levelConfig = function (L) {
  const c = levelConfigPlain35.apply(this, arguments);
  if (L <= LEVELS.length && LEVELS[L - 1].long) c.long = true;
  return c;
};
const LONG_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2.5h12M6 21.5h12M7.5 2.5c0 5 4.5 6.5 4.5 9.5S7.5 16.5 7.5 21.5M16.5 2.5c0 5-4.5 6.5-4.5 9.5s4.5 4.5 4.5 9.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/><path d="M9.5 19.5c.8-2 2.5-3 2.5-3s1.7 1 2.5 3z" fill="#FFE27A"/></svg>';
const drawIntroExtrasPlain35 = drawIntroExtras;
drawIntroExtras = function () {
  const r = drawIntroExtrasPlain35.apply(this, arguments);
  if (cfg && cfg.long && !cfg.hard) {
    const d = $('introDiff'); d.hidden = false;
    d.innerHTML = '<span class="dtag dl">' + LONG_SVG + 'Langes Level</span><small>Mehr Züge, größere Ziele</small>';
  }
  return r;
};

/* ===================== V35: goals always fit in their box: one row, smaller, then a neat grid of two rows (label hidden) ===================== */
fitGoals = function () {
  const box = $('goals'), hb = box && box.closest('.goalsbox');
  if (!hb) return;
  const row = hb.closest('.hud-row');
  box.classList.remove('gtight', 'gtight2', 'grows', 'gmini'); hb.classList.remove('grows'); box.style.maxWidth = ''; box.style.removeProperty('--gc');
  if (row) row.classList.remove('noscore');
  if (typeof goals === 'undefined' || !goals || !goals.length || !box.clientWidth) return;
  // a goal sticking out of the box (or the box scrolling) counts as not fitting
  const over = () => {
    const h = hb.getBoundingClientRect(), cs = getComputedStyle(hb), l = h.left + parseFloat(cs.paddingLeft) - 2, r = h.right - parseFloat(cs.paddingRight) + 2;
    for (const c of box.children) { const k = c.getBoundingClientRect(); if (k.width && (k.left < l || k.right > r)) return true; }
    // the boxes of the panel must not run into each other either (the goals box can be squeezed below its own width)
    if (row) {
      const rs = [...row.children].filter(e => getComputedStyle(e).display !== 'none' && e.getBoundingClientRect().width).map(e => e.getBoundingClientRect());
      for (let i = 1; i < rs.length; i++) if (rs[i].left < rs[i - 1].right - 1) return true;
      const rr = row.getBoundingClientRect(); if (rs.length && rs[rs.length - 1].right > rr.right + 1) return true;
    }
    return box.scrollWidth > box.clientWidth + 1;
  };
  const reset = () => { box.classList.remove('gtight', 'gtight2', 'grows', 'gmini'); hb.classList.remove('grows'); box.style.removeProperty('--gc'); };
  const rows = () => { box.classList.remove('gtight', 'gtight2'); box.classList.add('grows'); hb.classList.add('grows'); box.style.setProperty('--gc', Math.ceil(goals.length / 2)); };
  // one row, then smaller, then (four or more goals) two rows
  const steps = allowRows => {
    reset(); if (!over()) return true;
    box.classList.add('gtight'); if (!over()) return true;
    box.classList.add('gtight2'); if (!over()) return true;
    if (allowRows && goals.length >= 2) { rows(); if (!over()) return true; }
    return false;
  };
  if (steps(goals.length >= 4)) return;
  // still no room (a narrow phone, or the level number as a fourth box in the first levels): the points make room,
  // they still show on the win card; then the same steps again, from the big icons on
  if (row) row.classList.add('noscore');
  if (steps(true)) return;
  box.classList.add('gmini');
  // the finale on a small phone: three rows
  if (over() && goals.length >= 5 && box.classList.contains('grows')) box.style.setProperty('--gc', Math.ceil(goals.length / 3));
};
addEventListener('resize', () => requestAnimationFrame(() => { if (!onMap) fitGoals(); }));
const fitLayoutPlain35c = fitLayout;
fitLayout = function () { const r = fitLayoutPlain35c.apply(this, arguments); if (!onMap && typeof goals !== 'undefined' && goals.length) fitGoals(); return r; };
