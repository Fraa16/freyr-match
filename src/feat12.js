
/* ===================== round 3: gifts, cucumbers, alarm clocks, orders, the magic feather, turbo robot, super pounce ===================== */
const COMBO_SVG = `<svg viewBox="0 0 100 100"><circle cx="36" cy="58" r="24" fill="url(#gPink)" ${OL('#9E0C57')}/><circle cx="64" cy="42" r="24" fill="url(#gGreen)" ${OL('#155F20')}/>` +
  `<path d="M64 30 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3Z M36 46 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3Z" fill="#fff"/>` +
  `<path d="M57 4 L45 22 H54 L48 38 L64 16 H55Z" fill="url(#gGold)" stroke="#8A4A00" stroke-width="2.4" stroke-linejoin="round"/></svg>`;
// an order: a note with a paw stamp and a pencil
const ORDER_SVG = `<svg viewBox="0 0 100 100"><g ${OL('#7A5AA8')}><path d="M20 10 H72 L82 20 V90 H20Z" fill="#fff"/><path d="M72 10 V20 H82" fill="#EDE4FA"/></g>` +
  `<g stroke="#C9B6E8" stroke-width="3.4" stroke-linecap="round"><path d="M30 30 H70 M30 42 H66 M30 54 H58"/></g>` +
  `<g fill="url(#gPink)"><ellipse cx="44" cy="74" rx="8" ry="6.6"/><ellipse cx="34" cy="66" rx="3.4" ry="4.2"/><ellipse cx="41" cy="60.5" rx="3.4" ry="4.2"/><ellipse cx="48.5" cy="60.5" rx="3.4" ry="4.2"/><ellipse cx="55" cy="66" rx="3.4" ry="4.2"/></g>` +
  `<g transform="rotate(38 76 66)"><rect x="70" y="40" width="11" height="40" rx="2.5" fill="url(#gYellow)" ${OL('#8A4A00')}/><path d="M70 80 L75.5 92 L81 80Z" fill="#FFE3C2" ${OL('#8A4A00')}/></g></svg>`;
const VAC_TURBO_SVG = VAC_ICON.replace('</svg>', `<path d="M128 0 L92 52 H118 L100 104 L160 36 H130Z" fill="url(#gGold)" stroke="#8A4A00" stroke-width="7" stroke-linejoin="round"/></svg>`);
const MAKE_ICON = w => w === 'cat' ? CAT_SVG : w === 'combo' ? COMBO_SVG : iconFor({ type: w, dir: 'h' });
const MAKE_NAME = { cat: ['Flitzekatze', 'Flitzekatzen'], laser: ['Laserpunkt', 'Laserpunkte'], nip: ['Katzenminze', 'Katzenminzen'], bowl: ['Festmahl-Napf', 'Festmahl-Näpfe'], combo: ['Kombi', 'Kombis'] };
const EXTRA_A = { cat: 'eine Flitzekatze', laser: 'ein Laserpunkt', nip: 'eine Katzenminze', bowl: 'ein Festmahl-Napf' };
const clockHTML = n => `<span class="clk${n <= 3 ? ' low' : ''}">${CLOCK_BADGE}<b>${n}</b></span>`;
const isHit = x => !!x && (x.type === 'box' || x.type === 'wet' || x.type === 'gift' || x.type === 'cuke');
let clockRang = false, toldCuke = false, toldGift = false, toldClock = false, toldFeather = false;

/* ---------- gifts: one hit opens them, and an extra jumps out ---------- */
function giftKind() {
  const pool = [['cat', 38], ['laser', 30], ['nip', 24], ['bowl', 8]].filter(([k]) => isUnlocked(k));
  if (!pool.length) return 'cat';
  let t = Math.random() * pool.reduce((a, [, w]) => a + w, 0);
  for (const [k, w] of pool) { if ((t -= w) < 0) return k; }
  return pool[0][0];
}

