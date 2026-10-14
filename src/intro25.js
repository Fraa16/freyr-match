
/* ===================== V25: Freyr's real bed and his morning (art) ===================== */
// his bed: a round plush bed in latte beige, the rim made of fat rolls. Drawn in map units around (0, 0), like the other scenery.
// part: 'back' = shadow, the far half of the rim and the cushion; 'front' = the near half of the rim; 'all' = both
// a rectangle with round corners, seen from the front and above: x to the right, z to the back, y up
const BED = { w: 46, d: 30, r: 17, B: 15, H: 10, Hc: 4, f: .5, N: 26 };
const bedPt = (x, z, y = 0) => [x, -z * BED.f - y];
function bedGeo() {
  if (bedGeo.g) return bedGeo.g;
  const { w, d, r, B, N } = BED, wc = w - B / 2, dc = d - B / 2, rc = r - B / 2, ax = wc - rc, az = dc - rc;
  // the middle line of the rolls, counterclockwise from the front centre: [length, point at s, outward normal at s]
  const segs = [
    [ax, s => [s, -dc], () => [0, -1]],
    [Math.PI / 2 * rc, s => { const a = -Math.PI / 2 + s / rc; return [ax + rc * Math.cos(a), -az + rc * Math.sin(a)]; }, s => { const a = -Math.PI / 2 + s / rc; return [Math.cos(a), Math.sin(a)]; }],
    [2 * az, s => [wc, -az + s], () => [1, 0]],
    [Math.PI / 2 * rc, s => { const a = s / rc; return [ax + rc * Math.cos(a), az + rc * Math.sin(a)]; }, s => { const a = s / rc; return [Math.cos(a), Math.sin(a)]; }],
    [2 * ax, s => [ax - s, dc], () => [0, 1]],
    [Math.PI / 2 * rc, s => { const a = Math.PI / 2 + s / rc; return [-ax + rc * Math.cos(a), az + rc * Math.sin(a)]; }, s => { const a = Math.PI / 2 + s / rc; return [Math.cos(a), Math.sin(a)]; }],
    [2 * az, s => [-wc, az - s], () => [-1, 0]],
    [Math.PI / 2 * rc, s => { const a = Math.PI + s / rc; return [-ax + rc * Math.cos(a), -az + rc * Math.sin(a)]; }, s => { const a = Math.PI + s / rc; return [Math.cos(a), Math.sin(a)]; }],
    [ax, s => [-ax + s, -dc], () => [0, -1]]
  ];
  const L = segs.reduce((a, q) => a + q[0], 0);
  const at = t => { t = ((t % L) + L) % L; for (const [len, P, Nn] of segs) { if (t <= len + 1e-9) return { c: P(t), n: Nn(t) }; t -= len; } const q = segs[segs.length - 1]; return { c: q[1](q[0]), n: q[2](q[0]) }; };
  const ribs = [];
  for (let i = 0; i < N; i++) {
    const t0 = (i - .5) * L / N, t1 = (i + .5) * L / N, tm = i * L / N, m = at(tm);
    ribs.push({ t0, t1, tm, z: m.c[1], nz: m.n[1] });
  }
  return (bedGeo.g = { L, at, ribs });
}
function bedArt(part = 'all') {
  const { B, H, Hc } = BED, { at, ribs } = bedGeo();
  // a point on the outer (k > 0) or inner (k < 0) edge of the rolls, pushed out by 'bulge'
  const E = (t, k, y, bulge = 0) => { const q = at(t); const o = k * (B / 2 + bulge); return bedPt(q.c[0] + q.n[0] * o, q.c[1] + q.n[1] * o, y); };
  const p = q => f1(q[0]) + ' ' + f1(q[1]);
  const ctl = (a, m, b) => [2 * m[0] - (a[0] + b[0]) / 2, 2 * m[1] - (a[1] + b[1]) / 2];
  const edge = (r, k, y, bulge, back) => { const a = E(back ? r.t1 : r.t0, k, y), b = E(back ? r.t0 : r.t1, k, y), m = E(r.tm, k, y, bulge); return ` Q${p(ctl(a, m, b))} ${p(b)}`; };
  const BO = 1.6, BI = 1.4;
  const top = r => `M${p(E(r.t0, 1, H))}${edge(r, 1, H, BO)} L${p(E(r.t1, -1, H))}${edge(r, -1, H, BI, 1)}Z`;
  const wall = r => `M${p(E(r.t0, 1, H))}${edge(r, 1, H, BO)} L${p(E(r.t1, 1, 0))}${edge(r, 1, 0, BO, 1)}Z`;
  const inner = r => `M${p(E(r.t0, -1, H))}${edge(r, -1, H, BI)} L${p(E(r.t1, -1, Hc))}${edge(r, -1, Hc, BI, 1)}Z`;
  const thick = r => { const a = at(r.t0).c, b = at(r.t1).c, A = bedPt(a[0], a[1]), Bq = bedPt(b[0], b[1]); return Math.hypot(A[0] - Bq[0], A[1] - Bq[1]); };
  const crest = r => { const w1 = Math.min(5.6, thick(r) * .62), a = E(r.tm, -.72, H), b = E(r.tm, .8, H, BO * .8);
    return `<path d="M${p(a)} L${p(b)}" stroke="#E8DACA" stroke-width="${f1(w1)}" stroke-linecap="round" opacity=".95"/><path d="M${p(a)} L${p(b)}" stroke="#F7F0E7" stroke-width="${f1(w1 * .4)}" stroke-linecap="round" opacity=".7"/>`; };
  const wallCrest = r => { const a = E(r.tm, 1, H - 2.4, BO), b = E(r.tm, 1, 2, BO); return `<path d="M${p(a)} L${p(b)}" stroke="#D9C5AE" stroke-width="${f1(Math.min(4.8, thick(r) * .55))}" stroke-linecap="round" opacity=".95"/>`; };
  const GROOVE = '#8C735B', LINE = `fill="none" stroke="#4A1F66" stroke-opacity=".55" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"`;
  const back = ribs.filter(r => r.z > 1e-6), front = ribs.filter(r => r.z <= 1e-6);
  const byDepth = list => list.slice().sort((a, b) => b.z - a.z);
  const tops = list => byDepth(list).map(r => `<path d="${top(r)}" fill="#D9C6AD" stroke="${GROOVE}" stroke-width="1.2" stroke-linejoin="round"/>` + crest(r)).join('');
  // the outline: only where the bed meets the world or the hole
  const run = (list, k, y, bulge) => `M${p(E(list[0].t0, k, y))}` + list.map(r => edge(r, k, y, bulge)).join('');
  let s = '';
  if (part !== 'front') {
    const sh = bedPt(0, 0); s += `<ellipse cx="0" cy="${f1(sh[1] + 12)}" rx="${BED.w + 6}" ry="9" fill="#3B1F33" opacity=".13"/>`;
    // the hole: dark first, then the cushion a little lower, then the inside of the far rolls
    const hole = ribs.map((r, i) => (i ? ' L' : 'M') + p(E(r.t0, -1, H))).join('') + 'Z';
    const cush = ribs.map((r, i) => (i ? ' L' : 'M') + p(E(r.t0, -1, Hc))).join('') + 'Z';
    const c = bedPt(0, 0, Hc);
    s += `<path d="${hole}" fill="#A68E76"/><path d="${cush}" fill="#D2BDA3"/>` +
      `<ellipse cx="-4" cy="${f1(c[1] - 3)}" rx="16" ry="4" fill="#DECDB6" opacity=".85"/>` +
      `<path d="M-18 ${f1(c[1] - 1)} q3 -2 6 0 M6 ${f1(c[1] + 1)} q3 -2 6 0 M-4 ${f1(c[1] - 5)} q3 -2 6 0 M16 ${f1(c[1] - 4)} q3 -2 6 0" fill="none" stroke="#B9A189" stroke-width="1.1" stroke-linecap="round"/>`;
    s += byDepth(back.filter(r => r.nz > .05)).map(r => `<path d="${inner(r)}" fill="#B59D84" stroke="${GROOVE}" stroke-width="1.1" stroke-linejoin="round"/>`).join('');
    s += tops(back);
    // back half of the rim: from the right side round the back to the left side, and the far edge of the hole
    const rt = back.slice().sort((a, b) => a.t0 - b.t0);
    s += `<path d="${run(rt, 1, H, BO)} ${run(rt, -1, H, BI)}" ${LINE}/>`;
  }
  if (part !== 'back') {
    const walls = front.filter(r => r.nz < -.05);
    const ft = front.slice().sort((a, b) => ((a.t0 + bedGeo().L / 2) % bedGeo().L) - ((b.t0 + bedGeo().L / 2) % bedGeo().L));
    const wt = walls.slice().sort((a, b) => ((a.t0 + bedGeo().L / 2) % bedGeo().L) - ((b.t0 + bedGeo().L / 2) % bedGeo().L));
    s += walls.slice().sort((a, b) => Math.abs(at(b.tm).c[0]) - Math.abs(at(a.tm).c[0])).map(r => `<path d="${wall(r)}" fill="#C7AF94" stroke="${GROOVE}" stroke-width="1.2" stroke-linejoin="round"/>` + wallCrest(r)).join('');
    s += `<path d="${run(wt, 1, 1.2, BO)}" fill="none" stroke="#7A5A3C" stroke-opacity=".22" stroke-width="3.4" stroke-linecap="round"/>`;
    s += tops(front);
    s += `<path d="${run(ft, -1, H - .2, BI)}" fill="none" stroke="#7A5A3C" stroke-opacity=".18" stroke-width="3" stroke-linecap="round"/>`;
    // the near half: the front edge of the hole, and the bottom of the front wall with its two upright ends
    const R0 = E(bedGeo().L / 4, 1, H), L0 = E(3 * bedGeo().L / 4, 1, H);
    s += `<path d="${run(ft, -1, H, BI)} M${p(L0)} L${p(E(wt[0].t0, 1, 0))}${wt.map(r => edge(r, 1, 0, BO)).join('')} L${p(R0)}" ${LINE}/>`;
  }
  return s;
}

