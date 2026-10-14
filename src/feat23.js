
/* ===================== V23: fixes from the full audit ===================== */
let ending = false, winRunning = false, saidGold = false, boostPaid = 0, goalMode = 0;
const orList = a => a.length > 1 ? a.slice(0, -1).join(', ') + ' oder ' + a[a.length - 1] : a[0] || '';

/* ---------- the end of a level: no pause, no leaving, never two cards at once ---------- */
function closeSideCards() {
  if ($('setOv').classList.contains('show')) closeSettings();
  for (const id of ['pauseOv', 'quitOv']) $(id).classList.remove('show');
}
const winSequencePlain = winSequence;
winSequence = async function () {
  ending = true; winRunning = true; closeSideCards();
  try { return await winSequencePlain(); } finally { winRunning = false; }
};
const clockRingPlain = clockRing;
clockRing = async function () { ending = true; closeSideCards(); return clockRingPlain(); };
const showEndPlain = showEnd;
showEnd = function (won) { ending = true; closeSideCards(); return showEndPlain(won); };
const startLevelPlain = startLevel;
startLevel = function () { ending = false; winRunning = false; saidGold = false; boostPaid = 0; goalMode = 0; return startLevelPlain(); };
const rescuePlain = $('rescueBtn').onclick;
$('rescueBtn').onclick = function (e) { const t = treats; rescuePlain.call(this, e); if (treats < t) ending = false; };
const openPausePlain = openPause;
openPause = function () { if (ending || winRunning) return; return openPausePlain(); };
$('pauseBtn').onclick = openPause;
const tryPouncePlain = tryPounce;
tryPounce = function () { if (ending) return; return tryPouncePlain(); };
mascot.onclick = tryPounce;
// leaving: free before the first move (the life and a bought boost come back), otherwise ask first
$('toMap').onclick = async () => {
  $('pauseOv').classList.remove('show');
  for (let i = 0; busy && i < 120; i++) await sleep(50);
  if (busy || onMap || ending || document.querySelector('.overlay.show')) return;
  if (moves === startMoves && !rescues && score === 0) {
    refundLife(); clearTry();
    if (boostPaid) { treats += boostPaid; boostPaid = 0; saveJar(); }
    return showMap();
  }
  $('quitFace').innerHTML = CAT_ICON();
  $('quitText').textContent = winStreak ? 'Das Leben für diesen Versuch ist dann weg, und deine Glückssträhne auch.' : 'Das Leben für diesen Versuch ist dann weg.';
  const card = $('quitCard'); card.classList.remove('pop-in'); void card.offsetWidth; card.classList.add('pop-in');
  $('quitOv').classList.add('show');
};
$('quitGo').onclick = () => { $('quitOv').classList.remove('show'); $('endOv').classList.remove('show'); registerLoss(level); showMap(); };
// remember what a boost on the level card cost, for a free leave before the first move
const startGiftsPlain = startGifts;
startGifts = async function () { const t0 = treats, had = !!pick; await startGiftsPlain(); boostPaid = had ? Math.max(0, t0 - treats) : 0; };

/* ---------- Freyr's bubble: a fixed row, long sentences get a little smaller instead of pushing the board down ---------- */
function fitBubble() {
  const b = bubble; b.style.fontSize = '';
  if (!b.firstChild) return;
  const row = b.parentElement.clientHeight; if (!row) return;
  const cs = getComputedStyle(b), pad = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
  const range = document.createRange(); range.selectNodeContents(b);
  let fs = parseFloat(cs.fontSize); const min = Math.max(10.5, fs * .74);
  while (range.getBoundingClientRect().height > row - pad + .5 && fs > min) { fs -= .5; b.style.fontSize = fs + 'px'; }
}
const sayPlain = say;
say = function (text) { sayPlain(text); fitBubble(); };

/* ---------- the score panel keeps its size: room for a five-digit score, goal chips that only ever get tighter ---------- */
$('score').parentElement.classList.add('scorebox');
fitGoals = function () {
  const box = $('goals'), hb = box && box.closest('.goalsbox');
  if (!hb) return;
  const apply = m => {
    box.classList.toggle('gtight', m === 1); box.classList.toggle('grows', m === 2); hb.classList.toggle('grows', m === 2);
    box.style.maxWidth = m === 2 ? (Math.ceil(goals.length / 2) * 22) + 'px' : '';
  };
  if (goals.length < 4 || !box.clientWidth) { goalMode = 0; apply(0); return; }
  apply(goalMode);
  while (goalMode < 2 && box.scrollWidth > box.clientWidth + 1) apply(++goalMode);
};
addEventListener('resize', () => { goalMode = 0; if (goals && goals.length >= 4) fitGoals(); fitBubble(); });

/* ---------- small things ---------- */
// the cat button in the game says what a tap does
const drawPurrPlain = drawPurr;
drawPurr = function () {
  drawPurrPlain();
  const ready = purr >= PURR_MAX;
  mascot.setAttribute('aria-label', !isUnlocked('purr') ? catName : ready ? catName + ' springen lassen' : catName + ', Schnurr-Power ' + purr + ' von ' + PURR_MAX);
};
// Escape closes the small cards on a computer too
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if ($('quitOv').classList.contains('show')) $('quitStay').click();
  else if ($('kitOv').classList.contains('show')) $('kitLater').click();
  else if ($('chestOv').classList.contains('show') && $('chestBtn').dataset.step === 'close') $('chestBtn').click();
  else if ($('livesOv').classList.contains('show')) { $('livesOv').classList.remove('show'); if (!onMap) showMap(); }
});
// the main buttons of every card stay in reach on short screens
(function () {
  const wrapCta = ids => {
    const els = ids.map(id => $(id)).filter(Boolean); if (!els.length || els[0].parentElement.classList.contains('cta')) return;
    const card = els[0].closest('.card'); if (!card) return;
    let anchor = els[0]; while (anchor.parentElement !== card) anchor = anchor.parentElement;
    const w = document.createElement('div'); w.className = 'cta'; anchor.before(w); els.forEach(e => w.appendChild(e));
    if (anchor !== els[0] && !anchor.children.length) anchor.remove();
  };
  wrapCta(['livesBtn']); wrapCta(['chestBtn']); wrapCta(['kitWear', 'kitLater']); wrapCta(['quitStay', 'quitGo']); wrapCta(['pauseGo', 'toMap']);
  // "Zur Karte" on the end card is the X in the corner now, like on the level card
  const b = $('endMap'), card = $('endCard');
  if (b && card) { b.className = 'xbtn'; b.innerHTML = X_ICON; b.setAttribute('aria-label', 'Zur Karte'); b.title = 'Zur Karte'; card.prepend(b); }
})();

/* ---------- the treats pill: four digits get a smaller number, so the top bar never overlaps ---------- */
const drawTreatsPillPlain = drawTreatsPill;
drawTreatsPill = function () { drawTreatsPillPlain(); $('mTreats').classList.toggle('big', treats >= 1000); };
