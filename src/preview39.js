
/* ===================== V39 preview only: a playground to try the new sounds and animations ===================== */
// A button in the corner opens a list: every extra and every combo, and the Krallenkratzer. A tap sets up a fresh board
// on the "Spielwiese" (a level with plenty of moves), puts the extras in the middle and swaps them. Neu/Alt switches
// between the new and the old sounds and animations, so they can be compared right away.
(function () {
  // the performance test can switch all effects off, to see what costs the time on this phone
  window.NOFX39 = false;
  const GROUP39 = { canvas: ['addVfx', 'addPart', 'sparks', 'twinkle', 'burst', 'popFx', 'orb', 'shock', 'bolt', 'catBeam'], dom: ['fxEl', 'ring', 'dashers', 'flyToCat', 'boardFx', 'xflash', 'floatText'] };
  for (const [g, names] of Object.entries(GROUP39)) for (const name of names) {
    const f = window[name]; if (typeof f !== 'function') continue;
    window[name] = function () { const o = window.NOFX39; if (o === true || o === g) return; return f.apply(this, arguments); };
  }
  // the test notes every call of these that blocks the phone for more than 2 ms, to find what is inside a long frame
  const MARK = []; let marking = false;
  const PHASE39 = new Set(['convert', 'gravity', 'nachschlag', 'bigShake', 'shake', 'collectBells', 'render', 'resolve', 'callout']);
  for (const name of ['resolve', 'convert', 'gravity', 'render', 'fire', 'bigShake', 'shake', 'callout', 'say', 'updateHud', 'drawGoals', 'feedPurr', 'collectBells', 'nachschlag', 'trySwap', 'tileEl', 'popFx', 'spawnFx', 'flyToCat', 'fxLoop', 'dropIn', 'place', 'extrasFor', 'findMatches', 'hasMove', 'later', 'catEat', 'fitGoals', 'fitPurrTxt', 'drawPurr', 'sxPlay', 'chomp', 'chime']) {
    const f = window[name]; if (typeof f !== 'function') continue;
    window[name] = function () {
      if (!marking) return f.apply(this, arguments);
      const t = performance.now(), r = f.apply(this, arguments), dt = performance.now() - t;
      if (dt > 2 || PHASE39.has(name)) MARK.push([t, name, dt]);
      return r;
    };
  }
  // switches for the analysis: the shake, the pop of eaten tiles, the glow behind extras, the falling in of new tiles
  window.OPT39 = {};
  for (const name of ['bigShake', 'shake']) { const f = window[name]; window[name] = function () { if (OPT39.noshake) return; return f.apply(this, arguments); }; }
  { const f = window.dropIn; window.dropIn = function (d) { if (OPT39.nodrop) { if (d) d.classList.remove('fadein'); return; } return f.apply(this, arguments); }; }
  const SANDBOX = { name: 'Spielwiese', moves: 99, target: 1000, collect: [[0, 999]], board: ['........', '........', '........', '........', '........', '........', '........', '........'] };
  let LV0 = null;
  const DEMOS = [
    ['Doppel-Festmahl', [[4, 3, 'bowl'], [4, 4, 'bowl']], 'big'],
    ['Festmahl + Flitzer', [[4, 3, 'bowl'], [4, 4, 'cat', 'h']], 'big'],
    ['Festmahl + Minze', [[4, 3, 'bowl'], [4, 4, 'nip']], 'big'],
    ['Festmahl + Laser', [[4, 3, 'bowl'], [4, 4, 'laser']], 'big'],
    ['Krallenkratzer', 'claw', 'big'],
    ['Festmahl', [[4, 3, 'bowl']]],
    ['Flitzer', [[4, 3, 'cat', 'h']]],
    ['Minze', [[4, 3, 'nip']]],
    ['Laser', [[4, 3, 'laser']]],
    ['2× Flitzer', [[4, 3, 'cat', 'h'], [4, 4, 'cat', 'v']]],
    ['Flitzer + Minze', [[4, 3, 'cat', 'v'], [4, 4, 'nip']]],
    ['Laser + Flitzer', [[4, 3, 'laser'], [4, 4, 'cat', 'h']]],
    ['2× Minze', [[4, 3, 'nip'], [4, 4, 'nip']]],
    ['2× Laser', [[4, 3, 'laser'], [4, 4, 'laser']]],
    ['Extras entstehen', 'make'],
    ['Sieg im letzten Zug', 'clutch', 'big']
  ];
  const wait = ms => new Promise(r => setTimeout(r, ms));
  let running = false, queued = null;
  const go = d => { running = true; (d === 'bench' ? bench() : d === 'benchnip' ? bench('nip') : run(d)).catch(() => {}).finally(() => { running = false; if (queued) { const q = queued; queued = null; go(q); } }); };
  const idle = async () => { for (let i = 0; i < 300 && busy; i++) await wait(50); };
  // a board without matches, the extras on top
  function board(place, avoid = -1) {
    for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
      if (!mask[r][c]) { grid[r][c] = null; continue; }
      let t, n = 0;
      const same = (a, b) => a && b && a.type === t && b.type === t;
      do { t = rnd(); n++; } while (n < 60 && (t === avoid || ((c >= 2 && same(grid[r][c - 1], grid[r][c - 2])) || (r >= 2 && same(grid[r - 1][c], grid[r - 2][c])) ||
        (r >= 1 && c >= 1 && same(grid[r - 1][c], grid[r][c - 1]) && grid[r - 1][c - 1] && grid[r - 1][c - 1].type === t))));
      grid[r][c] = mk(t);
    }
    for (const [r, c, kind, dir] of place) { const x = mk(kind); if (dir) x.dir = dir; grid[r][c] = x; }
    render(false);
  }
  async function sandbox() {
    if (!onMap && !ending && LEVELS[0] === SANDBOX && level === 1) return;
    document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show'));
    if (!onMap) { showMap(); await wait(500); }
    try { for (let i = 0; i < 80 && introRun; i++) { mapSkip = true; await wait(50); } } catch (e) {}
    if (LEVELS[0] !== SANDBOX) { LV0 = LEVELS[0]; LEVELS[0] = SANDBOX; }
    lives = Math.max(lives, 1);
    openLevel(1); await wait(450);
    const b = $('introBtn'); if (b && $('introOv').classList.contains('show')) b.click();
    await wait(1300);
  }
  const showMap39 = showMap;
  showMap = function () { if (LV0 && LEVELS[0] === SANDBOX) { LEVELS[0] = LV0; LV0 = null; } return showMap39.apply(this, arguments); };
  async function run(d) {
    // (the tap already closed the list; a demo that was waiting must not close it again if it was opened meanwhile)
    await sandbox(); await idle();
    if (d[1] === 'claw') {
      board([]); await wait(350);
      inv.claw = (inv.claw || 0) + 1; aim = { kind: 'claw' }; window.__p39t = performance.now(); await doAim(4, 3); return;
    }
    if (d[1] === 'clutch') {
      // one move left, the goal is three of one kind: the swap wins on the very last move
      const T = rnd();
      board([], T); for (const [r, c] of [[4, 2], [4, 3], [3, 4]]) grid[r][c].type = T;
      render(false);
      goals = [{ kind: 'collect', type: T, n: 3, left: 3 }]; lastRem = []; moves = 1; updateHud(); drawGoals();
      await wait(700);
      window.__p39t = performance.now(); await trySwap(3, 4, 4, 4); return;
    }
    if (d[1] === 'make') {
      // four, a square, an L and five: each swap makes a new extra
      const T = rnd();
      const plans = [
        [[[2, 1], [2, 2], [2, 4], [3, 3]], [3, 3, 2, 3]],
        [[[2, 2], [2, 3], [3, 2], [4, 3]], [4, 3, 3, 3]],
        [[[1, 2], [2, 2], [3, 3], [3, 4], [4, 2]], [4, 2, 3, 2]],
        [[[2, 1], [2, 2], [2, 4], [2, 5], [3, 3]], [3, 3, 2, 3]]
      ];
      for (const [cells, sw] of plans) {
        board([], T);
        for (const [r, c] of cells) grid[r][c].type = T;
        render(false); await wait(500);
        await trySwap(...sw); await idle(); await wait(700);
      }
      return;
    }
    const one = d[1].length === 1 && d[1][0][2] !== 'bowl';
    if (one && typeof PAIR40 !== 'undefined' && PAIR40) {
      // Candy-Crush rule: the extra needs a match, so two treats of its colour wait where it lands
      const T = rnd(); board(d[1], T); grid[4][3].col = T; grid[4][5].type = T; grid[4][6].type = T; render(false);
    } else board(d[1]);
    await wait(500);
    window.__p39t = performance.now(); await trySwap(4, 3, 4, 4);
  }
  async function bench(mode) {
    const COMBOS = mode === 'nip' ? ['Festmahl + Minze', 'Festmahl + Laser'] : ['Festmahl + Flitzer', 'Festmahl + Minze', 'Festmahl + Laser', 'Doppel-Festmahl'];
    if (mode === 'nip') window.VARS39 = [['normal', {}], ['Schale eigene Ebene', { cls: 'tl39' }], ['Schale o. Schatten', { cls: 'ts39' }], ['ohne Wackeln', { noshake: 1 }], ['Brett eckig', { cls: 'nr39' }]];
    const VARS = window.VARS39 || [['alles an', {}], ['ohne Effekte', { nofx: true }]];
    const rnd0 = Math.random, snd0 = soundOn, pair0 = typeof PAIR40 !== 'undefined' ? PAIR40 : null, rows = [];
    const pill = document.createElement('div'); pill.id = 'p39pill'; document.body.appendChild(pill);
    let i = 0;
    // the sounds are prepared in the background first, so that does not run in the middle of the test
    if (typeof SXB !== 'undefined' && typeof sxPrewarm === 'function' && soundOn) { initAudio(); sxPrewarm(); for (let w = 0; w < 60 && SXB.size < Object.keys(SXDEF).length; w++) { pill.textContent = 'Sounds werden vorbereitet …'; await wait(250); } }
    try {
      if (pair0 !== null) PAIR40 = false;
      for (const [vn, o] of VARS) for (const cn of COMBOS) {
        pill.textContent = 'Leistungstest läuft … ' + (++i) + ' / ' + COMBOS.length * VARS.length;
        soundOn = snd0 && !o.mute; window.NOFX39 = o.nofx || false;
        window.OPT39 = o; document.body.classList.toggle('np39', !!o.nopop); document.body.classList.toggle('ng39', !!o.noglow);
        for (const c of ['tl39', 'ts39', 'nr39']) document.body.classList.toggle(c, o.cls === c);
        let a = 1234567; Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
        const fr = [], fe = []; let last = 0, on = true, t0 = 0;
        const loop = t => { if (window.__p39t && !t0) t0 = t; if (t0 && last && last >= t0) { fr.push(t - last); fe.push(t); } last = t; if (on) requestAnimationFrame(loop); };
        window.__p39t = 0; MARK.length = 0; marking = true; requestAnimationFrame(loop);
        await run(DEMOS.find(d => d[0] === cn)); await idle(); await wait(300); on = false; marking = false;
        const n = fr.length, sum = fr.reduce((x, y) => x + y, 0);
        // the worst frame: which calls ran inside it, and how long
        let wi = 0; fr.forEach((x, j) => { if (x > fr[wi]) wi = j; });
        const wEnd = fe[wi], wStart = wEnd - fr[wi], inFrame = MARK.filter(([t]) => t >= wStart - 5 && t <= wEnd);
        const js = {}; for (const [, nm, dt] of inFrame) if (dt > 2) js[nm] = Math.max(js[nm] || 0, dt);
        const before = MARK.filter(([t, nm]) => PHASE39.has(nm) && t <= wEnd && t >= wStart - 400).slice(-2).map(([t, nm]) => nm + ' ' + Math.round(t - wStart)).join(', ');
        const top = Object.entries(js).sort((p, q) => q[1] - p[1]).slice(0, 3).map(([k, v]) => k + ' ' + Math.round(v));
        const when = Math.round(wStart - t0);
        rows.push([cn, vn, fr.filter(x => x > 50).length, Math.round(Math.max(0, ...fr)), n ? Math.round(n * 1000 / sum) : 0, when, (top.join(', ') || '–') + (before ? ' · davor: ' + before : '')]);
        Math.random = rnd0; await wait(500);
      }
    } finally { if (mode === 'nip') window.VARS39 = null; Math.random = rnd0; soundOn = snd0; window.NOFX39 = false; window.OPT39 = {}; document.body.classList.remove('np39', 'ng39', 'tl39', 'ts39', 'nr39'); if (pair0 !== null) PAIR40 = pair0; pill.remove(); }
    const ov = document.createElement('div'); ov.id = 'p39res';
    ov.innerHTML = '<div class="p39card"><div class="p39head"><b>Leistungstest</b><small>' + esc(navigator.userAgent.replace(/.*?\((.*?)\).*/, '$1')).slice(0, 60) + '</small></div>' +
      '<table><tr><th>Kombi</th><th></th><th>Ruckler</th><th>längster</th><th>Bilder/s</th></tr>' +
      rows.map(r => `<tr><td>${r[0].replace('Festmahl', 'F.')}</td><td>${r[1]}</td><td class="${r[2] > 2 ? 'bad' : ''}">${r[2]}</td><td class="${r[3] > 100 ? 'bad' : ''}">${r[3]} ms</td><td>${r[4]}</td></tr>` +
        `<tr class="det"><td colspan="5">längster bei ${r[5]} ms: ${esc(r[6])}</td></tr>`).join('') +
      '</table><p class="p39note">Ruckler = Bilder, die länger als 50 ms gebraucht haben. Mach bitte einen Screenshot davon und schick ihn mir.</p><button type="button" class="p39x" aria-label="Schließen">✕</button></div>';
    ov.onclick = e => { if (e.target === ov || e.target.closest('.p39x')) ov.remove(); };
    document.body.appendChild(ov);
  }
  // the button and the list
  const btn = document.createElement('button'); btn.id = 'p39btn'; btn.type = 'button';
  btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M4 9v6h4l5 4V5L8 9H4z" fill="#fff"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg><b>Vorschau</b>';
  const sheet = document.createElement('div'); sheet.id = 'p39'; sheet.hidden = true;
  sheet.innerHTML = '<div class="p39card"><div class="p39head"><b>Vorschau</b><small>Neue Sounds und Animationen</small></div>' +
    '<div class="p39lbl">Sounds und Animationen</div><div class="p39seg" role="group"><button type="button" data-v="new">Neu</button><button type="button" data-v="old">Alt</button></div>' +
    (typeof PAIR40 !== 'undefined' ? '<div class="p39lbl">Extras</div><div class="p39seg" role="group"><button type="button" data-p="on">Erst paaren (Candy Crush)</button><button type="button" data-p="off">Sofort (bisher)</button></div>' : '') +
    '<div class="p39grid">' + DEMOS.map((d, i) => `<button type="button" class="${d[2] === 'big' ? 'big' : ''}" data-i="${i}">${d[0]}</button>`).join('') + '</div>' +
    '<p class="p39note">Tipp drauf: das Brett wird neu gelegt und die Extras werden getauscht. Danach kannst du normal weiterspielen.</p>' +
    '<button type="button" class="p39bench">Leistungstest starten (dauert gut eine Minute)</button>' +
    '<button type="button" class="p39bench alt" data-m="benchnip">Analyse Minze + Laser (dauert gut eine Minute)</button>' +
    '<button type="button" class="p39x" aria-label="Schließen">✕</button></div>';
  document.body.append(btn, sheet);
  // in a level the button sits in the gap above the board (when there is one), so it covers nothing
  const placeBtn = () => {
    let top = '';
    if (!onMap) { const bw = $('boardwrap'), ac = document.querySelector('main .actions'); if (bw && ac) { const b = bw.getBoundingClientRect(), a = ac.getBoundingClientRect(); if (a.top - b.bottom >= 50) top = Math.round((b.bottom + a.top) / 2 - 19) + 'px'; } }
    btn.style.top = top; btn.style.bottom = top ? 'auto' : '';
  };
  setInterval(placeBtn, 600); addEventListener('resize', placeBtn);
  const seg = () => sheet.querySelectorAll('.p39seg button').forEach(b => b.classList.toggle('on', b.dataset.v ? (b.dataset.v === 'new') === FX39 : (b.dataset.p === 'on') === !!PAIR40));
  const close = () => { sheet.hidden = true; };
  btn.onclick = () => { initAudio(); seg(); sheet.hidden = false; };
  sheet.onclick = e => {
    const b = e.target.closest('button');
    if (!b) { if (e.target === sheet) close(); return; }
    if (b.classList.contains('p39x')) return close();
    if (b.classList.contains('p39bench')) { const m = b.dataset.m || 'bench'; close(); if (running) queued = m; else go(m); return; }
    if (b.dataset.v) { FX39 = b.dataset.v === 'new'; try { localStorage.setItem('wm-fx39', FX39 ? 'new' : 'old'); } catch (er) {} seg(); return; }
    if (b.dataset.p) {
      PAIR40 = b.dataset.p === 'on'; try { localStorage.setItem('wm-pair40', PAIR40 ? 'on' : 'off'); } catch (er) {} seg();
      // extras already on the board get a colour (or show their old look again)
      if (!onMap && mask.length) { for (const row of grid) for (const x of row) if (x && (x.type === 'cat' || x.type === 'nip' || x.type === 'laser') && x.col == null) x.col = rnd(); if (!busy) render(false); }
      return;
    }
    if (b.dataset.i != null) { close(); if (running) queued = DEMOS[+b.dataset.i]; else go(DEMOS[+b.dataset.i]); }
  };
})();