/* ---------- cucumbers: after every move each one hops onto a neighbouring treat ---------- */
function hopSound() { sweep(300, 900, 0, .12, 'triangle', .06); sweep(900, 500, .1, .1, 'sine', .04); }
async function cukeStep() {
  const cs = [];
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (grid[r][c] && grid[r][c].type === 'cuke') cs.push([r, c]);
  if (!cs.length) return;
  const taken = new Set(); let hops = 0;
  for (const [r, c] of shuffleList(cs)) {
    const opts = shuffleList(D4.map(([dr, dc]) => [r + dr, c + dc]).filter(([rr, cc]) => {
      const y = inB(rr, cc) && mask[rr][cc] && grid[rr][cc];
      return !!y && !taken.has(rr * N + cc) && isNormal(y.type) && !y.locked;
    }));
    if (!opts.length) continue;
    const [rr, cc] = opts[0], cu = grid[r][c], t = grid[rr][cc];
    grid[rr][cc] = cu; grid[r][c] = t; taken.add(rr * N + cc); hops++;
    const el = els.get(cu.id);
    if (el) { el.style.transition = 'none'; el.style.setProperty('--hx', ((c - cc) * 100) + '%'); el.style.setProperty('--hy', ((r - rr) * 100) + '%'); }
    place(cu, rr, cc); place(t, r, c);
    if (el) { el.classList.remove('hop'); void el.offsetWidth; el.classList.add('hop'); setTimeout(() => { el.style.transition = ''; el.classList.remove('hop'); }, 420); }
  }
  if (!hops) return;
  hopSound();
  if (!toldCuke) { toldCuke = true; say('Hilfe, die Gurken hüpfen! Mach ein Match direkt daneben, dann sind sie weg.'); }
  else if (Math.random() < .25) say(['Iiih, Gurken!', catName + ' macht einen Buckel.', 'Die Gurke grinst so komisch.', catName + ' springt erschrocken zur Seite.'][Math.floor(Math.random() * 4)]);
  await sleep(430);
  // a hop can line up three treats
  await resolve(null, null);
}

/* ---------- alarm clocks: they tick down after every move; when one rings, the level is lost ---------- */
function drawClock(x) {
  const el = els.get(x.id); if (!el) return;
  const b = el.querySelector('.clk');
  if (!b) { if (x.clock > 0 || x.clock === 0) el.insertAdjacentHTML('beforeend', clockHTML(x.clock)); return; }
  b.classList.toggle('low', x.clock <= 3); b.querySelector('b').textContent = x.clock;
}
function tick() { sweep(2200, 2100, 0, .03, 'square', .02); }
function clockTick() {
  let rang = false, low = false;
  for (const row of grid) for (const x of row) {
    if (!x || !(x.clock > 0)) continue;
    x.clock--; drawClock(x);
    if (x.clock <= 0) rang = true; else if (x.clock <= 3) low = true;
  }
  if (low && !rang) { tick(); if (!toldClock) { toldClock = true; say('Der Wecker klingelt gleich! Friss das Leckerli mit dem Wecker.'); } }
  return rang;
}
function alarm() { if (!audioOk()) return; const t = actx.currentTime + .01; for (let i = 0; i < 10; i++) { tone(1568, t + i * .09, .05, 'square', .05); tone(2093, t + i * .09 + .045, .04, 'square', .04); } }
async function clockRing() {
  clockRang = true;
  for (const row of grid) for (const x of row) if (x && x.clock === 0) { const el = els.get(x.id); if (el) { el.classList.remove('ring'); void el.offsetWidth; el.classList.add('ring'); } }
  alarm(); buzz([80, 40, 80, 40, 80]); shake();
  callout('Rrriiing!', 'Der Wecker klingelt');
  say('Oh nein, der Wecker! Herrchen ist wach, die Nascherei ist vorbei.');
  await sleep(1300);
  return showEnd(false);
}
// a rescue after the alarm also sets the clocks back
function resetClocks() {
  for (const row of grid) for (const x of row) if (x && x.clock != null && x.clock < 5) { x.clock = 5; drawClock(x); const el = els.get(x.id); if (el) el.classList.remove('ring'); }
  clockRang = false;
}

/* ---------- the magic feather: any treat becomes a Flitzekatze ---------- */
async function featherAt(r, c) {
  const old = grid[r][c], k = r * N + c, X = goalCtx();
  let h = 0, v = 0;
  for (let i = 0; i < N; i++) { h += cellWorth(r * N + i, X); v += cellWorth(i * N + c, X); }
  const sp = mk('cat'); sp.dir = v > h ? 'v' : 'h';
  stampFx(k, FEATHER_TOOL); await sleep(260);
  const oe = els.get(old.id); if (oe) oe.remove(); els.delete(old.id);
  grid[r][c] = sp; const el = tileEl(sp); place(sp, r, c); el.classList.add('spawn');
  const [x, y] = cellXY(k); burst(x, y, 18, 1.3, ['#FF9CC6', '#FFD6EA', '#ffffff', '#FFE14D'], 'star'); sparkle(); extraSound('cat');
  callout('Zauberfeder!', 'Eine Flitzekatze');
  if (!toldFeather) { toldFeather = true; say('Hokuspokus, eine Flitzekatze! Tausch sie, dann flitzt sie los.'); }
  await sleep(320);
}

