
/* ===================== V32: the game screen, restructured ===================== */
// Freyr sits next to the score panel (the panel moves into his row), the level number becomes a little tab on the panel,
// and his speech bubble only pops up while he talks: it shows for as long as it takes to read, then goes again.
(function () {
  const top = document.querySelector('main .top'), hud = document.querySelector('main .hud');
  if (top && hud && hud.parentElement !== top) top.insertBefore(hud, bubble);
  const lv = $('level'), box = lv && lv.closest('.hbox');
  if (box && hud) { box.classList.remove('hbox'); box.classList.add('ltab'); hud.appendChild(box); }
})();
let bubLeft = 0, bubLast = 0, bubT = 0;
// the time counts only while the bubble can be seen (not behind a card, not on the map)
function bubbleTick() {
  const now = performance.now(), dt = now - bubLast; bubLast = now;
  if (!onMap && !document.hidden && !document.querySelector('.overlay.show')) bubLeft -= dt;
  if (bubLeft <= 0) { bubble.classList.remove('show'); bubT = 0; return; }
  bubT = setTimeout(bubbleTick, 200);
}
const sayPlain32 = say;
say = function (text) {
  const r = sayPlain32.apply(this, arguments);
  bubble.classList.add('show');
  bubLeft = Math.max(2400, Math.min(6500, 1000 + String(text || '').length * 55)); bubLast = performance.now();
  if (!bubT) bubT = setTimeout(bubbleTick, 200);
  return r;
};
// long sentences get a little smaller instead of covering half the board: three short lines at most
fitBubble = function () {
  const b = bubble; b.style.fontSize = '';
  if (!b.firstChild) return;
  // as high as the room between Freyr's row and the board allows (on small screens it may reach over the board)
  const room = $('board').getBoundingClientRect().top - b.getBoundingClientRect().top - 6;
  const max = room >= 44 ? Math.min(92, room) : 66;
  let fs = parseFloat(getComputedStyle(b).fontSize); const min = Math.max(11, fs * .76);
  while (b.offsetHeight > max && fs > min) { fs -= .5; b.style.fontSize = fs + 'px'; }
};
fitLayout();
