/* ===================== V37: Freyr's own chewing (chomp37.json): whole bursts of 0.75 s, so it sounds like eating ===================== */
// one burst for a small match, two overlapping ones for a big one; never the same burst twice in a row
let chompLast = -1;
chomp = function (count, delay = 0, rate = 1) {
  if (!audioOk() || !chompBuf) return;
  const now = actx.currentTime + .02 + delay, n = count >= 3 ? 2 : 1;
  for (let i = 0; i < n; i++) {
    let k = Math.floor(Math.random() * CHOMPS.length);
    if (k === chompLast) k = (k + 1) % CHOMPS.length;
    chompLast = k;
    const at = now + i * .24, src = actx.createBufferSource(), g = actx.createGain(), v = n > 1 ? .85 : 1;
    src.buffer = chompBuf; src.playbackRate.value = rate * (.96 + Math.random() * .08);
    g.gain.setValueAtTime(v, at); g.gain.setValueAtTime(v, at + .58); g.gain.linearRampToValueAtTime(0, at + .74);
    src.connect(g); g.connect(master); src.start(at, CHOMPS[k], .76);
  }
};