/* ---------- the lessons and level cards for the new things ---------- */
Object.assign(INTRO, {
  box3: () => [BOX_SVG(3), 'Neu: Kartontürme', 'Dreifach verklebt, mit Goldband. Die brauchen drei Treffer.'],
  order: () => [ORDER_SVG, 'Neu: Bestellungen', 'Auf der Liste stehen Extras. Bau sie aus passenden Formen, dann ist die Bestellung erfüllt.'],
  gift: () => [GIFT_SVG, 'Neu: Geschenkboxen', 'Ein Match direkt daneben packt sie aus. In jeder steckt ein Extra!'],
  cukes: () => [CUKE_SVG, 'Neu: Gurken', catName + ' hat schreckliche Angst vor Gurken. Sie hüpfen nach jedem Zug weiter. Ein Match direkt daneben verjagt sie.'],
  clock: () => [CLOCK_ICON, 'Neu: Wecker', 'Jeder Wecker zählt bei jedem Zug runter. Friss das Leckerli, bevor er klingelt, sonst wacht Herrchen auf und das Level ist verloren.'],
  feather: () => [FEATHER_TOOL, 'Neu: Zauberfeder', 'Sie verwandelt ein Leckerli in eine Flitzekatze und kostet keinen Zug. 2 Stück gibt es gratis.'],
  turbo: () => [VAC_TURBO_SVG, 'Neu: Turbo-Roboter', 'Der Staubsauger hat aufgerüstet! Er fährt jetzt zwei Felder pro Zug.'],
  superpounce: () => [CAT_ICON(), 'Neu: Super-Sprung', catName + ' ist stärker geworden. Sein Sprung räumt jetzt Reihe, Spalte und alles rundherum ab.'],
  goldrush: () => [GOLDPAW_SVG, 'Goldrausch', 'Heute glänzt es überall. Friss so viele goldene Leckerlis, wie auf der Liste stehen.']
});
const orderShape = () => { const g = goals.find(x => x.kind === 'make' && x.left > 0); return g && SHAPES[g.what] ? g.what : 'cat'; };
const orderText = () => { const g = goals.find(x => x.kind === 'make'); return g ? 'Bau ' + g.n + ' ' + MAKE_NAME[g.what][g.n === 1 ? 0 : 1] + '!' : ''; };
Object.assign(COACH, {
  box3: [{ plant: 'three', want: 'box3' }, { move: () => 'Kartontürme brauchen drei Treffer. Fang an!' }],
  order: [{ info: 'goals', text: () => 'Eine Bestellung! Hier zählt, was du baust. ' + orderText() }, { plant: orderShape }, { move: d => 'Wisch es ' + d + '. Das ist das erste Extra für die Liste!' }],
  gift: [{ plant: 'three', want: 'gift' }, { move: () => 'Ein Match direkt daneben packt das Geschenk aus!' }, { use: 'any', text: x => 'Da war ' + EXTRA_A[x.type] + ' drin! Tausch ' + ({ cat: 'sie', nip: 'sie' }[x.type] || 'ihn') + ' gleich mit einem Nachbarn.' }],
  cukes: [{ info: 'cuke', text: () => 'Iiih, eine Gurke! Gurken hüpfen nach jedem Zug weiter.' }, { plant: 'three', want: 'cuke' }, { move: () => 'Ein Match direkt daneben verjagt sie!' }],
  clock: [{ info: 'clock', text: () => 'Ein Wecker! Er zählt bei jedem Zug runter. Klingelt er, ist das Level verloren.' }, { plant: 'three', want: 'clock' }, { move: () => 'Friss das Leckerli mit dem Wecker, dann ist er aus.' }],
  feather: [{ tool: 'feather', text: () => 'Tipp auf die Zauberfeder.' }, { cell: 'feather', text: () => 'Und jetzt auf dieses Leckerli. Es wird zur Flitzekatze!' },
    { use: 'cat', text: x => 'Jetzt tausch sie. Sie flitzt durch die ganze ' + (x.dir === 'v' ? 'Spalte!' : 'Reihe!') }],
  turbo: [{ info: 'boss', text: () => 'Achtung, Turbo! Dieser Roboter fährt zwei Felder pro Zug.' }, { plant: 'three', want: 'boss' }, { move: () => 'Matches direkt neben ihm leeren seinen Akku. Schnell!' }],
  superpounce: [{ purr: 0 }, { info: 'purr', text: () => catName + ' ist stärker geworden! Sein Sprung räumt jetzt auch alles rundherum ab.' }, { mascot: () => 'Tipp ' + catName + ' an.' },
    { cell: 'pounce', text: () => 'Und jetzt auf dieses Feld. Super-Sprung!' }],
  goldrush: [{ info: 'goals', text: () => 'Goldrausch! Friss so viele goldene Leckerlis, wie hier stehen.' }, { info: 'gold', text: () => 'Da ist schon eins. Goldene Leckerlis laden auch die Schnurr-Power auf.' }]
});
Object.assign(WANT, {
  box3: P => P.hit.some(([r, c]) => nearType(r, c, y => y.type === 'box' && y.hp > 2)),
  gift: P => P.hit.some(([r, c]) => nearType(r, c, y => y.type === 'gift')),
  cuke: P => P.hit.some(([r, c]) => nearType(r, c, y => y.type === 'cuke')),
  clock: P => P.S.some(([r, c]) => grid[r][c].clock > 0)
});
Object.assign(SHOW, {
  box3: (r, c) => grid[r][c] && grid[r][c].type === 'box' && grid[r][c].hp > 2,
  gift: (r, c) => grid[r][c] && grid[r][c].type === 'gift',
  cuke: (r, c) => grid[r][c] && grid[r][c].type === 'cuke'
});
const TINFO = { cuke: x => x.type === 'cuke', clock: x => x.clock > 0, gift: x => x.type === 'gift' };
TOOL_SVG.feather = FEATHER_TOOL;
// special levels that mix things up
Object.assign(INTRO, {
  mix_cukecover: () => [CUKE_SVG, 'Gurken auf der Decke', 'Die Gurken haben sich auf ' + catName + 's Kuscheldecke geschlichen. Breite die Decke aus und verjag sie!'],
  mix_clockbox: () => [CLOCK_ICON, 'Wecker im Karton', 'Jemand hat Wecker zwischen die Kartontürme gestellt. Reiß die Kartons auf, bevor es klingelt!'],
  mix_giftparty: () => [GIFT_SVG, 'Geschenke-Party', 'Lauter Geschenke! Pack sie aus und bau dazu zwei Katzenminzen.'],
  mix_cukeclock: () => [CUKE_SVG, 'Gurken-Alarm', 'Gurken und Wecker auf einmal. Verjag die Gurken und lass keinen Wecker klingeln!'],
  mix_hundred: () => [VAC_TURBO_SVG, 'Level 100!', 'Zum Jubiläum kommt der Turbo-Roboter vorbei, mit Geschenken im Gepäck. Leer seinen Akku!'],
  mix_goldorder: () => [GOLDPAW_SVG, 'Goldene Bestellung', 'Goldrausch und Bestellung in einem Level: Friss Gold und bau die Extras auf der Liste.'],
  mix_wetcukes: () => [WET_SVG, 'Nassfutter-Party', 'Nassfutter und Gurken, ' + catName + 's schlimmster Tag! Räum alles weg.'],
  mix_bellgifts: () => [BELL_SVG, 'Glöckchenregen', 'Sechs Glöckchen wollen nach unten. Die Geschenke helfen dir dabei.'],
  mix_robopicnic: () => [VAC_TURBO_SVG, 'Robo-Picknick', 'Der Turbo-Roboter crasht das Picknick! Breite die Decke aus, räum das Nassfutter weg und leer seinen Akku.'],
  mix_boxmountain: () => [BOX_SVG(3), 'Kartonberg', 'Ein ganzer Berg aus Kartontürmen. Laserpunkte helfen beim Abtragen.'],
  mix_clockmilk: () => [CLOCK_ICON, 'Morgenwecker', 'Frühstück mit doppelten Pfützen, aber die Wecker ticken schon.'],
  mix_cukeharvest: () => [CUKE_SVG, 'Gurkenernte', 'Acht Gurken und dazwischen Gold. ' + catName + ' ist hin- und hergerissen.'],
  mix_bigorder: () => [ORDER_SVG, 'Bestellung XXL', 'Die größte Bestellung bisher: je zwei Katzenminzen, Laserpunkte und Flitzekatzen.'],
  mix_turboclean: () => [VAC_TURBO_SVG, 'Turbo-Hausputz', 'Der Turbo-Roboter putzt, und das Nassfutter bleibt liegen. Halt ihn auf!'],
  mix_allgold: () => [GOLDPAW_SVG, 'Alles Gold', 'Acht goldene Leckerlis, und die Wolle hält alles fest.'],
  mix_starrain: () => [GIFT_SVG, 'Sternenregen', 'Geschenke, Gold und eine Bestellung. Ein Level wie ein Feuerwerk!'],
  mix_rehearsal: () => [CLOCK_ICON, 'Generalprobe', 'Geschenke, Gurken und Wecker: die Probe fürs große Finale.'],
  mix_finale: () => [VAC_TURBO_SVG, 'Das große Finale', 'Alles auf einmal, und der Turbo-Roboter mittendrin. Zeig ihm, was du gelernt hast!']
});

