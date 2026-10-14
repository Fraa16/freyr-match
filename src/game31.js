
/* ===================== V31: the board gets the room ===================== */
// The game screen is one screen high and the board takes what is left. When that would make it narrower than the screen,
// the panels around it get more compact, step by step: the gaps, the score panel and the tool bar first, Freyr's row last
// (he and his bubble stay), until the board has the whole width. Not in the side-by-side layout of a phone held sideways.
const FITS = ['fit1', 'fit2', 'fit3', 'fit4'];
const SIDE = matchMedia('(orientation:landscape) and (max-height:520px)');
let fitLv = -1;
function fitLayout() {
  const html = document.documentElement, st = document.querySelector('main .stage');
  if (!st) return;
  html.classList.remove(...FITS);
  let lv = 0;
  if (!SIDE.matches) {
    for (; lv < FITS.length; lv++) {
      const r = st.getBoundingClientRect();
      if (!r.width || r.height + 1 >= r.width) break;
      html.classList.add(FITS[lv]);
    }
  }
  if (lv !== fitLv) { fitLv = lv; BG = null; if (bubble.firstChild) fitBubble(); return true; }
  return false;
}
// a change that does not come with a resize (fonts arriving late): the treat pictures follow
function refit() { if (fitLayout() && !onMap) requestAnimationFrame(() => buildBitmaps()); }
let fitRaf = 0;
addEventListener('resize', () => { cancelAnimationFrame(fitRaf); fitRaf = requestAnimationFrame(fitLayout); });
if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
const startLevelPlain31 = startLevel;
startLevel = function () { const r = startLevelPlain31.apply(this, arguments); fitLayout(); return r; };
fitLayout();
