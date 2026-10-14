
/* ===================== V27: leftover moves become extras, a stronger feast bowl, a Schnurr-Power you save up ===================== */

/* ---------- Schnurr-Power: one meter across all levels. It fills slowly, keeps its charge from level to level
   and waits until you decide where Freyr should jump ---------- */
try { const v = parseInt(localStorage.getItem('wm-purr'), 10); if (Number.isFinite(v)) purr = Math.max(0, Math.min(PURR_MAX, v)); } catch (e) {}
const drawPurrPlain27 = drawPurr;
drawPurr = function () { drawPurrPlain27(); try { localStorage.setItem('wm-purr', purr); } catch (e) {} syncMtap(); };
// the tapping paw only while Freyr sits in his spot and can jump: never during the win show, when he runs over the board.
// A full meter at the end of a level stays for the next one, and the bar says so.
let winShow = false;
function syncMtap() {
  const ready = purr >= PURR_MAX && isUnlocked('purr'), aiming = !!(aim && aim.kind === 'pounce');
  const over = winShow || winRunning || ending;
  const show = ready && !aiming && !over && !mascot.classList.contains('away');
  if (mtap.hidden === show) mtap.hidden = !show;
  if (show) placeMtap();
  if (ready && over && !aiming) $('purrTxt').textContent = 'Voll! Bleibt fürs nächste Level';
}
new MutationObserver(syncMtap).observe(mascot, { attributes: true, attributeFilter: ['class'] });
const winSequencePlain27 = winSequence;
winSequence = async function () {
  winShow = true; syncMtap();
  try { return await winSequencePlain27.apply(this, arguments); } finally { winShow = false; syncMtap(); }
};
const rescuePlain27 = $('rescueBtn').onclick;
$('rescueBtn').onclick = function (e) { rescuePlain27.call(this, e); drawPurr(); };
// the level card says when you bring a full meter into the level
const showIntroPlain27 = showIntro;
showIntro = function () {
  showIntroPlain27();
  let p = $('introPurr');
  const on = isUnlocked('purr') && purr >= PURR_MAX;
  if (!p) { p = document.createElement('p'); p.id = 'introPurr'; p.className = 'ipurr'; const g = $('introGoals'); if (g) g.after(p); }
  p.hidden = !on;
  if (on) p.innerHTML = `<span class="ipi">${ICONS[5]}</span><span>Schnurr-Power ist voll. Tipp im Level auf ${esc(catName)}, wenn du sie brauchst.</span>`;
};
INTRO.purr = () => [ICONS[5], 'Neu: Schnurr-Power', 'Jeder Cremesnack lädt ' + catName + 's Schnurr-Power auf. Ist sie voll, springt er auf ein Feld deiner Wahl und räumt Reihe und Spalte ab. Was du nicht nutzt, nimmst du ins nächste Level mit.'];
INTRO.bowl = () => [xicon('bowl'), 'Neu: Festmahl-Napf', 'Fünf gleiche in einer Reihe ergeben den Festmahl-Napf. Tausch ihn mit einem Leckerli, dann frisst ' + catName + ' alle von dieser Sorte und alles rund um den Napf.'];
// the first time the meter is full after this update: say once that it can be saved for later
const purrNoticePlain27 = purrNotice;
purrNotice = function () {
  const fresh = purrNew;
  purrNoticePlain27();
  if (!fresh || tut) return;
  let told = false; try { told = !!localStorage.getItem('wm-purr-keep'); } catch (e) {}
  if (told) return;
  try { localStorage.setItem('wm-purr-keep', '1'); } catch (e) {}
  say('Schnurr-Power voll! Tipp mich an, oder heb sie dir auf. Sie bleibt dir auch im nächsten Level.');
};