/* ===================== level 61: Freyr is from Trabzon, and a huge Trabzonspor fan ===================== */
const KITCOL = ['#8C1D40', '#B8325E', '#6CC4F0', '#A9DDF8', '#ffffff'];
// the jersey under Freyr's chin: claret with a sky-blue collar and the 61
ACC.trikot = `<g stroke="${INK}" stroke-width="3" stroke-linejoin="round"><path d="M15 101 Q17 86 33 83 L50 95 L67 83 Q83 86 85 101Z" fill="#8C1D40"/></g>` +
  `<path d="M33 83.5 L50 95 L67 83.5" fill="none" stroke="#6CC4F0" stroke-width="5" stroke-linejoin="round"/>` +
  `<path d="M22 90 Q19 95 19 101 M78 90 Q81 95 81 101" fill="none" stroke="#6CC4F0" stroke-width="5"/>` +
  `<text x="64" y="99.6" text-anchor="middle" font-family="'Lilita One',Nunito,sans-serif" font-size="9.5" fill="#fff">61</text>`;
OUTFITS.push({ id: 'trikot', name: 'Trikot', price: 0, level: 61 });
// on the map: the jersey on Freyr's body, and the 61 on his back when he walks away
const FREYR_BODY_KIT = FREYR_BODY.replace(`<ellipse cx="50" cy="34" rx="28" ry="21" fill="#fff" stroke="${INK}" stroke-width="3"/>`,
  `<ellipse cx="50" cy="34" rx="28" ry="21" fill="#8C1D40" stroke="${INK}" stroke-width="3"/><path d="M25 26 Q22.5 34 26 44 M75 26 Q77.5 34 74 44" fill="none" stroke="#6CC4F0" stroke-width="5" stroke-linecap="round"/>` +
  `<text x="50" y="45" text-anchor="middle" font-family="'Lilita One',Nunito,sans-serif" font-size="14" fill="#fff" stroke="#3A0716" stroke-width=".8">61</text>`);
