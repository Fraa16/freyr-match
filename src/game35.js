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