/* ---------- after the zoomies: every move still left becomes an extra on the board, then they all go off ---------- */
async function extraRain() {
  const cands = [];
  for (let k = 0; k < N * N; k++) { const x = grid[k / N | 0][k % N]; if (x && isNormal(x.type) && !x.locked && !x.gold) cands.push(k); }
  shuffleList(cands);
  const n = Math.min(moves, cands.length, 30);
  if (n <= 0) return;
  mascot.classList.add('away');
  callout('Extra-Regen!', n === 1 ? 'Dein letzter Zug wird ein Extra' : 'Jeder übrige Zug wird ein Extra');
  sparkle(); await sleep(REDUCED ? 100 : 620);
  const kinds = ['cat', 'cat', 'nip', 'laser'];
  for (let i = 0; i < n; i++) {
    const k = cands[i], r = k / N | 0, c = k % N, old = grid[r][c];
    const kind = kinds[Math.floor(Math.random() * kinds.length)], sp = mk(kind);
    if (kind === 'cat') sp.dir = Math.random() < .5 ? 'h' : 'v';
    grid[r][c] = sp;
    const oe = els.get(old.id); if (oe) oe.remove(); els.delete(old.id);
    const el = tileEl(sp); place(sp, r, c); el.classList.add('spawn'); spawnFx(k, kind);
    moves--; updateHud();
    const m = $('moves'); if (m) { m.classList.remove('bump'); void m.offsetWidth; m.classList.add('bump'); }
    chime(3 + i % 8); buzz(10);
    await sleep(REDUCED ? 15 : Math.max(70, 170 - i * 9));
  }
  // more moves than treats on the board: the rest still counts
  if (moves > 0) { const extra = moves * 100; score += extra; lastBonus += extra; moves = 0; updateHud(); }
  await sleep(REDUCED ? 80 : 380);
}

/* ---------- Festmahl-Napf: it eats its kind and everything right round the bowl ---------- */
EXTRA.bowl.tip = () => 'Festmahl-Napf! Tausch ihn mit einem Leckerli: ' + catName + ' frisst alle von der Sorte und alles rund um den Napf.';
const firePlain27 = fire;
fire = function (cell, k, clear, delay, base, fxq) {
  firePlain27(cell, k, clear, delay, base, fxq);
  if (cell.type !== 'bowl' || cell.eat === 'all') return;
  const r = k / N | 0, c = k % N;
  for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
    const rr = r + dr, cc = c + dc;
    if (!inB(rr, cc) || !mask[rr][cc] || !grid[rr][cc]) continue;
    const k2 = rr * N + cc; if (!clear.has(k2)) { clear.add(k2); delay.set(k2, base + 90); }
  }
  if (!REDUCED) {
    const [x, y, cw] = cellXY(k);
    shock(x, y, cw * .3, cw * 1.9, '#FFD23F', base + 70, 420, cw * .2, 'rgba(255,214,120,1)');
    later(base + 80, () => burst(x, y, 16, 1.6, ['#7A3E1C', '#A0592A', '#FF4FA3', '#FFE14D', '#3EB8FF', '#FFFFFF']));
  }
};
// two bowls: everything goes, and then a second helping for the whole board
async function nachschlag() {
  const keys = [], bd = new Map(), mid = (N - 1) / 2;
  for (let k = 0; k < N * N; k++) {
    const r = k / N | 0, c = k % N;
    if (!mask[r][c] || !grid[r][c]) continue;
    keys.push(k); bd.set(k, 140 + Math.round(Math.hypot(r - mid, c - mid) * 75));
  }
  if (!keys.length) return;
  callout('Nachschlag!', 'Noch eine Runde Festmahl'); extraSound('bowl'); buzz([40, 60, 40]);
  if (!REDUCED) {
    const b = boardEl.getBoundingClientRect(), cw = b.width / N, x = b.left + b.width / 2, y = b.top + b.height / 2;
    vortex(x, y, cw, 0, 1000); boardFlash(.18, 60, 220);
    orb(x, y, cw * .4, cw * 3, ['#ffffff', 'rgba(255,236,170,.9)', 'rgba(255,120,200,.45)'], 0, 520, .25);
  }
  await sleep(REDUCED ? 80 : 420);
  await resolve(new Set(keys), null, '', null, false, bd);
}