const FREYR_BACK_KIT = FREYR_BACK.replace(`<ellipse cx="50" cy="98" rx="28" ry="21" fill="#fff"/>`,
  `<ellipse cx="50" cy="98" rx="28" ry="21" fill="#8C1D40"/><path d="M25 90 Q22.5 98 26 108 M75 90 Q77.5 98 74 108" fill="none" stroke="#6CC4F0" stroke-width="5"/>` +
  `<text x="50" y="114" text-anchor="middle" font-family="'Lilita One',Nunito,sans-serif" font-size="16" fill="#fff" stroke="#3A0716" stroke-width=".8">61</text>`);
const freyrInner = () => `<div class="ffront">${wear === 'trikot' ? FREYR_BODY_KIT : FREYR_BODY}<div class="fhead">${CAT_ICON()}</div></div>${wear === 'trikot' ? FREYR_BACK_KIT : FREYR_BACK}`;
let kitNew = false;
document.body.insertAdjacentHTML('beforeend', '<div class="overlay" id="kitOv"><div class="card sticker" id="kitCard" role="dialog" aria-modal="true" aria-labelledby="kitTitle">' +
  '<h2 class="bigtitle disp" id="kitTitle">Trikot freigeschaltet!</h2><div class="kitart" id="kitArt"></div><p id="kitText"></p>' +
  '<div class="btncol"><button class="btn big" id="kitWear">Anziehen</button><button class="btn soft" id="kitLater">Später</button></div></div></div>');
function kitConfetti(n) {
  for (let i = 0; i < n; i++) addPart({ x: Math.random() * innerWidth, y: -20 - Math.random() * innerHeight * .4, vx: (Math.random() - .5) * 2.5, vy: 2 + Math.random() * 3, g: .05, life: 1,
    decay: .003 + Math.random() * .003, size: 7 + Math.random() * 7, rot: Math.random() * 6, vr: (Math.random() - .5) * .25, color: KITCOL[Math.floor(Math.random() * KITCOL.length)], shape: Math.random() < .5 ? 'heart' : 'rect' });
}
function showKit() {
  return new Promise(res => {
    const ov = $('kitOv'), card = $('kitCard');
    $('kitArt').innerHTML = CAT_ICON('trikot');
    $('kitText').textContent = catName + ' hat sein Bordo-Mavi-Trikot! Für Trabzon, mit der 61 auf dem Rücken. Du findest es auch bei den Outfits.';
    const done = on => { ov.classList.remove('show'); if (on) { wear = 'trikot'; saveJar(); refreshCats(); sparkle(); say(catName + ' trägt jetzt Bordo-Mavi. Bereit für das nächste Spiel!'); } res(); };
    $('kitWear').onclick = () => done(true); $('kitLater').onclick = () => done(false);
    card.classList.remove('pop-in'); void card.offsetWidth; card.classList.add('pop-in');
    ov.classList.add('show'); kitConfetti(90); fanfare(); buzz([40, 60, 40]);
  });
}
Object.assign(INTRO, {
  trabzon: () => [CAT_ICON('trikot'), 'Ein Level für Trabzon!', catName + ' kommt aus Trabzon und ist riesiger Trabzonspor-Fan. Heute gibt es Hamsi vom Schwarzen Meer: Friss 61 Stück, dann bekommt ' + catName + ' sein Bordo-Mavi-Trikot!']
});