// Freyr's head for the morning: the usual face, plus closed eyes and a big yawn
const MORNING_HEAD = CAT_SVG.replace('<g class="eyes">',
  `<g class="seyes"><path d="M28 57 Q36 63.5 44 57 M56 57 Q64 63.5 72 57" fill="none" stroke-width="3"/></g>` +
  `<g class="m-yawn"><path d="M42 70.5 Q41 88 50 88 Q59 88 58 70.5 Q50 74 42 70.5Z" fill="#C4416E" stroke-width="2.2"/>` +
  `<path d="M45 81.5 Q50 77.5 55 81.5 Q53.5 87 50 87 Q46.5 87 45 81.5Z" fill="#F58FB0"/></g>` +
  '<g class="eyes">');
const HEAD_IN = MORNING_HEAD.replace(/^<svg[^>]*>/, '').replace(/<\/svg>$/, '');

// Freyr curled up in the bed, in map units like the bed. 'mid' sits between the far and the near rim, 'top' lies on the near rim.
const CURL_HEAD = { x: -33, y: -54, s: 58 };
function curlArt(layer) {
  const W = '#fff', L = INK, h = CURL_HEAD;
  if (layer === 'mid') return `<g class="cbody"><path d="M2 -18 Q8 -33 24 -29 Q38 -25 37 -11 Q36 -2 28 1 L6 1Z" fill="${W}" stroke="${L}" stroke-width="1.6" stroke-linejoin="round"/>` +
    `<path d="M20 -26 Q27 -26 31 -21 M25 -17 Q29 -16 31 -13" fill="none" stroke="#E2D3E3" stroke-width="1.2" stroke-linecap="round"/></g>` +
    `<g class="chead"><svg class="catsvg" x="${h.x}" y="${h.y}" width="${h.s}" height="${h.s}" viewBox="0 0 100 100" overflow="visible">${HEAD_IN}</svg></g>`;
  return `<g class="ctail"><path d="M33 -6 Q44 2 38 11 Q33 17 22 15" fill="none" stroke="${L}" stroke-width="9.4" stroke-linecap="round"/><path d="M33 -6 Q44 2 38 11 Q33 17 22 15" fill="none" stroke="${W}" stroke-width="6.2" stroke-linecap="round"/>` +
    `<path d="M39 1 Q41 4 40.5 8 M34 13.5 Q31 15 28 15" fill="none" stroke="#E2D3E3" stroke-width="1.1" stroke-linecap="round"/></g>` +
    `<g class="cpaws"><ellipse cx="-14" cy="1" rx="5.6" ry="3.6" fill="${W}" stroke="${L}" stroke-width="1.5"/><ellipse cx="0" cy="1.5" rx="5.6" ry="3.6" fill="${W}" stroke="${L}" stroke-width="1.5"/>` +
    `<path d="M-16 3 V1.4 M-13 3.3 V1.7 M-2 3.6 V2 M1 3.8 V2.2" stroke="#D3C3D6" stroke-width="1" stroke-linecap="round"/></g>`;
}

