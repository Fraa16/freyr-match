
/* ===================== V26: no jump button, a tap on Freyr is enough; a full purr meter you can't miss ===================== */
// a paw taps on Freyr while his meter is full, the same paw the lessons use for "tap here"
const mtap = document.createElement('span');
mtap.className = 'mtap'; mtap.setAttribute('aria-hidden', 'true'); mtap.innerHTML = POINT_SVG; mtap.hidden = true;
mascot.after(mtap);
function placeMtap() {
  if (mtap.hidden) return;
  const w = mascot.offsetWidth, h = mascot.offsetHeight, s = Math.round(w * .46);
  Object.assign(mtap.style, { width: s + 'px', height: s + 'px', left: Math.round(mascot.offsetLeft + w * .62) + 'px', top: Math.round(mascot.offsetTop + h * .56) + 'px' });
}
addEventListener('resize', placeMtap);
let readyMoves = 0;
const drawPurrPlain26 = drawPurr;
drawPurr = function () {
  drawPurrPlain26();
  const ready = purr >= PURR_MAX && isUnlocked('purr'), aiming = !!(aim && aim.kind === 'pounce');
  mascot.classList.toggle('aiming', aiming);
  if (ready) $('purrTxt').textContent = aiming ? 'Tipp auf ein Feld' : 'Voll! Tipp auf ' + catName;
  else readyMoves = 0;
  const show = ready && !aiming;
  if (mtap.hidden === show) mtap.hidden = !show;
  placeMtap();
};
// the moment the meter is full: stars fly from the bar to Freyr, he jumps up and meows
const PSTAR = `<svg viewBox="-12 -12 24 24">${SPARK4(0, 0, 1.1, '#FFD23F')}${SPARK4(0, 0, .5, '#FFFFFF')}</svg>`;
function purrReady() {
  if (ending || winRunning) return;
  const go = () => {
    if (ending || winRunning || purr < PURR_MAX || onMap) return;
    mascot.classList.remove('bounce', 'powered', 'nudge'); void mascot.offsetWidth; mascot.classList.add('powered');
    const m = mascot.getBoundingClientRect();
    burst(m.left + m.width / 2, m.top + m.height / 2, 22, 1.3, ['#FFD23F', '#FFFFFF', '#FF7AC6', '#FFB21A']);
    meow(.8);
  };
  if (REDUCED) return go();
  const b = $('barwrap').getBoundingClientRect(), m = mascot.getBoundingClientRect(), tx = m.left + m.width / 2, ty = m.top + m.height / 2;
  const n = 7;
  for (let i = 0; i < n; i++) {
    const s = document.createElement('div'); s.className = 'pstar'; s.innerHTML = PSTAR;
    const x = b.left + b.width * (i + .5) / n, y = b.top + b.height / 2;
    s.style.left = x + 'px'; s.style.top = y + 'px'; document.body.appendChild(s);
    const dx = tx - x, dy = ty - y;
    const a = s.animate([
      { transform: 'translate(0,0) scale(.4) rotate(0deg)', opacity: 0 },
      { transform: `translate(${dx * .3}px,${dy * .3 - 34}px) scale(1.25) rotate(90deg)`, opacity: 1, offset: .35 },
      { transform: `translate(${dx}px,${dy}px) scale(.5) rotate(200deg)`, opacity: .9 }
    ], { duration: 480 + i * 40, delay: i * 25, easing: 'cubic-bezier(.45,0,.7,1)', fill: 'both' });
    a.onfinish = () => s.remove();
  }
  setTimeout(go, 560);
}
// and if two moves go by without using it, Freyr reminds you once
function purrRemind() {
  if (purr < PURR_MAX || aim || onMap || ending || winRunning || tut) return;
  mascot.classList.remove('bounce', 'powered', 'nudge'); void mascot.offsetWidth; mascot.classList.add('nudge');
  say('Meine Schnurr-Power ist voll! Tipp auf mich, dann auf ein Feld.');
}
const trySwapPlain26 = trySwap;
trySwap = async function () {
  const m0 = moves, full = purr >= PURR_MAX;
  const r = await trySwapPlain26.apply(this, arguments);
  if (full && moves < m0 && purr >= PURR_MAX && ++readyMoves === 2) purrRemind();
  return r;
};