/* ---------- many goals: smaller chips first, then two rows, so every goal stays visible ---------- */
function fitGoals() {
  const box = $('goals'), hb = box && box.closest('.goalsbox');
  if (!hb) return;
  box.classList.remove('gtight', 'grows'); hb.classList.remove('grows'); box.style.maxWidth = '';
  if (goals.length < 4 || !box.clientWidth) return;
  const over = () => box.scrollWidth > box.clientWidth + 1;
  if (!over()) return;
  box.classList.add('gtight');
  if (!over()) return;
  box.classList.remove('gtight'); box.classList.add('grows'); hb.classList.add('grows');
  box.style.maxWidth = (Math.ceil(goals.length / 2) * 22) + 'px';
}
const drawGoalsPlain = drawGoals;
drawGoals = function () { drawGoalsPlain(); fitGoals(); requestAnimationFrame(fitGoals); };
addEventListener('resize', () => { if (goals && goals.length >= 4) fitGoals(); });

/* ---------- extras: a bigger show every time one goes off ---------- */
const pctPos = k => ({ x: (k % N + .5) * STEP, y: ((k / N | 0) + .5) * STEP });
const cellDist = (a, b) => Math.hypot((a / N | 0) - (b / N | 0), a % N - b % N);
function fxEl(cls, css, ms, d, html) {
  if (REDUCED) return;
  later(d, () => {
    const e = document.createElement('div'); e.className = cls; if (html) e.innerHTML = html;
    Object.assign(e.style, css); boardEl.appendChild(e); setTimeout(() => e.remove(), ms);
  });
}
// the extra itself flares up as it goes off
function xflash(cell, k, d) {
  const p = pctPos(k);
  fxEl('xflash ' + cell.type, { left: p.x + '%', top: p.y + '%', width: STEP + '%', height: STEP + '%' }, 560, d, iconFor(cell));
}
// a glowing line from one cell to another
function beam(k1, k2, cls, d, ms) {
  const a = pctPos(k1), b = pctPos(k2), len = Math.hypot(b.x - a.x, b.y - a.y), ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
  fxEl(cls, { left: a.x + '%', top: a.y + '%', width: len + '%', transform: `rotate(${ang.toFixed(1)}deg)` }, ms, d, '<i></i>');
}
function bigShake() {
  if (REDUCED) return;
  const w = $('boardwrap'); w.classList.remove('shake', 'shake2'); void w.offsetWidth; w.classList.add('shake2');
  setTimeout(() => w.classList.remove('shake2'), 460);
}
// Flitzekatze: two little cats dash from the extra to both ends of its line
function dashers(r, c, dir, d) {
  if (REDUCED) return;
  const k0 = r * N + c, ends = dir === 'h' ? [r * N, r * N + N - 1] : [c, (N - 1) * N + c];
  for (const e of ends) {
    if (e === k0) continue;
    const a = pctPos(k0), b = pctPos(e), cells = dir === 'h' ? Math.abs(e % N - c) : Math.abs((e / N | 0) - r);
    const ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
    later(d, () => {
      const el = document.createElement('div'); el.className = 'xdash';
      el.innerHTML = `<div class="xt"></div><div class="xh" style="transform:rotate(${(-ang).toFixed(1)}deg)">${CAT_ICON()}</div>`;
      Object.assign(el.style, { left: a.x + '%', top: a.y + '%', width: STEP + '%', height: STEP + '%', transform: `rotate(${ang.toFixed(1)}deg)` });
      boardEl.appendChild(el);
      el.animate([{ left: a.x + '%', top: a.y + '%' }, { left: b.x + '%', top: b.y + '%' }], { duration: 70 + cells * 30, easing: 'linear', fill: 'forwards' }).onfinish = () => {
        const [x, y] = cellXY(e); burst(x, y, 10, 1.3, ['#FF8FC0', '#FFD1E1', '#ffffff'], 'star');
        el.animate([{ opacity: 1 }, { opacity: 0, transform: el.style.transform + ' scale(.6)' }], { duration: 180, fill: 'forwards' }).onfinish = () => el.remove();
      };
    });
  }
}
function lineSparks(r, c, dir, d) {
  for (let i = 0; i < N; i++) {
    const k = dir === 'h' ? r * N + i : i * N + c, dist = dir === 'h' ? Math.abs(i - c) : Math.abs(i - r);
    if (i % 2) continue;
    later(d + 40 + dist * 30, () => { if (!REDUCED) { const [x, y] = cellXY(k); burst(x, y, 5, 1.1, ['#FFD1E1', '#ffffff', '#FF8FC0'], 'star'); } });
  }
}
// Katzenminze: a green puff, a double shockwave and a burst of leaves
function nipFx(cell, k, d) {
  const R = cell.radius || 1, p = pctPos(k), size = (2 * R + 1.8) * STEP;
  fxEl('nflash', { left: p.x + '%', top: p.y + '%', width: size + '%', height: size + '%' }, 620, d);
  ring(k, R + .45, d + 110, 'ring white');
  later(d, () => {
    if (REDUCED) return;
    const [x, y] = cellXY(k);
    burst(x, y, 14 + 6 * R, 1.6 + .35 * R, ['#5ED83C', '#8FE870', '#B8F0A8', '#2FA84A'], 'leaf');
    burst(x, y, 8, 1.2, ['#ffffff', '#E6FFCF'], 'star');
  });
  later(d + 40, bigShake); later(d, thud);
}
// Laserpunkt: a red beam for every jump of the dot, and a flash ring where it lands
function laserBeams(from, targets, d) {
  const pts = [from, ...targets];
  for (let i = 1; i < pts.length; i++) {
    beam(pts[i - 1], pts[i], 'lbeam', d + LEG * (i - 1) + 25, 400);
    const p = pctPos(pts[i]);
    fxEl('lhit', { left: p.x + '%', top: p.y + '%', width: STEP + '%', height: STEP + '%' }, 440, d + LEG * i);
  }
}
// Festmahl-Napf: rainbow rays to every treat it eats, one after another, outward from the bowl
function bowlFx(k, targets, delay, d) {
  const p = pctPos(k);
  fxEl('bflash', { '--bx': p.x + '%', '--by': p.y + '%' }, 560, d);
  ring(k, 2.2, d + 150, 'ring rainbow');
  targets.slice(0, 30).forEach((x, i) => beam(k, x, 'bray c' + (i % 6), Math.max(d + 40, (delay.get(x) || d) - 120), 440));
  later(d, () => {
    if (REDUCED) return;
    const [x, y] = cellXY(k);
    burst(x, y, 30, 2.3, ['#FF6FB5', '#FFB547', '#FFE14D', '#7CDB5A', '#43B6FF', '#B57CFF'], 'star');
  });
  later(d + 60, bigShake); later(d, () => extraSound('bowl'));
}
const firePlain = fire;
fire = function (cell, k, clear, delay, base, fxq) {
  const had = new Set(clear);
  firePlain(cell, k, clear, delay, base, fxq);
  const added = [...clear].filter(x => !had.has(x) && x !== k);
  xflash(cell, k, base);
  const r = k / N | 0, c = k % N;
  if (cell.type === 'cat') {
    const dirs = cell.mode ? ['h', 'v'] : [cell.dir === 'v' ? 'v' : 'h'];
    for (const dd of dirs) { dashers(r, c, dd, base); lineSparks(r, c, dd, base); }
    if (cell.mode) later(base + 40, bigShake);
    later(base, () => sweep(500, 2200, 0, .22, 'triangle', .05));
  } else if (cell.type === 'nip') nipFx(cell, k, base);
  else if (cell.type === 'bowl') {
    // the treats go one after another, outward from the bowl, so the rays fan out
    if (cell.eat !== 'all') {
      added.sort((a, b) => cellDist(a, k) - cellDist(b, k));
      const step = Math.min(42, 760 / Math.max(1, added.length));
      added.forEach((x, i) => delay.set(x, base + 150 + Math.round(i * step)));
    }
    bowlFx(k, cell.eat === 'all' ? added.filter((x, i) => i % 3 === 0) : added, delay, base);
  }
};
const laserRunPlain = laserRun;
laserRun = function (from, targets, d) { laserRunPlain(from, targets, d); laserBeams(from, targets, d); };
// leaves for the catnip burst
const drawShapePlain = drawShape;
drawShape = function (p) {
  if (p.shape !== 'leaf') return drawShapePlain(p);
  const s = p.size / 2;
  fctx.beginPath(); fctx.moveTo(0, -s); fctx.quadraticCurveTo(s * .95, 0, 0, s); fctx.quadraticCurveTo(-s * .95, 0, 0, -s); fctx.fill();
  fctx.strokeStyle = 'rgba(255,255,255,.6)'; fctx.lineWidth = Math.max(1, s * .14);
  fctx.beginPath(); fctx.moveTo(0, -s * .75); fctx.lineTo(0, s * .75); fctx.stroke();
};

