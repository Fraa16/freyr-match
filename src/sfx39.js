
/* ===================== V39: new sounds for the extras ===================== */
// Made in the browser like the rest: filtered noise for swishes and puffs, FM bells, harp plucks, and a small room
// so they don't sound dry. Everything goes through one compressor, so a big combo stays loud without crackling.
// FX39 switches between the new sounds and animations and the old ones (the preview has a switch for it).
let FX39 = true;
try { FX39 = localStorage.getItem('wm-fx39') !== 'old'; } catch (e) {}
const SX = {};
const sxT = () => actx.currentTime + .01;
// F major pentatonic (the music is in F), i counts up from the base note
const PENT = [0, 2, 4, 7, 9];
const pent = (i, base = 77) => mf(base + 12 * Math.floor(i / 5) + PENT[((i % 5) + 5) % 5]);
function sxOut() {
  if (SX.out && SX.ctx === actx) return SX.out;
  SX.ctx = actx;
  const comp = actx.createDynamicsCompressor();
  comp.threshold.value = -16; comp.knee.value = 12; comp.ratio.value = 4; comp.attack.value = .003; comp.release.value = .2;
  const g = actx.createGain(); g.gain.value = 1.1; g.connect(comp); comp.connect(master);
  const sr = actx.sampleRate, len = Math.floor(sr * 1.5), ir = actx.createBuffer(2, len, sr);
  for (let ch = 0; ch < 2; ch++) { const d = ir.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.4) * (i < 60 ? i / 60 : 1); }
  const cv = actx.createConvolver(); cv.buffer = ir; const wg = actx.createGain(); wg.gain.value = .55; cv.connect(wg); wg.connect(comp);
  const nl = sr * 2, nb = actx.createBuffer(1, nl, sr), nd = nb.getChannelData(0);
  for (let i = 0; i < nl; i++) nd[i] = Math.random() * 2 - 1;
  SX.noise = nb; SX.verb = cv; SX.out = g;
  return g;
}
// a channel: optionally panned, with some of it sent to the room
function sxBus(pan = 0, wet = .2, vol = 1) {
  const out = sxOut(), g = actx.createGain(); g.gain.value = vol;
  let n = g;
  if (pan && actx.createStereoPanner) { const p = actx.createStereoPanner(); p.pan.value = Math.max(-1, Math.min(1, pan)); g.connect(p); n = p; }
  n.connect(out);
  if (wet > 0) { const s = actx.createGain(); s.gain.value = wet; n.connect(s); s.connect(SX.verb); }
  return g;
}
function sxEnv(g, t, vol, a, dur) { g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + a); g.gain.exponentialRampToValueAtTime(.0005, t + dur); }
function sxO(dest, type, f0, t, dur, vol, f1, glide, a = .006) {
  const o = actx.createOscillator(), g = actx.createGain(); o.type = type;
  o.frequency.setValueAtTime(f0, t); if (f1) o.frequency.exponentialRampToValueAtTime(f1, t + (glide || dur));
  sxEnv(g, t, vol, a, dur); o.connect(g); g.connect(dest); o.start(t); o.stop(t + dur + .05);
}
function sxN(dest, t, dur, vol, type, f0, f1, q = 1, a = .01) {
  const s = actx.createBufferSource(), f = actx.createBiquadFilter(), g = actx.createGain();
  s.buffer = SX.noise; f.type = type; f.Q.value = q;
  f.frequency.setValueAtTime(f0, t); if (f1) f.frequency.exponentialRampToValueAtTime(f1, t + dur);
  sxEnv(g, t, vol, a, dur); s.connect(f); f.connect(g); g.connect(dest);
  s.start(t, Math.random() * 1.2); s.stop(t + dur + .05);
}
// a bell: one sine bending another (FM), bright at the strike, then pure
function sxBell(dest, f, t, dur, vol, ratio = 3.5, idx = 2.2) {
  const c = actx.createOscillator(), m = actx.createOscillator(), mg = actx.createGain(), g = actx.createGain();
  c.frequency.value = f; m.frequency.value = f * ratio;
  mg.gain.setValueAtTime(f * idx, t); mg.gain.exponentialRampToValueAtTime(Math.max(1, f * .02), t + dur * .8);
  m.connect(mg); mg.connect(c.frequency); sxEnv(g, t, vol, .003, dur);
  c.connect(g); g.connect(dest); c.start(t); m.start(t); c.stop(t + dur + .05); m.stop(t + dur + .05);
}
// a harp string: bright at first, then soft
function sxPluck(dest, f, t, vol, dur = .55) {
  const o = actx.createOscillator(), o2 = actx.createOscillator(), lp = actx.createBiquadFilter(), g = actx.createGain(), g2 = actx.createGain();
  o.type = 'triangle'; o2.type = 'sine'; o.frequency.value = f; o2.frequency.value = f * 2.005; g2.gain.value = .35;
  lp.type = 'lowpass'; lp.frequency.setValueAtTime(Math.min(16000, f * 8), t); lp.frequency.exponentialRampToValueAtTime(f * 1.5, t + dur);
  o.connect(lp); o2.connect(g2); g2.connect(lp); lp.connect(g); sxEnv(g, t, vol, .004, dur); g.connect(dest);
  o.start(t); o2.start(t); o.stop(t + dur + .05); o2.stop(t + dur + .05);
}
const SFX = {
  // Flitzekatze: two swishes run out to both ends of the line (left and right in the ears), a rising zip, two little bells
  cat(at, dir, big) {
    const t = sxT() + at, layers = dir === 'v' ? [[0, 1], [0, -1]] : dir === 'x' ? [[-.7, 1], [.7, 1], [0, -1]] : [[-.7, 1], [.7, 1]];
    for (const [p, up] of layers) {
      const b = sxBus(p, .18);
      sxN(b, t, .34, big ? .42 : .34, 'bandpass', up > 0 ? 650 : 4800, up > 0 ? 5200 : 700, 1.4, .05);
      sxN(b, t + .02, .22, .1, 'highpass', 5000, 9000, .7, .02);
    }
    const c = sxBus(0, .25);
    sxO(c, 'triangle', 330, t, .24, .08, 1320, .17);
    sxO(c, 'sine', 660, t + .015, .18, .05, 2640, .15);
    sxBell(c, 2093, t + .16, .5, .035); sxBell(c, 2637, t + .21, .5, .03);
    if (big) sxO(c, 'sine', 110, t, .5, .3, 40, .42);
  },
  // Katzenminze: a soft low thump, a puff of air, a springy boing, leaves rustling out to both sides, a clear ping
  nip(at, R = 1) {
    const t = sxT() + at, c = sxBus(0, .22), big = R > 1;
    sxO(c, 'sine', big ? 120 : 150, t, big ? .6 : .4, .36, 42, big ? .5 : .32);
    sxN(c, t, big ? .55 : .4, .3, 'lowpass', 2600, 260, .8, .006);
    sxO(c, 'sine', 170, t + .03, .3, .13, 480, .14);
    sxO(c, 'triangle', 340, t + .04, .22, .04, 960, .12);
    for (const p of [-.55, .55]) sxN(sxBus(p, .15), t + .08, .38, .1, 'highpass', 2600, 7000, .6, .03);
    sxBell(c, 1568, t + .1, .6, .03, 2.01, 1.2);
  },
  // Laserpunkt: every jump a zap, every landing a note; the notes climb, so a chain of hits goes up the scale
  laserHit(at, i, pan) {
    const t = sxT() + at, b = sxBus(pan, .2);
    sxO(b, 'square', 1900, t, .11, .026, 320, .1, .002);
    sxO(b, 'sine', 3800, t, .09, .04, 700, .08, .002);
    sxN(b, t, .05, .13, 'highpass', 4500, 0, .7, .001);
    sxBell(b, pent(i + 5), t + .015, .35, .04, 2, 1.5);
  },
  // Festmahl-Napf: a deep whomp, a harp running up, a shimmering chord
  bowl(at) {
    const t = sxT() + at, c = sxBus(0, .35);
    sxO(c, 'sine', 95, t, .6, .3, 48, .5);
    sxN(c, t, .5, .15, 'lowpass', 1200, 200, .7, .01);
    for (let i = 0; i < 10; i++) sxPluck(c, pent(i, 72), t + .04 + i * .042, .07 * (1 - i / 16), .6);
    [77, 81, 84, 89].forEach((m, i) => sxBell(c, mf(m + 12), t + .38 + i * .03, 1.3, .026, 3.5, 1.6));
  },
  // one crackle for each rainbow bolt
  zap(at, pan) { const t = sxT() + at, b = sxBus(pan, .1); sxN(b, t, .07, .085, 'bandpass', 5200, 2400, 2.5, .001); sxO(b, 'sawtooth', 3200, t, .05, .011, 1200, .05, .001); },
  zaps(times) { times.slice(0, 14).forEach(at => SFX.zap(Math.max(0, at) / 1000, Math.random() * 1.4 - .7)); },
  // a new extra appears
  spawn(kind) {
    const t = sxT(), c = sxBus(0, .3);
    if (kind === 'cat') { sxN(c, t, .25, .18, 'bandpass', 900, 4800, 1.5, .03); [84, 88, 91].forEach((m, i) => sxBell(c, mf(m + 12), t + .05 + i * .06, .5, .05)); }
    else if (kind === 'nip') { sxO(c, 'sine', 300, t, .16, .13, 900, .1); [79, 86].forEach((m, i) => sxPluck(c, mf(m), t + .06 + i * .07, .08)); sxBell(c, mf(98), t + .2, .5, .03, 2.01, 1.2); }
    else if (kind === 'laser') { sxO(c, 'square', 600, t, .1, .04, 2400, .08); sxO(c, 'square', 900, t + .09, .12, .04, 3600, .09); sxO(c, 'sine', 1200, t, .2, .06, 4800, .18); sxBell(c, mf(100), t + .2, .4, .05, 2, 1.5); }
    else { for (let i = 0; i < 8; i++) sxPluck(c, pent(i, 72), t + i * .045, .07); [89, 93, 96].forEach((m, i) => sxBell(c, mf(m), t + .36 + i * .02, 1.4, .028)); sxN(c, t + .3, .9, .05, 'bandpass', 3000, 9000, 3, .2); }
  },
  // a bowl combo turns treats into extras: one rising harp note each, over a swell
  convStart(at, n, step) {
    const t = sxT() + at, c = sxBus(0, .4), dur = n * step + .45;
    sxN(c, t, dur, .08, 'bandpass', 500, 4000, 2.5, dur * .8);
    sxO(c, 'sine', 220, t, dur, .05, 880, dur, dur * .7);
  },
  conv(at, i, kind) {
    const t = sxT() + at, c = sxBus(((i * 37) % 9 - 4) / 6, .3);
    sxPluck(c, pent(i, 72), t, .07, .5);
    sxBell(c, pent(i + 7, 72), t + .01, .3, .018, kind === 'laser' ? 2 : 3.5, 1.2);
  },
  // under a big combo: a deep boom and a crash
  boom(at, size = 1) {
    const t = sxT() + at, c = sxBus(0, .45);
    sxO(c, 'sine', 80, t, 1.1 * size, .4, 30, .9 * size);
    sxO(c, 'triangle', 160, t, .35, .11, 60, .3);
    sxN(c, t, 1.2 * size, .24, 'lowpass', 4000, 180, .6, .005);
    sxN(c, t, .5, .1, 'highpass', 3000, 8000, .5, .002);
  },
  // Krallenkratzer: the paw comes in, three claws bite, a tearing scratch runs across from left to right
  scratch(at, dur) {
    const t = sxT() + at, b = sxBus(0, .2), t1 = t + .1;
    sxN(b, t - .08, .22, .16, 'bandpass', 500, 2600, 1.2, .1);
    const s = actx.createBufferSource(), f = actx.createBiquadFilter(), am = actx.createGain(), g = actx.createGain(), lfo = actx.createOscillator(), lg = actx.createGain();
    s.buffer = SX.noise; f.type = 'bandpass'; f.Q.value = 2.2; f.frequency.setValueAtTime(1400, t1); f.frequency.linearRampToValueAtTime(2800, t1 + dur);
    lfo.type = 'square'; lfo.frequency.setValueAtTime(28, t1); lfo.frequency.linearRampToValueAtTime(46, t1 + dur);
    am.gain.value = .5; lg.gain.value = .5; lfo.connect(lg); lg.connect(am.gain);
    g.gain.setValueAtTime(0, t1); g.gain.linearRampToValueAtTime(.55, t1 + .03); g.gain.setValueAtTime(.55, t1 + dur * .85); g.gain.exponentialRampToValueAtTime(.001, t1 + dur + .08);
    s.connect(f); f.connect(am); am.connect(g);
    let n = g;
    if (actx.createStereoPanner) { const p = actx.createStereoPanner(); p.pan.setValueAtTime(-.85, t1); p.pan.linearRampToValueAtTime(.85, t1 + dur); g.connect(p); n = p; }
    n.connect(sxOut()); const w = actx.createGain(); w.gain.value = .15; n.connect(w); w.connect(SX.verb);
    s.start(t1, Math.random()); s.stop(t1 + dur + .12); lfo.start(t1); lfo.stop(t1 + dur + .12);
    for (let i = 0; i < 3; i++) sxN(b, t1 - .01 + i * .022, .05, .2, 'highpass', 3500, 0, .8, .001);
    sxO(b, 'sine', 150, t1 + dur, .28, .2, 60, .22);
    sxBell(b, mf(96), t1 + dur + .02, .45, .025, 2, 1.4);
  },
  // two bowls: a swell that charges up (the harp gets faster and faster) ...
  feastCharge(at, dur) {
    const t = sxT() + at, c = sxBus(0, .4);
    sxN(c, t, dur + .05, .2, 'bandpass', 250, 3200, 3, dur * .9);
    sxO(c, 'sine', 110, t, dur + .05, .13, 440, dur, dur * .85);
    sxO(c, 'triangle', 220, t, dur + .05, .045, 880, dur, dur * .85);
    for (let k = 0, u = 0; u < dur - .03; k++) { sxPluck(c, pent(k, 65), t + u, .045 + .03 * u / dur, .35); u += .1 * Math.pow(.86, k) + .018; }
  },
  // ... then a big bang, a full chord, and glitter falling down
  feastBang(at) {
    const t = sxT() + at, c = sxBus(0, .55);
    SFX.boom(at, 1.4);
    [53, 57, 60, 65, 69, 72].forEach((m, i) => sxO(c, 'triangle', mf(m), t + i * .012, 1.8, .04, 0, 0, .01));
    [89, 93, 96, 101].forEach((m, i) => sxBell(c, mf(m), t + .05 + i * .04, 2, .028, 3.5, 1.8));
    for (let i = 0; i < 16; i++) sxBell(sxBus(Math.random() * 1.6 - .8, .4), pent(18 - i, 72), t + .3 + i * .07 + Math.random() * .03, .5, .02, 3.5, 1.3);
  },
  // won with the last move: two heartbeats, then a crash, a brass stab and a ta-da
  clutch(at, beat) {
    const t = sxT() + at, c = sxBus(0, .25);
    for (const u of [0, .52]) { sxO(c, 'sine', 70, t + u, .22, .5, 42, .2, .004); sxO(c, 'sine', 64, t + u + .17, .26, .38, 40, .24, .004); }
    const t2 = t + beat, b = sxBus(0, .5);
    SFX.boom(at + beat, 1);
    sxN(b, t2, 1.8, .2, 'highpass', 6500, 4000, .6, .002);
    sxN(b, t2, .9, .12, 'bandpass', 3000, 1500, .8, .002);
    // the stab: saws through a closing lowpass
    const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.Q.value = 2; lp.frequency.setValueAtTime(4500, t2); lp.frequency.exponentialRampToValueAtTime(700, t2 + .6); lp.connect(b);
    [53, 60, 65, 69, 72].forEach(m => { sxO(lp, 'sawtooth', mf(m), t2, .7, .045, 0, 0, .01); sxO(lp, 'sawtooth', mf(m) * 1.004, t2, .7, .03, 0, 0, .01); });
    [[72, .55], [77, .72]].forEach(([m, u]) => { sxO(b, 'triangle', mf(m), t2 + u, .5, .09, 0, 0, .01); sxBell(b, mf(m + 12), t2 + u, .9, .04); });
    [89, 93, 96].forEach((m, i) => sxBell(b, mf(m), t2 + .8 + i * .05, 1.4, .03));
  },
  // the second helping: the board swirls round and round into the bowl, then a gulp
  whirl(at, dur) {
    const t = sxT() + at, out = sxOut();
    const s = actx.createBufferSource(), f = actx.createBiquadFilter(), g = actx.createGain(); s.buffer = SX.noise; s.loop = true;
    f.type = 'bandpass'; f.Q.value = 4; f.frequency.setValueAtTime(400, t); f.frequency.exponentialRampToValueAtTime(2400, t + dur);
    const lfo = actx.createOscillator(), lg = actx.createGain(); lfo.frequency.setValueAtTime(3, t); lfo.frequency.linearRampToValueAtTime(9, t + dur); lg.gain.value = 380; lfo.connect(lg); lg.connect(f.frequency);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(.3, t + dur * .3); g.gain.setValueAtTime(.3, t + dur * .85); g.gain.exponentialRampToValueAtTime(.001, t + dur + .1);
    s.connect(f); f.connect(g);
    let n = g;
    if (actx.createStereoPanner) {
      const p = actx.createStereoPanner(), pl = actx.createOscillator(), pg = actx.createGain();
      pl.frequency.setValueAtTime(1.5, t); pl.frequency.linearRampToValueAtTime(5, t + dur); pg.gain.value = .7; pl.connect(pg); pg.connect(p.pan); g.connect(p); n = p;
      pl.start(t); pl.stop(t + dur + .2);
    }
    n.connect(out); const w = actx.createGain(); w.gain.value = .3; n.connect(w); w.connect(SX.verb);
    s.start(t); s.stop(t + dur + .2); lfo.start(t); lfo.stop(t + dur + .2);
    const c = sxBus(0, .3);
    sxO(c, 'sine', 1400, t, dur, .045, 300, dur, dur * .3);
    sxO(c, 'sine', 320, t + dur, .25, .3, 70, .2, .01);
    sxO(c, 'triangle', 640, t + dur, .12, .07, 140, .1, .005);
    [77, 81, 84].forEach((m, i) => sxBell(c, mf(m + 12), t + dur + .12 + i * .06, .8, .03));
  }
};
// the sounds of the extras that went off in one round of a resolve (fire() notes them in fxq.x)
function sxPlay(list) {
  if (!list || !list.length || !audioOk()) return;
  sxOut();
  const n = { cat: 0, nip: 0, laser: 0 };
  let first = Infinity;
  for (const e of list) {
    first = Math.min(first, e.d);
    if (e.type === 'cat' && n.cat++ < 5) SFX.cat(e.d / 1000, e.mode ? 'x' : e.dir, !!e.mode);
    else if (e.type === 'nip' && n.nip++ < 4) SFX.nip(e.d / 1000, e.radius || 1);
    else if (e.type === 'laser') (e.hits || []).forEach((h, i) => { if (n.laser++ < 14) SFX.laserHit(h.d / 1000, i, h.pan); });
  }
  if (list.length >= 4) SFX.boom(first / 1000 + .05, Math.min(1.5, .8 + list.length * .05));
}