// the static bed on the map, where the old basket was
DECO.bed = () => '<g class="mbed">' + bedArt('all') + '</g>';

/* ===================== V25: the intro: Freyr wakes up in his bed, stands up, meows and walks to level 1 ===================== */
// his real meow, from Francesco's video
const MEOW_B64 = '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6Mb2SGLya7VtMbg1O//KEfvaUDohSTWLKrMIuDW2fuFJTQr6Fhp0NgAbeoBRkAAABYHhWd50ZZALgyml9XQiMlFCrMbsUqRigzJpdKr/+1LEOoAKaKc/p6zWkUqU5jAsLLg1GngSVHQQJCpiQnhmIL2nzEeAJS7/0R9b8qEwKQVJBbbCDZWeNpIFh4RZj7OuqCvWAUCIQAAAgAH/xDVJ8FBGGBAvEQaVP0BOlUz9XGgNMltNyVeq4WJtL6vvWVOqZb15J2AvoFGIX1qfvu0jGoCyta6VgPKkO5dzUMBGnkxtlE4eNBAGs4AXo9sMLZAY12+RodqiUpBYrkh8WIDHCVSbxBnKEncVSj9UL18c0e/pPGPgOW1sY9/TP+oUMv/7UsRFgIoglS2ntZgBSRKkWAw8GHJYD+mUxPhxFekLsCrg0NuBAQi7iI1yempAP/VdbTT1LZYICjR6RGcKxNulHqOWvvOWl2GlGPbRGpjYgCMmEYodwKg0AUSKPRZy2EV5He1/jdI8+tZbT1JqooLE9jsKt13tbQjKhcj2DdS7KsABAABAUj338bcRuuAWeO0WqAZc51HA21axujvZyFCXf23CTpfhJUq3OL6ZjBSIZHuGJ8yG2MgRFA8oiHGxK+yn/Pv/1/a71W/3//+q3/cJ//tSxFGACmCXGiyx9EEzECPph5UwLB0bZ0ABTjKKBqONVZwmDl9+ebE2d1RQSWQN+2qsua0UBRiYFZNMYWO7P72TNffKz1j63uXAjlWa1aU8EHFFCxFvtuTAAgL4VUWtMQw2qzGYWpTLWwhkH4k+ocVqICbTqDiSdhSkIoh1PdP7vY4CAoOHouGhKkSR7w2CpO0qbdQxtvrrV/+jqT/V6W93/XWAAINSUL0xMzY+RZ4wbKVkA0WJ9rFmIc6zF1I+yhjmCerER5QVfeobuu9SNCv/+1LEX4EI5JsUDLB0gSkKIiBcPGhFF+ulmAadq7Oje9f0er/f1oLfwTppqZx+WIDW/7mkJKMbJUlud2oUavsXPHfQGlkazNT1L+EngVbkrLPhS1ndFRqyzhEDVrd/0JyyAIRIzIqISiMyiSbZREJwmNJHXGo1aJxxZlqSlntjKz/RfRLGKi/qzlDAgcNBUsKkQELf/pCTMChQkaY5l3/WKGqQlwKKEn1MTUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/7UsR0gwe8SxLAvGPA6wYhyBMk0FVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//tSxJYDyRSS4CSYTRAAADSAAAAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVU=';
let meowBuf = null, meowLoading = false;
function loadMeow() {
  if (!actx || meowBuf || meowLoading) return;
  meowLoading = true;
  try {
    const bin = atob(MEOW_B64), bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const p = actx.decodeAudioData(bytes.buffer, b => { meowBuf = b; }, () => { meowLoading = false; });
    if (p && p.catch) p.catch(() => { meowLoading = false; });
  } catch (e) { meowLoading = false; }
}
function meow(vol = .9) {
  if (!audioOk() || !meowBuf) return false;
  const src = actx.createBufferSource(), g = actx.createGain();
  src.buffer = meowBuf; g.gain.value = vol; src.connect(g); g.connect(master); src.start(actx.currentTime + .02);
  return true;
}
const initAudioPlain25 = initAudio;
initAudio = function () { initAudioPlain25(); loadMeow(); };