/* ---------- after the zoomies: every extra still on the board goes off, like fireworks ---------- */
let lastFire = 0;
async function extrasFinale() {
  const before = score; lastFire = 0;
  let told = false;
  for (let round = 0; round < 4; round++) {
    const keys = [];
    for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const x = grid[r][c]; if (x && isPower(x.type) && !x.locked) keys.push(r * N + c); }
    if (!keys.length) break;
    if (!told) {
      told = true; mascot.classList.add('away');
      callout('Extra-Feuerwerk!', keys.length === 1 ? 'Dein letztes Extra geht los' : 'Deine ' + keys.length + ' übrigen Extras gehen los');
      sparkle(); await sleep(REDUCED ? 150 : 700);
    }
    shuffleList(keys);
    const gap = REDUCED ? 0 : Math.max(170, 430 - keys.length * 30);
    await resolve(new Set(keys), null, null, null, true, new Map(keys.map((k, i) => [k, i * gap])));
  }
  mascot.classList.remove('away');
  lastFire = score - before;
  return lastFire;
}

/* ---------- a stronger palette: deeper skies, darker trays so the treats pop, richer map worlds ---------- */
[[0, { sky1: '#FF5FA8', sky2: '#FFA9D2', line: 'rgba(255,255,255,.92)', fill: 'rgba(62,14,88,.74)', alt: 'rgba(104,38,140,.66)' }],
 [1, { sky1: '#3F9CFF', sky2: '#B49CFF', line: 'rgba(255,255,255,.92)', fill: 'rgba(20,32,112,.74)', alt: 'rgba(52,74,170,.66)' }],
 [2, { sky1: '#1A1052', sky2: '#6A35C8', line: 'rgba(255,255,255,.7)', fill: 'rgba(10,6,44,.76)', alt: 'rgba(48,32,118,.68)' }],
 [3, { sky1: '#FF7A30', sky2: '#FFC983', line: 'rgba(255,255,255,.92)', fill: 'rgba(48,18,92,.74)', alt: 'rgba(86,46,150,.64)' }]].forEach(([i, o]) => Object.assign(WSTYLE[i], o));
Object.assign(MCOL[0], { lo: '#5FCB45', hi: '#94E36F' }); Object.assign(MCOL[1], { lo: '#57B9FF', hi: '#AE94FF' }); Object.assign(MCOL[3], { lo: '#FF8B3D', hi: '#FFC47A' });

/* ---------- phones: sticky main buttons on the cards, focus moves into a dialog and back ---------- */
(function () {
  const wrap = (ids, card) => {
    const els = ids.map(id => $(id)).filter(Boolean); if (!els.length || els[0].parentElement.classList.contains('cta')) return;
    const w = document.createElement('div'); w.className = 'cta'; els[0].before(w); els.forEach(e => w.appendChild(e));
  };
  wrap(['introBtn']); wrap(['rescueBtn', 'endBtn', 'endMap']); wrap(['setDone']);
  const mo = new MutationObserver(ms => {
    for (const m of ms) {
      const ov = m.target, open = ov.classList.contains('show');
      if (open && !ov.__open) {
        ov.__open = true; ov.__prev = document.activeElement;
        setTimeout(() => {
          if (!ov.classList.contains('show')) return;
          const ok = b => b && !b.hidden && !b.disabled && b.offsetParent;
          const t = ['.cta .btn.big', '.cta .btn', '.btn.big', 'button'].map(s => [...ov.querySelectorAll(s)].find(ok)).find(Boolean) || ov.querySelector('[role="dialog"]');
          if (t) { if (!t.hasAttribute('tabindex') && t.getAttribute('role') === 'dialog') t.setAttribute('tabindex', '-1'); try { t.focus({ preventScroll: true }); } catch (e) {} }
        }, 80);
      } else if (!open && ov.__open) {
        ov.__open = false;
        const p = ov.__prev; ov.__prev = null;
        if (p && document.contains(p) && p.offsetParent && !document.querySelector('.overlay.show')) { try { p.focus({ preventScroll: true }); } catch (e) {} }
      }
    }
  });
  document.querySelectorAll('.overlay').forEach(ov => mo.observe(ov, { attributes: true, attributeFilter: ['class'] }));
  // Escape on the level card goes back to the map, like its X
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && $('introOv').classList.contains('show') && $('introX')) $('introX').click(); });
})();