const INTRO_VER = '1', INTRO_STOP = { stop: true };
let introRun = null;
function introSeen() { try { return localStorage.getItem('wm-intro') === INTRO_VER; } catch (e) { return false; } }
function startGame() { if (introSeen()) showMap(); else playIntro(); }
// waits that end at once when the intro is stopped
function iWait(run, ms) {
  return new Promise((res, rej) => {
    if (run.dead) return rej(INTRO_STOP);
    run.pending.add(rej);
    const id = setTimeout(() => { run.timers.delete(id); run.pending.delete(rej); res(); }, ms);
    run.timers.add(id);
  });
}
function iTween(run, ms, fn) {
  return new Promise((res, rej) => {
    if (run.dead) return rej(INTRO_STOP);
    run.pending.add(rej);
    const t0 = performance.now();
    const f = now => {
      if (run.dead) return;
      const t = ms > 0 ? Math.min(1, (now - t0) / ms) : 1;
      fn(t);
      if (t < 1) requestAnimationFrame(f); else { run.pending.delete(rej); res(); }
    };
    requestAnimationFrame(f);
  });
}
function iTap(run) {
  return new Promise((res, rej) => {
    if (run.dead) return rej(INTRO_STOP);
    const screen = $('mapScreen');
    const off = () => { screen.removeEventListener('pointerdown', go); document.removeEventListener('keydown', go); run.pending.delete(stop); };
    const go = e => { if (e.type === 'keydown' && e.key !== 'Enter' && e.key !== ' ') return; off(); res(); };
    const stop = x => { off(); rej(x); };
    run.pending.add(stop);
    screen.addEventListener('pointerdown', go); document.addEventListener('keydown', go);
  });
}
const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
const smooth = t => t * t * (3 - 2 * t);
// the camera: map point (fx, fy) in the middle of the screen, zoom z; never shows anything beyond the map
function iCam(run, fx, fy, z) {
  run.cam = { fx, fy, z };
  const map = $('map'), inner = $('mapInner'), k = inner.offsetWidth / 400, W = map.clientWidth, Hs = map.clientHeight, H = mapGeo.H;
  const hw = W / 2 / (z * k), hh = Hs / 2 / (z * k);
  fx = 2 * hw >= 400 ? 200 : Math.max(hw, Math.min(400 - hw, fx));
  fy = 2 * hh >= H ? H / 2 : Math.max(hh, Math.min(H - hh, fy));
  const tx = W / 2 - inner.offsetLeft - z * fx * k, ty = Hs / 2 + map.scrollTop - z * fy * k;
  inner.style.transform = Math.abs(z - 1) < 1e-4 && Math.abs(tx) < .05 && Math.abs(ty) < .05 ? '' : `translate(${tx.toFixed(2)}px,${ty.toFixed(2)}px) scale(${z.toFixed(4)})`;
}
// the view the map has once the intro is over: level 1 at the usual height
function iHome() { const map = $('map'), inner = $('mapInner'), k = inner.offsetWidth / 400; return { x: (map.clientWidth / 2 - inner.offsetLeft) / k, y: (map.clientHeight / 2 + map.scrollTop) / k }; }
function iZoom0() {
  if (REDUCED) return 1;
  const map = $('map'), k = $('mapInner').offsetWidth / 400;
  return Math.max(Math.min(3, map.clientHeight / (210 * k)), Math.min(3.2, map.clientWidth / (400 * k)));
}
const iPlace = (el, x, y) => { el.style.left = (x / 4).toFixed(3) + '%'; el.style.top = (y / mapGeo.H * 100).toFixed(4) + '%'; };
const introSprite = () => `<div class="fwrap"><i class="fshadow"></i><div class="fsprite"><div class="ffront">${FREYR_BODY}<div class="fhead">${CAT_ICON('')}</div></div>${FREYR_BACK}</div></div>`;
// Freyr's feet when he stands in his bed, from the middle of the bed
const BED_FEET = -1.5;
function introScene(geo) {
  const b = geo.pts[0], VB = [-64, -80, 128, 112];
  const box = `left:${((b.x + VB[0]) / 4).toFixed(3)}%;top:${((b.y + VB[1]) / geo.H * 100).toFixed(4)}%;width:${(VB[2] / 4).toFixed(3)}%;aspect-ratio:${VB[2]}/${VB[3]}`;
  const svg = (id, inner) => `<svg class="ibed" id="${id}" style="${box}" viewBox="${VB.join(' ')}" aria-hidden="true">${inner}</svg>`;
  const el = document.createElement('div'); el.id = 'iScene'; el.className = 'asleep shut'; el.setAttribute('aria-hidden', 'true');
  el.innerHTML = svg('iBedBack', `<g filter="url(#mGloss)">${bedArt('back')}</g>${curlArt('mid')}`) +
    `<div class="icat" id="iCat" hidden>${introSprite()}</div>` +
    svg('iBedFront', `<g filter="url(#mGloss)">${bedArt('front')}</g>${curlArt('top')}`) +
    `<span class="zzz disp" id="iZzz">z<b>z</b><i>z</i></span>`;
  $('mapInner').appendChild(el);
  iPlace($('iZzz'), b.x + 18, b.y - 52); iPlace($('iCat'), b.x, b.y + BED_FEET);
  return el;
}
function introCleanup(run) {
  if (run.cleaned) return; run.cleaned = true;
  stopRun(run);
  const map = $('map'), inner = $('mapInner');
  inner.style.transform = ''; inner.style.transformOrigin = ''; inner.style.willChange = ''; map.style.overflowY = ''; map.style.opacity = '';
  $('mapScreen').classList.remove('intro', 'iquiet');
  for (const id of ['iShade', 'iHint', 'iBubble']) { const e = $(id); if (e) e.remove(); }
  removeEventListener('resize', run.onResize);
  if (run.anim) { mapAnimating = false; mapSkip = false; }
  if (introRun === run) introRun = null;
}
function stopRun(run) {
  if (run.dead) return; run.dead = true;
  for (const id of run.timers) clearTimeout(id);
  const p = [...run.pending]; run.pending.clear(); run.timers.clear();
  for (const r of p) r(INTRO_STOP);
}
function introStop() { if (introRun) introCleanup(introRun); }
const hideMapPlain25 = hideMap;
hideMap = function () { introStop(); return hideMapPlain25(); };
const showMapPlain25 = showMap;
showMap = function (prog) { if (introRun && !introRun.self) introStop(); return showMapPlain25(prog); };

async function playIntro() {
  if (introRun) return;
  const run = introRun = { dead: false, timers: new Set(), pending: new Set(), cleaned: false, self: true, anim: false, cam: null };
  let done = false;
  try {
    for (const id of ['setOv', 'livesOv', 'chestOv', 'kitOv']) { const o = $(id); if (o) o.classList.remove('show'); }
    showMap(); run.self = false;
    // the map as on the very first day: level 1 still closed, no paw prints yet, Freyr asleep in his bed
    const ml = maxLevel; maxLevel = 0;
    try { renderMap(); } finally { maxLevel = ml; }
    mapAnimating = true; run.anim = true; mapSkip = false;
    const geo = mapGeo, b = geo.pts[0], seg = geo.seg(0), inner = $('mapInner'), map = $('map'), screen = $('mapScreen');
    const bedDeco = inner.querySelector('.mbed'); if (bedDeco) bedDeco.parentNode.style.visibility = 'hidden';
    $('mFreyr').style.visibility = 'hidden';
    const paws = inner.querySelector('.mapsvg g[fill="#FF5FA8"]');
    if (paws) paws.insertAdjacentHTML('afterbegin', pawsOn(seg, 'pz'));
    const scene = introScene(geo), cat = $('iCat'), spr = cat.querySelector('.fsprite');
    screen.classList.add('intro', 'iquiet');
    screen.insertAdjacentHTML('beforeend', '<div class="ishade" id="iShade"></div><button class="ihint" id="iHint" hidden>Tippe, um Freyr zu wecken</button><div class="ibubble" id="iBubble" aria-live="polite"></div>');
    map.style.overflowY = 'hidden'; inner.style.transformOrigin = '0 0'; inner.style.willChange = 'transform';
    // where the camera ends up: the normal view of level 1 (kept right when the phone is turned)
    let home = null; const setHome = () => { scrollMapTo(1, .62); home = iHome(); };
    setHome();
    const Z0 = iZoom0();
    run.onResize = () => { setHome(); if (run.cam) iCam(run, run.cam.fx, run.cam.fy, run.cam.z); };
    addEventListener('resize', run.onResize);
    let F = { x: b.x + 4, y: b.y - 22 };
    iCam(run, F.x, F.y, Z0);

    // asleep until someone taps
    const hint = $('iHint');
    const showHint = setTimeout(() => { if (!run.dead) { hint.hidden = false; void hint.offsetWidth; hint.classList.add('show'); } }, 1100);
    run.timers.add(showHint);
    await iTap(run);
    clearTimeout(showHint);
    initAudio(); loadMeow();
    hint.classList.remove('show'); setTimeout(() => { hint.hidden = true; }, 400);
    $('iShade').classList.add('off');
    scene.classList.remove('asleep'); $('iZzz').classList.add('gone');

    // an ear twitch, eyes open, a blink, a big yawn, a stretch
    scene.classList.add('twitch'); await iWait(run, 480); scene.classList.remove('twitch');
    scene.classList.remove('shut'); scene.classList.add('lift'); await iWait(run, 420);
    scene.classList.add('shut'); await iWait(run, 120); scene.classList.remove('shut'); await iWait(run, 320);
    scene.classList.add('shut', 'yawn'); await iWait(run, 1050); scene.classList.remove('yawn', 'shut'); await iWait(run, 220);
    scene.classList.add('stretch'); await iWait(run, 640); scene.classList.remove('stretch'); await iWait(run, 260);

    // he stands up in his bed
    scene.classList.add('up'); cat.hidden = false; cat.classList.add('rise');
    if (audioOk()) { const t = actx.currentTime + .02; tone(392, t, .12, 'triangle', .05); tone(587.33, t + .09, .18, 'triangle', .05); }
    const F1 = { x: b.x + 2, y: b.y - 36 };
    await iTween(run, 600, t => { const e = smooth(t); iCam(run, F.x + (F1.x - F.x) * e, F.y + (F1.y - F.y) * e, Z0); });
    F = F1; cat.classList.remove('rise');
    await iWait(run, 150);

    // "Miau!": his real meow
    cat.classList.add('meow', 'eat'); meow(); buzz(25);
    const bub = $('iBubble');
    bub.innerHTML = '<b>Miau!</b><span>Ich hab Hunger!</span>';
    const place = () => {
      const h = cat.querySelector('.fhead').getBoundingClientRect(), sb = screen.getBoundingClientRect();
      bub.style.left = (h.left + h.width / 2 - sb.left).toFixed(1) + 'px'; bub.style.top = (h.top - sb.top - 10).toFixed(1) + 'px';
    };
    place(); bub.classList.add('show');
    await iWait(run, 820); cat.classList.remove('eat');
    // the music comes in once the meow has been heard
    startMusic(); duck(false);
    await iWait(run, 1150); bub.classList.remove('show'); bub.classList.add('hide'); cat.classList.remove('meow');
    await iWait(run, 260);

    // he turns round and hops out of the bed onto the path
    spr.classList.add('back'); await iWait(run, 260);
    const N = 48, acc = [0]; let p = seg.a;
    for (let i = 1; i <= N; i++) { const q = bez(seg, i / N); acc.push(acc[i - 1] + Math.hypot(q.x - p.x, q.y - p.y)); p = q; }
    let i0 = 1; while (acc[i0] < 46) i0++;
    const t46 = (i0 - 1 + (46 - acc[i0 - 1]) / (acc[i0] - acc[i0 - 1])) / N, P46 = bez(seg, t46);
    const A = { x: b.x, y: b.y + BED_FEET };
    cat.classList.add('jump');
    if (audioOk()) { const t = actx.currentTime + .01; tone(523.25, t, .1, 'triangle', .045); tone(783.99, t + .07, .14, 'triangle', .04); }
    await iTween(run, REDUCED ? 1 : 520, t => { const e = ease(t); iPlace(cat, A.x + (P46.x - A.x) * e, A.y + (P46.y - A.y) * e - 26 * 4 * t * (1 - t)); });
    cat.classList.remove('jump'); void cat.offsetWidth; cat.classList.add('land');
    await iWait(run, 200); cat.classList.remove('land');

    // and walks up to level 1 while the camera lets go
    spr.classList.add('walk'); screen.classList.remove('iquiet');
    const pz = [...inner.querySelectorAll('.pz')];
    const len = acc[N] - 46, dur = REDUCED ? 600 : Math.max(1500, Math.min(2600, len * 12));
    const Fw = { ...F };
    let lastStep = 0, n = 0;
    await iTween(run, dur, t => {
      const e = ease(t), tt = t46 + (1 - t46) * e, q = bez(seg, tt);
      const lift = 14 * Math.max(0, (e - .86) / .14);
      iPlace(cat, q.x, q.y); cat.style.transform = lift ? `translateY(${(-lift).toFixed(1)}px)` : '';
      for (const el of pz) if (+el.dataset.t <= tt) el.classList.add('show');
      const c = smooth(Math.min(1, t / .9)), f0 = smooth(Math.min(1, t / .25));
      const fx = Fw.x + (q.x - Fw.x) * f0, fy = Fw.y + (q.y - 30 - Fw.y) * f0;
      iCam(run, fx + (home.x - fx) * c, fy + (home.y - fy) * c, Z0 * Math.pow(1 / Z0, c));
      const now = performance.now();
      if (now - lastStep > 180 && t < .97) { lastStep = now; if (audioOk()) tone(n++ % 2 ? 620 : 540, actx.currentTime + .01, .06, 'triangle', .035); }
    });
    pz.forEach(el => el.classList.add('show'));
    iCam(run, home.x, home.y, 1);

    // level 1 opens
    spr.classList.remove('walk', 'back'); void spr.offsetWidth; spr.classList.add('hop'); chime(4);
    const nn = nodeEl(1);
    if (nn) { nn.classList.remove('lock'); nn.classList.add('cur', 'unlock'); nn.setAttribute('aria-label', 'Level 1 spielen'); burstAt(nn, 26, 1.6); }
    sparkle(); buzz(30);
    screen.classList.remove('intro');
    await iWait(run, 640);
    try { localStorage.setItem('wm-intro', INTRO_VER); } catch (e) {}
    done = true;
  } catch (e) {
    if (e !== INTRO_STOP) console.error(e);
  } finally {
    introCleanup(run);
  }
  if (!done || !onMap) return;
  // back to the real map: the same picture for a new player, the player's own level for everyone else
  const map = $('map'), jump = maxLevel > 1;
  if (jump && !REDUCED) { map.style.transition = 'opacity .22s'; map.style.opacity = '0'; await new Promise(r => setTimeout(r, 230)); }
  if (!onMap) { map.style.opacity = ''; map.style.transition = ''; return; }
  showMap();
  if (jump) { void map.offsetWidth; map.style.opacity = ''; setTimeout(() => { map.style.transition = ''; }, 300); }
  setTimeout(() => {
    if (onMap && !mapAnimating && !introRun && lives > 0 && !document.querySelector('.overlay.show')) openLevel(maxLevel);
  }, jump ? 650 : 420);
}

// watch it again: from Freyr's card on the map
(function () {
  const done = $('setDone'); if (!done) return;
  const b = document.createElement('button');
  b.className = 'btn soft small'; b.id = 'setIntro'; b.type = 'button'; b.textContent = 'Intro nochmal ansehen';
  done.after(b);
  b.onclick = () => { if (!onMap || introRun) return; closeSettings(); playIntro(); };
  const openPlain = openSettings;
  openSettings = function () { const r = openPlain.apply(this, arguments); b.hidden = !onMap; return r; };
  $('mFace').onclick = openSettings;
})();
