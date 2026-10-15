import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
s = open(D + 'game_v17_base.html').read()
R = lambda f: open(D + f).read()
LVFILE = os.environ.get('LV12', 'levels12.json')
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, ('COUNT', s.count(a), a[:140])
    s = s.replace(a, b)
def block(start, end_marker, new):
    global s
    assert s.count(start) == 1, ('BLOCK', s.count(start), start[:80])
    a = s.index(start); b = s.index(end_marker, a + len(start))
    s = s[:a] + new + s[b:]

rep('</style>', R('feat12.css') + R('feat23.css') + R('intro25.css') + R('feat26.css') + R('vfx28.css') + R('game27.css') + R('perf28.css') + R('game30.css') + R('game32.css') + R('game33.css') + R('game35.css') + R('game36.css') + '</style>')

# ---------------- tiles: triple boxes, gifts, cucumbers, alarm clocks ----------------
block('const BOX_SVG = hp =>', 'const NETP =', R('art12.js').split('const BOX3_SVG = hp => ')[1].split('\n// the alarm clock')[0].replace('`<svg viewBox', 'const BOX_SVG = hp => `<svg viewBox', 1) + '\n')
rep("const canSwap = x => !!x && x.type !== 'box' && x.type !== 'wet' && x.type !== 'boss' && !x.locked;",
    "const canSwap = x => !!x && x.type !== 'box' && x.type !== 'wet' && x.type !== 'boss' && x.type !== 'gift' && x.type !== 'cuke' && !x.locked;")
rep("x.type === 'box' ? BOX_SVG(x.hp) : x.type === 'wet' ? WET_SVG : ICONS[x.type];",
    "x.type === 'box' ? BOX_SVG(x.hp) : x.type === 'wet' ? WET_SVG : x.type === 'gift' ? GIFT_SVG : x.type === 'cuke' ? CUKE_SVG : ICONS[x.type] + (x.clock != null ? clockHTML(x.clock) : '');")
rep("  if (x.type === 'boss') return 'Staubsauger-Roboter';\n  return (x.gold ? 'Goldenes ' : '') + NAMES[x.type] + (x.locked ? ', in Wolle festgeknotet' : '');",
    "  if (x.type === 'boss') return 'Staubsauger-Roboter';\n  if (x.type === 'gift') return 'Geschenkbox';\n  if (x.type === 'cuke') return 'Gurke';\n  return (x.gold ? 'Goldenes ' : '') + NAMES[x.type] + (x.locked ? ', in Wolle festgeknotet' : '') + (x.clock != null ? ', Wecker: ' + x.clock : '');")
rep("        if (ch === 'b' || ch === 'B') { row.push({ type: 'box', id: ++idc, hp: ch === 'B' ? 2 : 1, gold: false, locked: false }); continue; }",
    "        if (ch === 'b' || ch === 'B' || ch === 'C') { row.push({ type: 'box', id: ++idc, hp: ch === 'C' ? 3 : ch === 'B' ? 2 : 1, gold: false, locked: false }); continue; }\n"
    "        if (ch === 'p' || ch === 'u') { row.push({ type: ch === 'p' ? 'gift' : 'cuke', id: ++idc, hp: 1, gold: false, locked: false }); continue; }")
rep("        const x = mk(t); if (ch === 'w') x.locked = true; row.push(x);", "        const x = mk(t); if (ch === 'w') x.locked = true; if (ch === 'a') x.clock = cfg.clock || 12; row.push(x);")
rep("    const pool = []; for (const row of grid) for (const x of row) if (x && isNormal(x.type) && !x.locked) pool.push(x);\n    if (pool.length) pool[Math.floor(Math.random() * pool.length)].gold = true;",
    "    const pool = []; for (const row of grid) for (const x of row) if (x && isNormal(x.type) && !x.locked && x.clock == null) pool.push(x);\n    for (let i = 0; i < (goals.some(g => g.kind === 'gold') ? 3 : 1) && pool.length; i++) pool.splice(Math.floor(Math.random() * pool.length), 1)[0].gold = true;")
# goals
rep("  if (has('bB')) cfg.goals.push({ kind: 'boxes' });", "  if (has('bBC')) cfg.goals.push({ kind: 'boxes' });")
rep("  if (has('V')) cfg.goals.push({ kind: 'boss' });", """  if (has('V')) cfg.goals.push({ kind: 'boss' });
  if (has('p')) cfg.goals.push({ kind: 'gifts' });
  if (has('u')) cfg.goals.push({ kind: 'cukes' });
  for (const [what, n] of def.make || []) cfg.goals.push({ kind: 'make', what, n: n + loop });
  if (def.goldrush) cfg.goals.push({ kind: 'gold', n: def.goldrush + loop });""")
rep("  cfg.boxHp = has('B') ? 2 : 1;", """  cfg.boxHp = has('C') ? 3 : has('B') ? 2 : 1;
  cfg.clock = Math.max(6, (def.clock || 12) - loop); cfg.clockRate = def.clockRate || 0; cfg.clockMax = def.clockMax || 3;
  cfg.turbo = def.turbo || 0; cfg.goldRate = def.goldrush ? .08 : .015;""")
rep("  if (g.kind === 'boss') return boss ? Math.max(0, boss.hp) : 0;\n  return countOnBoard(x => x.locked);",
    """  if (g.kind === 'boss') return boss ? Math.max(0, boss.hp) : 0;
  if (g.kind === 'gifts') return countOnBoard(x => x.type === 'gift');
  if (g.kind === 'cukes') return countOnBoard(x => x.type === 'cuke');
  if (g.kind === 'make' || g.kind === 'gold') return Math.max(0, g.left);
  return countOnBoard(x => x.locked);""")
rep(": g.kind === 'boss' ? VAC_ICON : NET_ICON;",
    ": g.kind === 'boss' ? (cfg && cfg.turbo ? VAC_TURBO_SVG : VAC_ICON) : g.kind === 'gifts' ? GIFT_SVG : g.kind === 'cukes' ? CUKE_SVG : g.kind === 'make' ? MAKE_ICON(g.what) : g.kind === 'gold' ? GOLDPAW_SVG : NET_ICON;")
rep("  if (g.kind === 'boss') return n + ' Treffer gegen den Staubsauger';\n  return n + ' Leckerlis aus der Wolle befreien';",
    """  if (g.kind === 'boss') return n + ' Treffer gegen den ' + (cfg && cfg.turbo ? 'Turbo-Roboter' : 'Staubsauger');
  if (g.kind === 'gifts') return n + (n === 1 ? ' Geschenk' : ' Geschenke') + ' auspacken';
  if (g.kind === 'cukes') return n + (n === 1 ? ' Gurke' : ' Gurken') + ' verjagen';
  if (g.kind === 'make') return n + ' ' + MAKE_NAME[g.what][n === 1 ? 0 : 1] + (g.what === 'combo' ? ' zünden' : ' bauen');
  if (g.kind === 'gold') return n + (n === 1 ? ' goldenes Leckerli' : ' goldene Leckerlis') + ' fressen';
  return n + ' Leckerlis aus der Wolle befreien';""")
rep("const isStatic = x => !!x && (x.type === 'box' || x.type === 'wet' || x.type === 'boss' || x.locked);",
    "const isStatic = x => !!x && (x.type === 'box' || x.type === 'wet' || x.type === 'boss' || x.type === 'gift' || x.type === 'cuke' || x.locked);")
# falling treats: golden ones (more in a gold rush) and new alarm clocks
rep("  const bellCol = bellNow ? Math.floor(Math.random() * N) : -1;", "  const bellCol = bellNow ? Math.floor(Math.random() * N) : -1;\n  let clocksNow = cfg.clockRate ? countOnBoard(x => x.clock > 0) : 99;")
rep("      else cell = mk(rnd(), cfg.gold && Math.random() < .015);",
    "      else { cell = mk(rnd(), cfg.gold && Math.random() < cfg.goldRate); if (!cell.gold && clocksNow < cfg.clockMax && Math.random() < cfg.clockRate) { cell.clock = cfg.clock; clocksNow++; } }")
rep("    const hot = x.type === 'boss' || x.type === 'box' || x.type === 'wet' || x.locked || x.gold ||",
    "    const hot = x.type === 'boss' || isHit(x) || x.clock > 0 || x.locked || x.gold ||")

# ---------------- resolve: gifts open into extras, cucumbers flee, orders and gold count ----------------
rep("      if (cell.type === 'box' || cell.type === 'wet') { hit(k, dOf(k)); clear.delete(k); continue; }", "      if (isHit(cell)) { hit(k, dOf(k)); clear.delete(k); continue; }")
rep("        if (r2 >= 0 && r2 < N && c2 >= 0 && c2 < N && grid[r2][c2] && (grid[r2][c2].type === 'box' || grid[r2][c2].type === 'wet')) hit(r2 * N + c2, dOf(k));",
    "        if (r2 >= 0 && r2 < N && c2 >= 0 && c2 < N && isHit(grid[r2][c2])) hit(r2 * N + c2, dOf(k));")
rep("    let golds = 0, broken = 0, wetBroken = 0, firstHit = Infinity, bossHit = 0;", "    let golds = 0, broken = 0, wetBroken = 0, firstHit = Infinity, bossHit = 0, giftsOpened = 0, cukesGone = 0, giftKinds = [];")
block("    for (const [k, d] of hits) {\n      const r = k / N | 0, c = k % N, box = grid[r][c], el = els.get(box.id), isWet = box.type === 'wet';",
      "    // the blanket: every patch",
      """    for (const [k, d] of hits) {
      const r = k / N | 0, c = k % N, box = grid[r][c], el = els.get(box.id), isWet = box.type === 'wet';
      box.hp--; maxD = Math.max(maxD, d); firstHit = Math.min(firstHit, d);
      if (box.hp <= 0) {
        brokenKeys.push(k);
        if (box.type === 'gift') {
          // the present opens and an extra jumps out right where it stood
          const kind = giftKind(), sp = mk(kind); if (kind === 'cat') sp.dir = Math.random() < .5 ? 'h' : 'v';
          giftsOpened++; giftKinds.push(kind); grid[r][c] = sp;
          later(d, () => {
            const [x, y] = cellXY(k); burst(x, y, 22, 1.5, ['#43B6FF', '#FF4FA3', '#FFE14D', '#ffffff'], 'star');
            if (el) el.classList.add('pop');
            setTimeout(() => { if (el) el.remove(); els.delete(box.id); }, 260);
            if (grid[r][c] === sp && !els.has(sp.id)) { const ne = tileEl(sp); place(sp, r, c); ne.classList.add('spawn'); }
          });
          continue;
        }
        if (box.type === 'cuke') cukesGone++; else if (isWet) { wetBroken++; wetGone = true; } else broken++;
        grid[r][c] = null;
        later(d, () => {
          const [x, y] = cellXY(k); burst(x, y, 14, 1.3, box.type === 'cuke' ? ['#5ED83C', '#B8F0A8', '#ffffff', '#1A8628'] : isWet ? WETCOL : BOXCOL, isWet || box.type === 'cuke' ? undefined : 'rect');
          if (el) el.classList.add(box.type === 'cuke' ? 'flee' : 'pop');
          setTimeout(() => { if (el) el.remove(); els.delete(box.id); }, box.type === 'cuke' ? 480 : 280);
        });
      } else {
        const hp = box.hp;
        later(d, () => {
          if (!el) return;
          el.innerHTML = BOX_SVG(hp); el.setAttribute('aria-label', labelFor(box));
          el.classList.remove('hit'); void el.offsetWidth; el.classList.add('hit');
          const [x, y] = cellXY(k); burst(x, y, 6, .9, BOXCOL, 'rect');
        });
      }
    }
""")
rep("    for (const g of goals) if (g.kind === 'collect') for (const k of clear) { const cell = grid[k / N | 0][k % N]; if (cell && cell.type === g.type) g.left--; }",
    "    for (const g of goals) if (g.kind === 'collect') for (const k of clear) { const cell = grid[k / N | 0][k % N]; if (cell && cell.type === g.type) g.left--; }\n"
    "    if (golds) for (const g of goals) if (g.kind === 'gold') g.left -= golds;\n"
    "    for (const [, ex] of spawns) for (const g of goals) if (g.kind === 'make' && g.what === ex.kind && g.left > 0) g.left--;")
rep("+ tucked * 20 + bossHit * 30 +", "+ tucked * 20 + giftsOpened * 80 + cukesGone * 80 + bossHit * 30 +")
rep("    if (wetBroken) later(firstHit, () => splorch());", "    if (wetBroken) later(firstHit, () => splorch());\n    if (cukesGone) later(firstHit, () => { hopSound(); catYuck(); });\n    if (giftsOpened) later(firstHit, () => { sparkle(); extraSound(giftKinds[0]); });")
rep("      else if (broken) text = 'Karton auf!';", "      else if (giftsOpened) { text = 'Geschenk!'; sub = EXTRA[giftKinds[0]].name; }\n      else if (cukesGone) text = cukesGone > 1 ? 'Gurken verjagt!' : 'Gurke verjagt!';\n      else if (broken) text = 'Karton auf!';")
rep("      else if (wetBroken && !countOnBoard(x => x.type === 'wet')) say('Puh! Kein Nassfutter mehr. ' + catName + ' atmet auf.');",
    "      else if (wetBroken && !countOnBoard(x => x.type === 'wet')) say('Puh! Kein Nassfutter mehr. ' + catName + ' atmet auf.');\n"
    "      else if (giftsOpened && !toldGift) { toldGift = true; say('Ein Geschenk! Da war ' + EXTRA_A[giftKinds[0]] + ' drin.'); }\n"
    "      else if (cukesGone && !countOnBoard(x => x.type === 'cuke')) say('Alle Gurken sind weg. ' + catName + ' traut sich wieder raus.');")
# two extras swapped: an ordered combo
rep("    if (sa && sb) {\n      // two extras swapped together: a bigger combo", "    if (sa && sb) {\n      for (const g of goals) if (g.kind === 'make' && g.what === 'combo' && g.left > 0) g.left--;\n      // two extras swapped together: a bigger combo")
# after a move: cucumbers hop, clocks tick
rep("  if (moves > 0 && boss && boss.hp > 0) { await bossStep(); updateHud(); if (goalsDone()) return winSequence(); }\n  if (moves <= 0) {",
    """  if (moves > 0 && boss && boss.hp > 0) { await bossStep(); updateHud(); if (goalsDone()) return winSequence(); }
  if (moves > 0 && countOnBoard(x => x.type === 'cuke')) { await cukeStep(); updateHud(); if (goalsDone()) return winSequence(); }
  if (moves > 0 && clockTick()) return clockRing();
  if (moves <= 0) {""")
rep("  else if (cell.locked && !toldLock) { toldLock = true; say('Das hängt in der Wolle fest. Bring es in ein Match, dann ist es frei.'); }",
    "  else if (cell.locked && !toldLock) { toldLock = true; say('Das hängt in der Wolle fest. Bring es in ein Match, dann ist es frei.'); }\n"
    "  else if (cell.type === 'gift') say('Geschenke kann man nicht verschieben. Ein Match direkt daneben packt sie aus!');\n"
    "  else if (cell.type === 'cuke') { catYuck(); say('Die Gurke fasst ' + catName + ' nicht an! Mach ein Match direkt daneben, dann ist sie weg.'); }")
# what a cell is worth: the bot and the hints learn the new things
rep("  return { want: new Set(goals.filter(g => g.kind === 'collect' && g.left > 0).map(g => g.type)), milk: has('milk'), cover: has('cover'), bells: has('bells'), locks: has('locks') };",
    "  return { want: new Set(goals.filter(g => g.kind === 'collect' && g.left > 0).map(g => g.type)), milk: has('milk'), cover: has('cover'), bells: has('bells'), locks: has('locks'),\n"
    "    make: new Set(goals.filter(g => g.kind === 'make' && g.left > 0).map(g => g.what)) };")
rep("  if (x.type === 'box' || x.type === 'wet') return 3;", "  if (x.type === 'box' || x.type === 'wet' || x.type === 'gift') return 3;\n  if (x.type === 'cuke') return 3.5;")
rep("  if (x.gold) v += 1.5;", "  if (x.gold) v += goals.some(g => g.kind === 'gold' && g.left > 0) ? 4 : 1.5;\n  if (x.clock > 0) v += 2.5 + (x.clock <= 3 ? 8 : x.clock <= 6 ? 2.5 : 0);")
rep("  for (const [dr, dc] of D4) { const y = inB(r + dr, c + dc) && grid[r + dr][c + dc]; if (y && (y.type === 'box' || y.type === 'wet')) v += 1.8; if (y && y.type === 'boss') nearBoss = true; }",
    "  for (const [dr, dc] of D4) { const y = inB(r + dr, c + dc) && grid[r + dr][c + dc]; if (y && (y.type === 'box' || y.type === 'wet' || y.type === 'gift')) v += 1.8; if (y && y.type === 'cuke') v += 2.6; if (y && y.type === 'boss') nearBoss = true; }")
rep("      if (pa && pb) v = 40 + (a.type === 'bowl' || b.type === 'bowl' ? 30 : 0);", "      if (pa && pb) v = 40 + (a.type === 'bowl' || b.type === 'bowl' ? 30 : 0) + (X.make.has('combo') ? 40 : 0);")
rep("          for (const [, ex] of extrasFor(m, [r * N + c, r2 * N + c2])) v += SPAWN_V[ex.kind];", "          for (const [, ex] of extrasFor(m, [r * N + c, r2 * N + c2])) v += SPAWN_V[ex.kind] + (X.make.has(ex.kind) ? 30 : 0);")

# ---------------- the turbo robot drives two cells per move ----------------
rep("async function bossStep() {\n  if (!boss || boss.hp <= 0) return;\n  bossPlan();", "async function bossStep() {\n  await bossDrive();\n  if (cfg.turbo && boss && boss.hp > 0 && moves > 0) { await sleep(100); await bossDrive(); }\n}\nasync function bossDrive() {\n  if (!boss || boss.hp <= 0) return;\n  bossPlan();")
rep("  e.innerHTML = VAC_SVG + '<i class=\"varrow\"></i><div class=\"vbat\"><i></i><b class=\"vhp\"></b></div>';",
    "  e.innerHTML = VAC_SVG + '<i class=\"varrow\"></i><div class=\"vbat\"><i></i><b class=\"vhp\"></b></div>' + (cfg.turbo ? '<span class=\"vbolt\">' + BOLT_SVG + '</span>' : '');\n  e.classList.toggle('turbo', !!cfg.turbo);")
rep("  else if (!bossTold.move) { bossTold.move = true; say('Der Roboter fährt nach jedem Zug ein Feld weiter. Der Pfeil zeigt, wohin.'); }",
    "  else if (!bossTold.move) { bossTold.move = true; say(cfg.turbo ? 'Der Turbo-Roboter fährt zwei Felder pro Zug! Der Pfeil zeigt, wohin.' : 'Der Roboter fährt nach jedem Zug ein Feld weiter. Der Pfeil zeigt, wohin.'); }")

# ---------------- the super pounce: row, column and everything around the landing spot ----------------
rep("  for (let i = 0; i < N; i++) {\n    if (mask[r][i]) add(r * N + i, 40 + Math.abs(i - c) * 32);\n    if (mask[i][c]) add(i * N + c, 40 + Math.abs(i - r) * 32);\n  }",
    "  for (let i = 0; i < N; i++) {\n    if (mask[r][i]) add(r * N + i, 40 + Math.abs(i - c) * 32);\n    if (mask[i][c]) add(i * N + c, 40 + Math.abs(i - r) * 32);\n  }\n"
    "  if (isUnlocked('superpounce')) for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) if (inB(r + dr, c + dc) && mask[r + dr][c + dc]) add((r + dr) * N + c + dc, 70);")
rep("  boing(0); buzz([30, 40, 30]); callout('Sprung!', catName + ' räumt auf');", "  boing(0); buzz([30, 40, 30]); callout(isUnlocked('superpounce') ? 'Super-Sprung!' : 'Sprung!', catName + ' räumt auf');")
rep("  else if (kind === 'pounce') for (let i = 0; i < N; i++) { out.push(r * N + i); if (i !== r) out.push(i * N + c); }",
    "  else if (kind === 'pounce') { for (let i = 0; i < N; i++) { out.push(r * N + i); if (i !== r) out.push(i * N + c); } if (isUnlocked('superpounce')) for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) if ((dr || dc) && dr && dc && inB(r + dr, c + dc)) out.push((r + dr) * N + c + dc); }\n"
    "  else if (kind === 'feather') out.push(r * N + c);")
rep("const AIM_TEXT = {\n  pounce: () => 'Tipp auf ein Feld: ' + catName + ' springt drauf und räumt Reihe und Spalte ab.',",
    "const AIM_TEXT = {\n  pounce: () => 'Tipp auf ein Feld: ' + catName + ' springt drauf und räumt Reihe und Spalte ab' + (isUnlocked('superpounce') ? ', dazu alles rundherum.' : '.'),\n"
    "  feather: () => 'Tipp auf ein Leckerli: Es wird zur Flitzekatze.',")

# ---------------- the magic feather, the fourth tool ----------------
rep("  { id: 'swap', name: 'Stupser', short: 'Stupser', price: 15, unlock: 24, how: 'Mit dem Stupser tauschst du zwei Nachbarn, auch ohne Match.' }\n];",
    "  { id: 'swap', name: 'Stupser', short: 'Stupser', price: 15, unlock: 43, how: 'Mit dem Stupser tauschst du zwei Nachbarn, auch ohne Match.' },\n"
    "  { id: 'feather', name: 'Zauberfeder', short: 'Feder', price: 18, unlock: 97, how: 'Die Zauberfeder macht aus einem Leckerli eine Flitzekatze.' }\n];")
rep("price: 20, unlock: 21,", "price: 20, unlock: 33,")
rep("let inv = { paw: 0, claw: 0, swap: 0 }, invGot = {}", "let inv = { paw: 0, claw: 0, swap: 0, feather: 0 }, invGot = {}")
rep("boardEl.classList.remove('aim-pounce', 'aim-paw', 'aim-claw', 'aim-swap');", "boardEl.classList.remove('aim-pounce', 'aim-paw', 'aim-claw', 'aim-swap', 'aim-feather');")
rep("boardEl.classList.remove('aiming', 'aim-pounce', 'aim-paw', 'aim-claw', 'aim-swap');", "boardEl.classList.remove('aiming', 'aim-pounce', 'aim-paw', 'aim-claw', 'aim-swap', 'aim-feather');")
rep("  if (kind === 'paw' && (!cell || cell.type === 'bell')) { if (cell) { nope(); say('Glöckchen kann man nicht wegschlagen. Bring sie nach unten!'); } return; }",
    "  if (kind === 'paw' && (!cell || cell.type === 'bell')) { if (cell) { nope(); say('Glöckchen kann man nicht wegschlagen. Bring sie nach unten!'); } return; }\n"
    "  if (kind === 'feather' && (!cell || !isNormal(cell.type) || cell.locked)) { nope(); say('Die Zauberfeder wirkt nur auf Leckerlis, die frei liegen.'); return; }")
rep("    if (kind === 'paw') await pawAt(r, c); else await clawAt(r);", "    if (kind === 'paw') await pawAt(r, c); else if (kind === 'feather') await featherAt(r, c); else await clawAt(r);")

# ---------------- losing to an alarm clock, and the rescue that sets the clocks back ----------------
rep("  $('endTitle').textContent = won ? 'Level ' + level + ' geschafft!' : close ? 'Knapp daneben!' : 'Keine Züge mehr';",
    "  $('endTitle').textContent = won ? 'Level ' + level + ' geschafft!' : clockRang ? 'Der Wecker klingelt!' : close ? 'Knapp daneben!' : 'Keine Züge mehr';")
rep("  else text = treats >= price ? (close ? 'So knapp! Mit 5 Zügen mehr klappt das.' : 'Mit 5 Zügen mehr kannst du weiterspielen.') : catName + ' hat noch Hunger.';",
    "  else if (clockRang) text = treats >= price ? 'Herrchen ist wach. Mit 5 Zügen mehr und neu gestellten Weckern geht es weiter.' : 'Herrchen ist wach. Die Nascherei ist vorbei.';\n"
    "  else text = treats >= price ? (close ? 'So knapp! Mit 5 Zügen mehr klappt das.' : 'Mit 5 Zügen mehr kannst du weiterspielen.') : catName + ' hat noch Hunger.';")
rep("  moves += 5; updateHud();\n  $('endOv').classList.remove('show');", "  moves += 5; if (clockRang) resetClocks(); updateHud();\n  $('endOv').classList.remove('show');")
rep("  COLORS = cfg.colors; help = helpFor(level); cfg.gold = cfg.gold && isUnlocked('gold'); tutAbort();",
    "  COLORS = cfg.colors; help = helpFor(level); cfg.gold = cfg.gold && isUnlocked('gold'); tutAbort(); clockRang = false;")

# ---------------- the learning path over 160 levels ----------------
rep("const UNLOCK = { cat: 2, laser: 3, nip: 5, bowl: 7, chest: 8, purr: 9, combo: 12, boosts: 13, streak: 15, gold: 18 };",
    "const UNLOCK = { cat: 2, laser: 3, nip: 5, bowl: 7, chest: 8, purr: 9, combo: 12, streak: 22, boosts: 26, gold: 28, superpounce: 91 };")
# lessons: an order plants the shape on the list, a gift lesson fires whatever came out, the feather lesson aims at a good spot
rep("  if (st.plant) { const P = plant(st.plant, st.want, st.type); if (!P) return false; ctx.P = P; return true; }",
    "  if (st.plant) { const P = plant(typeof st.plant === 'function' ? st.plant() : st.plant, st.want, st.type); if (!P) return false; ctx.P = P; return true; }")
rep("if (x && x.type === st.use) {", "if (x && (st.use === 'any' ? isPower(x.type) : x.type === st.use)) {")
rep("    if (k == null) for (let i = 27; i < N * N && k == null; i++) if (plainAt(i / N | 0, i % N)) k = i;",
    "    else if (st.cell === 'feather') { const X = goalCtx(); let bv = -1e9; for (let i = 0; i < N * N; i++) { const r = i / N | 0, c = i % N; if (!plainAt(r, c)) continue; let h = 0, v = 0; for (let j = 0; j < N; j++) { h += cellWorth(r * N + j, X); v += cellWorth(j * N + c, X); } const sc = Math.max(h, v) - Math.hypot(r - 3.5, c - 3.5) * .6; if (sc > bv) { bv = sc; k = i; } } }\n"
    "    if (k == null) for (let i = 27; i < N * N && k == null; i++) if (plainAt(i / N | 0, i % N)) k = i;")
rep("    await tutWait({ type: 'turn', cell: k, check: () => true });\n    return true;", "    await tutWait({ type: 'turn', cell: k, check: () => true });\n    ctx.at = k;\n    return true;")
rep("    : target === 'gold' ? keysBox(k => grid[k / N | 0][k % N] && grid[k / N | 0][k % N].gold) : null;",
    "    : target === 'gold' ? keysBox(k => grid[k / N | 0][k % N] && grid[k / N | 0][k % N].gold)\n"
    "    : TINFO[target] ? keysBox(k => { const x = grid[k / N | 0][k % N]; return !!x && TINFO[target](x); }) : null;")

# ---------------- 32 worlds, each with its own name ----------------
rep("const worldName = w => WORLDS[w % 4].name + (w >= 4 ? ' ' + (Math.floor(w / 4) + 1) : '');",
    "const worldName = w => WORLD_NAMES[w % WORLD_NAMES.length][0] + (w >= WORLD_NAMES.length ? ' ' + (Math.floor(w / WORLD_NAMES.length) + 1) : '');")
rep("  $('introWorld').textContent = cfg.name + ' ' + WORLDS[cfg.world].at;", "  $('introWorld').textContent = cfg.name + ' ' + WORLD_NAMES[Math.floor((level - 1) / 5) % WORLD_NAMES.length][1];")
W = [('Erdbeergarten', 'im Erdbeergarten'), ('Wolkenland', 'im Wolkenland'), ('Sternennacht', 'in der Sternennacht'), ('Zuckerstrand', 'am Zuckerstrand'),
     ('Kirschblütenhain', 'im Kirschblütenhain'), ('Regenbogenhimmel', 'im Regenbogenhimmel'), ('Mondgarten', 'im Mondgarten'), ('Muschelbucht', 'in der Muschelbucht'),
     ('Blumenwiese', 'auf der Blumenwiese'), ('Luftschloss', 'im Luftschloss'), ('Glühwürmchenwald', 'im Glühwürmchenwald'), ('Korallenriff', 'am Korallenriff'),
     ('Trabzon', 'in Trabzon'), ('Drachenhimmel', 'im Drachenhimmel'), ('Polarlicht', 'im Polarlicht'), ('Leuchtturmküste', 'an der Leuchtturmküste'),
     ('Tulpenfeld', 'im Tulpenfeld'), ('Federwolken', 'in den Federwolken'), ('Sternschnuppenberg', 'am Sternschnuppenberg'), ('Palmeninsel', 'auf der Palmeninsel'),
     ('Beerenwald', 'im Beerenwald'), ('Luftballonfest', 'beim Luftballonfest'), ('Traumland', 'im Traumland'), ('Piratenbucht', 'in der Piratenbucht'),
     ('Kürbisbeet', 'im Kürbisbeet'), ('Sonnenwolken', 'in den Sonnenwolken'), ('Mitternachtsmarkt', 'auf dem Mitternachtsmarkt'), ('Lagune', 'in der Lagune'),
     ('Zaubergarten', 'im Zaubergarten'), ('Himmelstor', 'am Himmelstor'), ('Sternenpalast', 'im Sternenpalast'), ('Goldstrand', 'am Goldstrand')]
if os.path.exists(D + 'worlds36.json') and not os.environ.get('NO36'): W = W + [tuple(x) for x in json.load(open(D + 'worlds36.json'))]
rep("const LEVELS = [", "const WORLD_NAMES = " + json.dumps(W, ensure_ascii=False) + ";\nconst LEVELS = [")

# ---------------- 160 levels ----------------
LV = json.load(open(D + LVFILE))
if os.path.exists(D + 'fix23.json') and not os.environ.get('NOFIX23'):
    for k, v in json.load(open(D + 'fix23.json')).items(): LV[int(k) - 1].update(v)
# V27: the Schnurr-Power carries over and fills slowly, so the moves are retuned with the bot
if os.path.exists(D + 'fix27.json') and not os.environ.get('NOFIX27'):
    for k, v in json.load(open(D + 'fix27.json')).items(): LV[int(k) - 1].update(v)
if os.path.exists(D + 'fix35.json') and not os.environ.get('NOFIX35'):
    for k, v in json.load(open(D + 'fix35.json')).items(): LV[int(k) - 1].update(v)
# V36: levels 161-260 (generated by mk_levels36.py, goals and moves tuned with the bot: tune36.py, tune36b.py -> fix36.json)
if os.path.exists(D + 'levels36.json') and not os.environ.get('NO36'):
    LV += json.load(open(D + 'levels36.json'))
    if os.path.exists(D + 'fix36.json'):
        for k, v in json.load(open(D + 'fix36.json')).items(): LV[int(k) - 1].update(v)
def lvdef(d):
    parts = ["name: " + json.dumps(d['name'], ensure_ascii=False), "moves: %d" % d['moves'], "target: %d" % d.get('target', 1000)]
    if d.get('intro'): parts.append("intro: '%s'" % d['intro'])
    for k in ['hard', 'colors', 'bells', 'cover', 'boss', 'goldrush', 'clock', 'clockMax', 'turbo', 'long']:
        if d.get(k): parts.append("%s: %d" % (k, d[k]))
    if d.get('clockRate'): parts.append("clockRate: %s" % d['clockRate'])
    if d.get('collect'): parts.append('collect: ' + json.dumps(d['collect']))
    if d.get('make'): parts.append('make: ' + json.dumps(d['make']))
    if d.get('fish'): parts.append("fish: '%s'" % d['fish'])
    if d.get('kit'): parts.append('kit: 1')
    if d.get('belts'): parts.append('belts: ' + json.dumps(d['belts']))
    if d.get('wildRate'): parts.append('wildRate: %s' % d['wildRate'])
    return '  { ' + ', '.join(parts) + ',\n    board: ' + json.dumps(d['board'], ensure_ascii=False).replace('"', "'").replace("','", "', '") + ' }'
body = []
for i, d in enumerate(LV):
    if i % 5 == 0: body.append('  // ' + W[i // 5 % len(W)][0])
    body.append(lvdef(d) + (',' if i < len(LV) - 1 else ''))
block('const LEVELS = [', 'function levelConfig(L) {', 'const LEVELS = [\n' + '\n'.join(body) + '\n];\n')

# lessons count as seen for levels cleared in an older version (1-60); the new ones from 61 on are always shown once
rep("for (let L = 1; L < Math.min(maxLevel, LEVELS.length + 1); L++) { const id = LEVELS[L - 1].intro; if (id) learnt[id] = true; }",
    "for (let L = 1; L < Math.min(maxLevel, 61); L++) { const id = LEVELS[L - 1].intro; if (id) learnt[id] = true; }")

# ---------------- level 61: Hamsi, a jersey-shaped claret and blue board, the jersey to unlock ----------------
rep("  if (g.kind === 'collect') return n + ' ' + (n === 1 ? NAMES[g.type] : PLURAL[g.type]) + ' fressen';",
    "  if (g.kind === 'collect') return n + ' ' + (g.type === 0 && cfg && cfg.fish ? cfg.fish : n === 1 ? NAMES[g.type] : PLURAL[g.type]) + ' fressen';")
rep("  cfg.turbo = def.turbo || 0; cfg.goldRate = def.goldrush ? .08 : .015;", "  cfg.turbo = def.turbo || 0; cfg.goldRate = def.goldrush ? .05 : .015; cfg.fish = loop ? null : def.fish || null; cfg.kit = loop ? 0 : def.kit || 0;")
rep("""  let o = '', f = '', k = '';
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (mask[r][c]) {
    o += `<rect x="${c * 100}" y="${r * 100}" width="100" height="100" rx="20"/>`;
    f += `<rect x="${c * 100 - 1}" y="${r * 100 - 1}" width="102" height="102" rx="16"/>`;
    if ((r + c) % 2) k += `<rect x="${c * 100 + 7}" y="${r * 100 + 7}" width="86" height="86" rx="16"/>`;
  }
  $('boardwrap').insertAdjacentHTML('afterbegin', `<svg class="tray" viewBox="0 0 800 800" aria-hidden="true"><g fill="none" stroke="var(--trayLine)" stroke-width="22">${o}</g><g fill="var(--trayFill)">${f}</g><g fill="var(--trayAlt)">${k}</g></svg>`);""",
"""  let o = '', f = '', k = '', fb = '', kb = '';
  const kit = cfg && cfg.kit;
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (mask[r][c]) {
    // the jersey level: claret body, sky-blue sleeves
    const blue = kit && r <= 2 && (c <= 1 || c >= 6);
    o += `<rect x="${c * 100}" y="${r * 100}" width="100" height="100" rx="20"/>`;
    const fr = `<rect x="${c * 100 - 1}" y="${r * 100 - 1}" width="102" height="102" rx="16"/>`; if (blue) fb += fr; else f += fr;
    if ((r + c) % 2) { const kr = `<rect x="${c * 100 + 7}" y="${r * 100 + 7}" width="86" height="86" rx="16"/>`; if (blue) kb += kr; else k += kr; }
  }
  $('boardwrap').insertAdjacentHTML('afterbegin', `<svg class="tray" viewBox="0 0 800 800" aria-hidden="true"><g fill="none" stroke="${kit ? '#4A0B1F' : 'var(--trayLine)'}" stroke-width="22">${o}</g><g fill="${kit ? '#8C1D40' : 'var(--trayFill)'}">${f}</g><g fill="${kit ? '#A12B52' : 'var(--trayAlt)'}">${k}</g>` +
    (kit ? `<g fill="#4DA9E0">${fb}</g><g fill="#6CC4F0">${kb}</g>` : '') + `</svg>`);""")
rep("  const words = ['Geschafft!', 'Pfotastisch!', 'Miau-tastisch!', 'Schnurr-fekt!'];", "  const words = cfg && cfg.kit ? ['Bordo-Mavi!'] : ['Geschafft!', 'Pfotastisch!', 'Miau-tastisch!', 'Schnurr-fekt!'];")
rep("  confetti(100); victory(); duck(true); buzz([40, 60, 40, 60, 90]);", "  if (cfg && cfg.kit) kitConfetti(110); else confetti(100); victory(); duck(true); buzz([40, 60, 40, 60, 90]);")
# winning it unlocks the jersey; the reveal comes on the map
rep("function showEnd(won) {\n  cancelAim(true); clearPreview(); lastWon = won;", "function showEnd(won) {\n  cancelAim(true); clearPreview(); lastWon = won;\n  if (won && cfg.kit && !owned.includes('trikot')) { owned.push('trikot'); saveJar(); kitNew = true; }")
rep("  mapAnimating = false;\n  if (onMap && isUnlocked('chest') && !learnt.chest", "  mapAnimating = false;\n  if (onMap && kitNew) { kitNew = false; await showKit(); }\n  if (onMap && isUnlocked('chest') && !learnt.chest")
# the outfit list: the jersey is locked until level 61 is won
rep("    const has = owned.includes(o.id), on = wear === o.id;\n    const tag = on ? 'Ablegen' : has ? 'Anziehen' : asking === o.id ? 'Kaufen?' : `<span class=\"price\">${KIB_ICON}${o.price}</span>`;",
    "    const has = owned.includes(o.id), on = wear === o.id, locked = !!o.level && !has;\n    const tag = on ? 'Ablegen' : has ? 'Anziehen' : locked ? 'Ab Level ' + o.level : asking === o.id ? 'Kaufen?' : `<span class=\"price\">${KIB_ICON}${o.price}</span>`;")
rep("${!has && treats < o.price ? ' disabled' : ''}>${CAT_ICON(o.id)}", "${!has && (locked || treats < o.price) ? ' disabled' : ''}>${CAT_ICON(o.id)}")
# the map sprite wears it too
rep("  return `<div class=\"fwrap\"><i class=\"fshadow\"></i><div class=\"fsprite\"><div class=\"ffront\">${FREYR_BODY}<div class=\"fhead\">${CAT_ICON()}</div></div>${FREYR_BACK}</div></div>`;",
    "  return `<div class=\"fwrap\"><i class=\"fshadow\"></i><div class=\"fsprite\">${freyrInner()}</div></div>`;")
rep("  document.querySelectorAll('.fhead').forEach(e => { e.innerHTML = CAT_ICON(); });", "  document.querySelectorAll('.fsprite').forEach(e => { e.innerHTML = freyrInner(); });")

# ---------------- the new code goes in after the lessons, before the boot ----------------
rep("\naddEventListener('resize', sizeFx);\n", "\n" + R('art12.js') + R('feat12.js') + R('feat23.js') + R('intro25.js') + R('feat26.js') + R('vfx28.js') + R('game27.js') + R('perf28.js') + R('game30.js') + R('game31.js') + R('game32.js') + R('game33.js') + R('game35.js') + R('game36.js') + R('game37.js') + "\naddEventListener('resize', sizeFx);\n")

# ---- map walk without the 3D camera tilt: the map stays flat, Freyr walks; scroll only if the path is out of view
rep("""// the walk, filmed in 3D: the camera tips the map back, Freyr turns around and walks up the path
async function walkTo(a, midway) {
  const geo = mapGeo, seg = geo.seg(a), inner = $('mapInner'), map = $('map'), k = inner.offsetWidth / 400;
  const stand = $('mFreyr'), walker = $('mWalker'), mark = $('mMark');
  const mid = bez(seg, .5);
  map.scrollTop = mid.y * k - map.clientHeight * .52;
  walker.innerHTML = freyrSprite(); walker.hidden = false;""",
"""// the walk: the map stays flat, Freyr turns around and walks up the path to the next level
async function walkTo(a, midway) {
  const geo = mapGeo, seg = geo.seg(a), inner = $('mapInner'), map = $('map'), k = inner.offsetWidth / 400;
  const stand = $('mFreyr'), walker = $('mWalker'), mark = $('mMark');
  const mid = bez(seg, .5), ys = [seg.a.y, mid.y, seg.b.y].map(y => y * k);
  // scroll only when the path is not fully in view (top bar and Freyr's height included), and then gently
  if (Math.min(...ys) - 80 < map.scrollTop + 84 || Math.max(...ys) + 24 > map.scrollTop + map.clientHeight - 24) {
    const from = map.scrollTop, to = mid.y * k - map.clientHeight * .52;
    if (REDUCED) map.scrollTop = to;
    else await new Promise(res => {
      const t0 = performance.now();
      const f = now => { const t = mapSkip ? 1 : Math.min(1, (now - t0) / 420), e = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; map.scrollTop = from + (to - from) * e; if (t < 1) requestAnimationFrame(f); else res(); };
      requestAnimationFrame(f);
    });
  }
  walker.innerHTML = freyrSprite(); walker.hidden = false;""")
rep("""  map.style.overflowY = 'hidden';
  inner.style.transformOrigin = `${(mid.x * k).toFixed(1)}px ${(mid.y * k).toFixed(1)}px`;
  const TILT = 'perspective(720px) rotateX(38deg) scale(1.32)';
  let cam = null;
  inner.style.willChange = 'transform';
  if (!REDUCED) { cam = inner.animate([{ transform: 'none' }, { transform: TILT }], { duration: 750, easing: 'cubic-bezier(.45,0,.2,1)', fill: 'forwards' }); whoosh(0); walker.classList.add('tilted'); }
  await follow(cam, seg.a, LIFT);""",
"""  map.style.overflowY = 'hidden';
  const cam = null;
  await follow(cam, seg.a, LIFT);
  if (!REDUCED && !mapSkip) await mwait(180);""")
# ---- rounder map path: a longer wave, so the bends between the level dots are about twice as wide
rep("const nodeX = L => 200 + 108 * Math.sin((L - 1) * 1.1 + .4);", "const nodeX = L => 200 + 108 * Math.sin((L - 1) * .75 + .4);")
# ---- the paw treat: a creamy white kitty paw, so it stands apart from the brown kibble
rep('<radialGradient id="gYellow" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFF8CC"/><stop offset=".45" stop-color="#FFC21A"/><stop offset="1" stop-color="#DD6F00"/></radialGradient>',
    '<radialGradient id="gYellow" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFF8CC"/><stop offset=".45" stop-color="#FFC21A"/><stop offset="1" stop-color="#DD6F00"/></radialGradient>'
    '<radialGradient id="gPaw" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#FFF4E2"/><stop offset="1" stop-color="#F6BD72"/></radialGradient>')
rep("<g fill=\"url(#gYellow)\" ${OL('#B05400')}><ellipse cx=\"50\" cy=\"64\"", "<g fill=\"url(#gPaw)\" ${OL('#C46A12')}><ellipse cx=\"50\" cy=\"64\"")
# ---- after the zoomies the leftover extras go off
rep("  if (n) lastBonus += await zoomiesFinale(n);\n", "  if (n) lastBonus += await zoomiesFinale(n);\n  lastBonus += await extrasFinale();\n")
rep("  if (won) text = lastBonus ? 'Davon Zoomies-Bonus: +' + lastBonus.toLocaleString('de-DE') : catName + ' ist satt und glücklich.';",
    "  if (won) text = lastBonus ? (lastFire ? (lastBonus > lastFire ? 'Davon Bonus für Zoomies und Feuerwerk: +' : 'Davon Feuerwerk-Bonus: +') : 'Davon Zoomies-Bonus: +') + lastBonus.toLocaleString('de-DE') : catName + ' ist satt und glücklich.';")
# ---- stronger colors: deeper treat gradients
rep('<radialGradient id="gBlue" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#D8F4FF"/><stop offset=".42" stop-color="#43B6FF"/><stop offset="1" stop-color="#0F5FCB"/></radialGradient>', '<radialGradient id="gBlue" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#D6F2FF"/><stop offset=".42" stop-color="#2AA4FF"/><stop offset="1" stop-color="#0A4CB4"/></radialGradient>')
rep('<radialGradient id="gPink" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFE0EF"/><stop offset=".42" stop-color="#FF4FA3"/><stop offset="1" stop-color="#B80F66"/></radialGradient>', '<radialGradient id="gPink" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFDCEC"/><stop offset=".42" stop-color="#FF3393"/><stop offset="1" stop-color="#A1075A"/></radialGradient>')
rep('<radialGradient id="gWhite" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#EEE8FA"/><stop offset="1" stop-color="#9C8CC4"/></radialGradient>', '<radialGradient id="gWhite" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#ECE4FA"/><stop offset="1" stop-color="#8C78C6"/></radialGradient>')
rep('<radialGradient id="gPurple" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#F1DCFF"/><stop offset=".42" stop-color="#A75CFF"/><stop offset="1" stop-color="#5419BD"/></radialGradient>', '<radialGradient id="gPurple" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#EFD6FF"/><stop offset=".42" stop-color="#9744FF"/><stop offset="1" stop-color="#4510AC"/></radialGradient>')
rep('<radialGradient id="gGreen" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#E6FFCF"/><stop offset=".45" stop-color="#5ED83C"/><stop offset="1" stop-color="#1A8628"/></radialGradient>', '<radialGradient id="gGreen" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#E2FFC8"/><stop offset=".45" stop-color="#45CC22"/><stop offset="1" stop-color="#127A1E"/></radialGradient>')
rep('<radialGradient id="gRed" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFD4DE"/><stop offset=".42" stop-color="#FF2D55"/><stop offset="1" stop-color="#9E001E"/></radialGradient>', '<radialGradient id="gRed" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFD0DA"/><stop offset=".42" stop-color="#FF1F4B"/><stop offset="1" stop-color="#8E0019"/></radialGradient>')
rep('<radialGradient id="gKib" gradientUnits="userSpaceOnUse" cx="36" cy="30" r="66"><stop offset="0" stop-color="#F6BE85"/><stop offset=".45" stop-color="#C7763A"/><stop offset="1" stop-color="#6E3510"/></radialGradient>', '<radialGradient id="gKib" gradientUnits="userSpaceOnUse" cx="36" cy="30" r="66"><stop offset="0" stop-color="#F7BA7C"/><stop offset=".45" stop-color="#C26A2A"/><stop offset="1" stop-color="#5E2A08"/></radialGradient>')
# ---- stronger colors on the map: richer hills and meadow patches, a clearer road edge
rep("const HILL = [['#FFC4E0', '#D7F7C2'], ['#FFFFFF', '#E3D6FF'], ['#5A43B5', '#2F2380'], ['#FFE6BC', '#9EE6F2']][k];",
    "const HILL = [['#FFA3CF', '#B4EC96'], ['#FFFFFF', '#D6C4FF'], ['#5A43B5', '#2F2380'], ['#FFD594', '#78DBF0']][k];")
rep('fill="#D2F2B8" opacity=".55"', 'fill="#B6EB92" opacity=".6"')
rep('stroke="#DDB0F2" stroke-width="34"', 'stroke="#C88AEA" stroke-width="34"')

# ======================= V23: fixes from the full audit =======================
# opening the settings does not pop up the keyboard
rep("renderOutfits(); $('setOv').classList.add('show'); $('nameIn').focus(); }", "renderOutfits(); $('setOv').classList.add('show'); }")
# gold: a short callout with what is left on gold rush levels, and Freyr only says it once per level
rep("      else if (golds) text = 'Goldenes Leckerli!';",
    "      else if (golds) { const gg = goals.find(g => g.kind === 'gold'); if (gg) { text = 'Gold!'; if (gg.left > 0) sub = 'noch ' + gg.left; } else text = 'Goldenes Leckerli!'; }")
rep("      else if (golds) say(catName + ' hat ein goldenes Leckerli gefunden. '",
    "      else if (golds && !saidGold) say((saidGold = true, catName) + ' hat ein goldenes Leckerli gefunden. '")
# the jar text: the name is escaped, the list joins cleanly, hard levels say they pay double or triple
rep("""        : first ? 'Jeder übrige Zug bringt 1 Leckerli, höchstens ' + EARN_MAX + ' pro Level. Damit kaufst du ' + [TOOLS.some(toolOpen) && 'Hilfsmittel', isUnlocked('boosts') && 'Hilfe vor einem Level', '5 Extra-Züge in der Not', 'Outfits für ' + catName].filter(Boolean).join(', ').replace(/, ([^,]*)$/, ' oder $1') + '.'""",
    """        : first ? 'Jeder übrige Zug bringt 1 Leckerli, höchstens ' + EARN_MAX + ' pro Level' + (mult > 1 ? (mult > 2 ? ', in diesem Level dreifach' : ', in diesem Level doppelt') : '') + '. Damit kaufst du ' + orList([TOOLS.some(toolOpen) && 'Hilfsmittel', isUnlocked('boosts') && 'Hilfe vor einem Level', '5 Extra-Züge in der Not', 'Outfits für ' + esc(catName)].filter(Boolean)) + '.'""")
# housekeeping: an old unused function and CSS rules nothing uses any more
block("// one extra from the jar, placed on a random treat when the level starts\nfunction useBoost(id) {", "function showEnd(won) {", "")
for dead in [".hud-main{display:grid;grid-template-columns:1fr auto auto;gap:14px;align-items:center}\n",
             ".nums{font-size:.82rem;color:var(--muted);margin-top:3px;font-weight:700}\n", ".nums{display:none}\n",
             ".stat{text-align:center;min-width:46px}\n", ".iconrow{display:flex;gap:10px}\n", ".iconrow{gap:14px}\n",
             ".legendwrap-empty{display:none}\n", ".blabel{font-size:.82rem}\n",
             ".btarget{font:400 .92rem 'Lilita One','Nunito',sans-serif;color:#F0306A;min-width:2.6em;text-align:right}\n",
             "#custom{background:linear-gradient(#FFA6D3,#FF4F9A 55%,#DC1F76);box-shadow:inset 0 -4px 0 rgba(0,0,0,.12),0 0 0 3px #fff,0 0 0 5px #A80F57,0 7px 0 4px rgba(90,10,50,.25);text-shadow:0 2px 0 #A80F57,1px 0 #A80F57,-1px 0 #A80F57,0 -1px #A80F57}\n",
             "  main .iconrow{gap:8px}\n", "  main #custom{padding:11px 14px}\n", "  main .iconrow{gap:9px}\n", "  main #custom{padding:10px 12px;font-size:1rem}\n"]:
    rep(dead, "")

# ---- requests after the audit: the cat is always Freyr (no name field, no photo); the jersey stays a surprise
rep("""    <h2 class="disp" id="setTitle">Deine Katze</h2>
    <p>Dein Foto wird zur Katzen-Kachel und zur Katze oben.</p>
    <div class="field">
      <label for="nameIn">Name</label>
      <input type="text" id="nameIn" maxlength="20" autocomplete="off">
    </div>
    <div class="field">
      <span class="lbl">Foto</span>
      <div class="row">
        <button class="btn" id="photoBtn">Foto wählen</button>
        <button class="btn soft" id="photoDel">Zeichnung nehmen</button>
      </div>
      <input type="file" id="fileIn" accept="image/*" hidden>
    </div>
    <div class="field">
      <span class="lbl">Outfits <span class="bal" id="setBal"></span></span>
      <div class="outfits" id="outfits"></div>
    </div>
    <button class="btn" id="setDone">Speichern</button>""",
"""    <h2 class="disp" id="setTitle">Freyrs Outfits</h2>
    <p>Was zieht Freyr heute an?</p>
    <div class="field">
      <span class="lbl">Deine Leckerlis <span class="bal" id="setBal"></span></span>
      <div class="outfits" id="outfits"></div>
    </div>
    <button class="btn" id="setDone">Fertig</button>""")
rep("  photo = localStorage.getItem('wm-photo'); const nm = localStorage.getItem('wm-name'); catName = !nm || nm === 'Mieze' ? 'Freyr' : nm;\n",
    "  localStorage.removeItem('wm-photo'); localStorage.removeItem('wm-name');\n")
block("function save() {", "function say(text) {", "")
rep("function openSettings() { $('nameIn').value = catName; $('setFace')", "function openSettings() { $('setFace')")
rep("""  catName = $('nameIn').value.trim() || 'Freyr';
  save(); refreshCats(); $('setOv').classList.remove('show');""", """  refreshCats(); $('setOv').classList.remove('show');""")
rep("  say('Hi, ich bin ' + catName + '. Fütter mich!');\n}", "  say(wear ? 'Steht mir, oder?' : catName + ' hat Hunger. Fütter mich!');\n}")
block("$('photoBtn').onclick = () => $('fileIn').click();", "\n/* ---------- level map: scenery", "")
rep('<button class="mascot" id="mascot" aria-label="Deine Katze einrichten"></button>', '<button class="mascot" id="mascot" aria-label="Freyr"></button>')
rep('<div class="pi"><button class="mface" id="pCat" aria-label="Deine Katze einrichten"></button><span>Deine Katze</span></div>',
    '<div class="pi"><button class="mface" id="pCat" aria-label="Freyrs Outfits"></button><span>Outfits</span></div>')
rep('<button class="mface" id="mFace" aria-label="Deine Katze einrichten"></button>', '<button class="mface" id="mFace" aria-label="Freyrs Outfits"></button>')
rep("  $('outfits').innerHTML = OUTFITS.map(o => {", "  $('outfits').innerHTML = OUTFITS.filter(o => !o.level || owned.includes(o.id)).map(o => {")
rep("  trabzon: () => [CAT_ICON('trikot'), 'Ein Level für Trabzon!', catName + ' kommt aus Trabzon und ist riesiger Trabzonspor-Fan. Heute gibt es Hamsi vom Schwarzen Meer: Friss 61 Stück, dann bekommt ' + catName + ' sein Bordo-Mavi-Trikot!']",
    "  trabzon: () => [CAT_ICON(), 'Ein Level für Trabzon!', catName + ' kommt aus Trabzon und ist riesiger Trabzonspor-Fan. Heute gibt es Hamsi vom Schwarzen Meer: Friss 61 Stück!']")

# ---------------- V25: the intro, and his real bed at the start of the path ----------------
rep("if (L0 === 1) avoid.push({ x: geo.pts[0].x, y: geo.pts[0].y, r: 46 });", "if (L0 === 1) avoid.push({ x: geo.pts[0].x, y: geo.pts[0].y, r: 58 });")
rep("if (L0 === 1) decos.push({ k: 'basket', x: geo.pts[0].x, y: geo.pts[0].y, s: 1, r: 40 });", "if (L0 === 1) decos.push({ k: 'bed', x: geo.pts[0].x, y: geo.pts[0].y, s: 1, r: 50 });")
block("    if (o.k === 'basket') art +=", "    s += `<g transform=", "")
rep("\nshowMap();\n</script>", "\nstartGame();\n</script>")

# ---------------- V26: no jump button, a tap on Freyr is enough ----------------
rep('<button class="purrgo" id="purrGo" disabled>Sprung!</button>', '')
rep("  const go = $('purrGo'); go.disabled = !ready; go.classList.toggle('on', !!(aim && aim.kind === 'pounce'));\n", "")
rep("  const p = $('purrGo'); p.classList.remove('pop'); void p.offsetWidth; p.classList.add('pop');\n", "  purrReady();\n")
rep("mascot.onclick = tryPounce;\n$('purrGo').onclick = tryPounce;\n", "mascot.onclick = tryPounce;\n")
rep("e.target.closest('#board, .tools, #mascot, #purrGo, .overlay, #coach')", "e.target.closest('#board, .tools, #mascot, .overlay, #coach')")

# ---------------- V27: treats burst into pieces, new extras flash ----------------
rep("        burst(x, y, cell.gold ? 16 : (specials ? 6 : 4), cell.gold ? 1.6 : 1 + combo * .15);\n", "        popFx(k, cell, combo, specials);\n")
rep("      burst(x, y, ex.kind === 'bowl' ? 28 : 14, ex.kind === 'bowl' ? 1.8 : 1.2);\n", "      burst(x, y, ex.kind === 'bowl' ? 28 : 14, ex.kind === 'bowl' ? 1.8 : 1.2); spawnFx(k, ex.kind);\n")

# ---------------- V27: Schnurr-Power across levels, two bowls = a second helping, leftover moves become extras ----------------
rep("rescues = 0; pick = null; purr = 0; purrNew = false; askTool = null;", "rescues = 0; pick = null; purrNew = false; askTool = null;")
rep("const PURR_MAX = 15;", "const PURR_MAX = " + os.environ.get('PURRMAX', '60') + ";")
rep('<span class="ptxt" id="purrTxt">0 / 15</span>', '<span class="ptxt" id="purrTxt">0 / ' + os.environ.get('PURRMAX', '60') + '</span>')
rep("if (o.type === 'bowl') { a.eat = 'all'; pre = [kb]; label = 'Alles weg!'; }", "if (o.type === 'bowl') { a.eat = 'all'; pre = [kb]; label = 'Alles weg!'; feast2 = true; }")
rep("    const blast = new Set([ka, kb]); let label = null, pre = [];", "    const blast = new Set([ka, kb]); let label = null, pre = [], feast2 = false;")
rep("    await resolve(blast, null, label, pre);\n  } else if (findMatches().cells.size) {", "    await resolve(blast, null, label, pre);\n    if (feast2) await nachschlag();\n  } else if (findMatches().cells.size) {")
rep("  if (n) lastBonus += await zoomiesFinale(n);\n  lastBonus += await extrasFinale();", "  if (n) lastBonus += await zoomiesFinale(n);\n  if (moves > 0) await extraRain();\n  lastBonus += await extrasFinale();")

# ---------------- V28: smooth play — no layout in the hot path, tiles on transforms, treats as pictures ----------------
rep("const iconFor = x =>", "let iconFor = x =>")
rep("      d.style.transition = 'none'; d.style.left = (c * STEP) + '%'; d.style.top = (from * STEP) + '%';\n      if (from >= 0) d.classList.add('fadein');\n      fresh.push([cell, r, c, d]);",
    "      place(cell, r, c);\n      if (from >= 0) d.classList.add('fadein');\n      fresh.push([cell, r, c, d, from]);")
rep("  void boardEl.offsetHeight;\n  for (const [cell, r, c, d] of fresh) { d.style.transition = ''; place(cell, r, c); }",
    "  for (const [cell, r, c, d, from] of fresh) dropIn(d, c, from, r);")
rep("const m = mascot.getBoundingClientRect(), tx = m.left + m.width / 2, ty = m.top + m.height * .62;", "const m = mascotGeo(), tx = m.left + m.width / 2, ty = m.top + m.height * .62;")
# little animations restart without forcing a layout
for old, new, cnt in [
    ("mascot.classList.remove('bounce', 'eat'); void mascot.offsetWidth; mascot.classList.add('bounce');", "mascot.classList.remove('eat'); replay(mascot, 'bounce');", 1),
    ("mascot.classList.remove('bounce', 'eat'); void mascot.offsetWidth; mascot.classList.add('eat');", "mascot.classList.remove('bounce'); replay(mascot, 'eat');", 1),
    ("c.classList.remove('show'); void c.offsetWidth; c.classList.add('show');", "replay(c, 'show');", 1),
    ("w.classList.remove('shake'); void w.offsetWidth; w.classList.add('shake');", "replay(w, 'shake');", 1),
    ("mascot.classList.remove('bounce', 'eat', 'yuck'); void mascot.offsetWidth; mascot.classList.add('yuck');", "mascot.classList.remove('bounce', 'eat'); replay(mascot, 'yuck');", 1),
    ("e.classList.remove('wob'); void e.offsetWidth; e.classList.add('wob');", "replay(e, 'wob');", 1),
    ("el.classList.remove('hit'); void el.offsetWidth; el.classList.add('hit');", "replay(el, 'hit');", 2),
    ("el.classList.remove('nope'); void el.offsetWidth; el.classList.add('nope');", "replay(el, 'nope');", 2),
    ("m.classList.remove('bump'); void m.offsetWidth; m.classList.add('bump');", "replay(m, 'bump');", 2),
    ("el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump');", "replay(el, 'bump');", 1),
    ("w.classList.remove('shake', 'shake2'); void w.offsetWidth; w.classList.add('shake2');", "w.classList.remove('shake'); replay(w, 'shake2');", 1),
    ("boss.el.classList.remove('drive'); void boss.el.offsetWidth; boss.el.classList.add('drive');", "replay(boss.el, 'drive');", 1),
    ("boss.el.classList.remove('nope'); void boss.el.offsetWidth; boss.el.classList.add('nope');", "replay(boss.el, 'nope');", 1)]:
    rep(old, new, cnt)
# HUD text is only written when it changes; the zoomies runner glides on a transform
rep("  if (shownScore !== score) animateScore(); else $('score').textContent = score;\n  $('level').textContent = level;\n  $('moves').textContent = moves;",
    "  if (shownScore !== score) animateScore(); else setText($('score'), score);\n  setText($('level'), level);\n  setText($('moves'), moves);")
rep("  $('purrTxt').textContent = ready ? 'Voll!' : purr + ' / ' + PURR_MAX;", "  if (!ready) setText($('purrTxt'), purr + ' / ' + PURR_MAX);")
rep("  if (ready) $('purrTxt').textContent = aiming ? 'Tipp auf ein Feld' : 'Voll! Tipp auf ' + catName;", "  if (ready) setText($('purrTxt'), aiming ? 'Tipp auf ein Feld' : 'Voll! Tipp auf ' + catName);")
rep("$('purrTxt').textContent = 'Voll! Bleibt fürs nächste Level';", "setText($('purrTxt'), 'Voll! Bleibt fürs nächste Level');")
rep("el.animate([from, to], { duration: (d.keys.length + 1) * d.ms, easing: 'linear', fill: 'forwards' })", "runAnim(el, from, to, { duration: (d.keys.length + 1) * d.ms, easing: 'linear', fill: 'forwards' })")
# the walk on the map: where a map point lands on screen is measured once, not in every frame
rep("""  const place = (pt, lift) => {
    mark.style.left = pt.x * k + 'px'; mark.style.top = (pt.y * k - lift) + 'px';
    const r = mark.getBoundingClientRect(), sb = $('mapScreen').getBoundingClientRect(), sc = r.width / 40;
    walker.style.transform = `translate(${(r.left + r.width / 2 - sb.left).toFixed(1)}px,${(r.top + r.height / 2 - sb.top).toFixed(1)}px) scale(${sc.toFixed(3)}) translate(-50%,-100%)`;
  };""", "  const place = walkPlacer(mark, walker, k);")
# the map keeps its drawing when nothing in it changed (only buttons, banners and Freyr are rebuilt)
rep("  $('mapInner').innerHTML = s + h;", "  setMapHTML(s, h);")
# a swipe reads the board size from the shared measurement
rep("th = boardEl.clientWidth / N * .35", "th = boardGeo().w / N * .35")
# the cat's arrows: two little pictures that move as a whole (moving paths inside one drawing repainted it in every frame)
rep("""const DIR_SVG = d => `<svg class="dir" viewBox="0 0 100 100"><g${d === 'v' ? ' transform="rotate(90 50 50)"' : ''} fill="#fff" stroke="#E0146A" stroke-width="4.5" stroke-linejoin="round"><path class="al" d="M16 36 L2 50 L16 64Z"/><path class="ar" d="M84 36 L98 50 L84 64Z"/></g></svg>`;""",
    """const DIR_SVG = d => `<span class="dir dir2${d === 'v' ? ' v' : ''}" aria-hidden="true"><svg class="da al" viewBox="0 0 100 100"><path d="M16 36 L2 50 L16 64Z" fill="#fff" stroke="#E0146A" stroke-width="4.5" stroke-linejoin="round"/></svg><svg class="da ar" viewBox="0 0 100 100"><path d="M84 36 L98 50 L84 64Z" fill="#fff" stroke="#E0146A" stroke-width="4.5" stroke-linejoin="round"/></svg></span>`;""")
# the score counts up at the same speed, but the number is written every second frame
rep("  const step = () => {\n    shownScore = Math.min(score, shownScore + Math.max(1, Math.ceil((score - shownScore) * .18)));\n    el.textContent = shownScore;",
    "  let fr = 0;\n  const step = () => {\n    shownScore = Math.min(score, shownScore + Math.max(1, Math.ceil((score - shownScore) * .18)));\n    if ((fr++ & 1) === 0 || shownScore >= score) el.textContent = shownScore;")
# ---------------- V30: three hearts a bit easier, the bed goes where Freyr slept ----------------
rep("const HEART2 = .15, HEART3 = .35;", "const HEART2 = " + os.environ.get('HEART2', '.1') + ", HEART3 = " + os.environ.get('HEART3', '.28') + ";")
rep("  if (L0 === 1) decos.push({ k: 'bed', x: geo.pts[0].x, y: geo.pts[0].y, s: 1, r: 50 });\n", "  decos = bedDecos(geo, decos);\n")
# earlier worlds come back on the map when asked (the sign at the bottom)
rep("const lastW = Math.max(3, Math.floor((maxLevel - 1) / 5) + 1), firstW = Math.max(0, lastW - 4);", "const lastW = Math.max(3, Math.floor((maxLevel - 1) / 5) + 1), firstW = Math.max(0, lastW - 4 - mapBack);")
# V35: in his speech bubble Freyr talks about himself as "ich" (before: "Freyr kann nicht mehr aufhören zu fressen")
for a, b in [
    ("say('Nassfutter auf der Kuscheldecke?! ' + catName + ' ist empört.');", "say('Nassfutter auf meiner Kuscheldecke?! Ich bin empört.');"),
    ("catName + ' rümpft die Nase.'", "'Ich rümpf die Nase.'"),
    ("say((saidGold = true, catName) + ' hat ein goldenes Leckerli gefunden. '", "say((saidGold = true, 'Ich hab ein goldenes Leckerli gefunden! ')"),
    ("say('Puh! Kein Nassfutter mehr. ' + catName + ' atmet auf.');", "say('Puh! Kein Nassfutter mehr. Ich atme auf.');"),
    ("say('Alle Gurken sind weg. ' + catName + ' traut sich wieder raus.');", "say('Alle Gurken sind weg. Ich trau mich wieder raus.');"),
    ("say(catName + ' liebt seine Kuscheldecke. Mehr davon!');", "say('Ich liebe meine Kuscheldecke. Mehr davon!');"),
    ("say(catName + ' kann nicht mehr aufhören zu fressen.');", "say('Ich kann nicht mehr aufhören zu fressen!');"),
    ("say('Die Gurke fasst ' + catName + ' nicht an! Mach ein Match direkt daneben, dann ist sie weg.');", "say('Die Gurke fass ich nicht an! Mach ein Match direkt daneben, dann ist sie weg.');"),
    ("say(catName + ' springt ein letztes Mal!');", "say('Ich springe ein letztes Mal!');"),
    ("say('Noch 5 Züge. ' + catName + ' zählt auf dich!');", "say('Noch 5 Züge. Ich zähl auf dich!');"),
    ("say(n ? catName + ' ist satt und kriegt die Zoomies!' : catName + ' ist satt und glücklich!');", "say(n ? 'Ich bin satt und krieg die Zoomies!' : 'Ich bin satt und glücklich!');"),
    ("const hungry = [' hat Hunger!', ' schaut dich mit großen Augen an.', ' hätte gern einen Cremesnack. Oder zwei.', ' wartet geduldig. Fast.', ' hat schon wieder Hunger.'];",
     "const hungry = ['Ich hab Hunger!', 'Ich schau dich mit großen Augen an.', 'Ich hätte gern einen Cremesnack. Oder zwei.', 'Ich warte geduldig. Fast.', 'Ich hab schon wieder Hunger.'];"),
    ("say(catName + hungry[level === 1 ? 0 : Math.floor(Math.random() * hungry.length)]);", "say(hungry[level === 1 ? 0 : Math.floor(Math.random() * hungry.length)]);"),
    ("say('Weiter geht\\u2019s! ' + catName + ' glaubt an dich.');", "say('Weiter geht\\u2019s! Ich glaub an dich.');"),
    ("catName + ' hat Hunger. Fütter mich!'", "'Ich hab Hunger. Fütter mich!'"),
    ("say(catName + ' ist bereit zum Sprung. Tipp ihn an!');", "say('Ich bin bereit zum Sprung. Tipp mich an!');"),
    ("say('Geschafft! Der Staubsauger ist aus. ' + catName + ' ist sehr stolz auf dich.');", "say('Geschafft! Der Staubsauger ist aus. Ich bin sehr stolz auf dich.');"),
    ("catName + ' macht einen Buckel.'", "'Ich mach einen Buckel.'"),
    ("catName + ' springt erschrocken zur Seite.'", "'Ich spring erschrocken zur Seite.'"),
    ("say(catName + ' trägt jetzt Bordo-Mavi. Bereit für das nächste Spiel!');", "say('Ich trag jetzt Bordo-Mavi. Bereit für das nächste Spiel!');"),
    ("'Laserpunkt! Tausch ihn, dann jagt ' + catName + ' 3 Leckerlis quer übers Feld.'", "'Laserpunkt! Tausch ihn, dann jag ich 3 Leckerlis quer übers Feld.'"),
    ("'Festmahl-Napf! Tausch ihn mit einem Leckerli, dann frisst ' + catName + ' alle von der Sorte.'", "'Festmahl-Napf! Tausch ihn mit einem Leckerli, dann fress ich alle von der Sorte.'"),
    ("pounce: () => 'Tipp auf ein Feld: ' + catName + ' springt drauf und räumt Reihe und Spalte ab'", "pounce: () => 'Tipp auf ein Feld: Ich springe drauf und räume Reihe und Spalte ab'"),
    # the purr bar: shorter text, it has to fit in one line
    ("setText($('purrTxt'), 'Voll! Bleibt fürs nächste Level');", "setText($('purrTxt'), 'Fürs nächste Level');"),
    ("if (ready) setText($('purrTxt'), aiming ? 'Tipp auf ein Feld' : 'Voll! Tipp auf ' + catName);", "if (ready) setText($('purrTxt'), aiming ? 'Tipp auf ein Feld' : 'Tipp auf ' + catName + '!');"),
]:
    rep(a, b)
# V36: hooks for the new things (game36.js): goal icons can be extended, matches light dark cells, the fish falls in now and then, the bowl and the fish
rep("const goalIcon = g =>", "let goalIcon = g =>")
rep("if (milk[r][c] > 0) { milk[r][c]--; lick(r, c, d); licks.push(d); }", "if (milk[r][c] > 0) { milk[r][c]--; lick(r, c, d); licks.push(d); }\n      if (dark.length) lightAt(r, c, d);")
rep("cell = mk(rnd(), cfg.gold && Math.random() < cfg.goldRate);", "cell = mk(rnd(), cfg.gold && Math.random() < cfg.goldRate); if (cfg.wildRate && !cell.gold && Math.random() < cfg.wildRate && countOnBoard(x => x.type === 'wild') < 2) cell.type = 'wild';")
rep("if (sp.type === 'bowl') sp.eat = o.type;", "if (sp.type === 'bowl') sp.eat = o.type === 'wild' ? bestColor() : o.type;")
# V37: the chomp: chewing bursts from Freyr's own recordings (6 recordings, 22 bursts of 0.75 s, mk_chomp37.py), one per 0.85 s slot; played by game37.js
if os.path.exists(D + 'chomp37.json'):
    import re as _re
    _c = json.load(open(D + 'chomp37.json'))
    assert len(_re.findall(r"const CHOMP_B64 = '[A-Za-z0-9+/=]+';", s)) == 1 and len(_re.findall(r"const CHOMPS = \[[0-9., ]+\];", s)) == 1
    s = _re.sub(r"const CHOMP_B64 = '[A-Za-z0-9+/=]+';", lambda m: "const CHOMP_B64 = '" + _c['b64'] + "';", s)
    s = _re.sub(r"const CHOMPS = \[[0-9., ]+\];", lambda m: "const CHOMPS = " + json.dumps(_c['offs']) + ";", s)
# V38: an extra swapped with a treat: when the treat makes a match where it lands, that match is eaten as well and earns its extra
# (it used to go off with the blast only, so the four in a row it made never became a cat). Not for the bowl (it eats the whole kind)
# and not for two extras (their combo is the move).
rep("    await resolve(blast, null, label, pre);",
    "    await resolve(blast, (sa && sb) || (sa ? a : b).type === 'bowl' ? null : [[r1, c1], [r2, c2]], label, pre);")
rep("    if (blast) { blast.forEach(k => clear.add(k)); if (bd) bd.forEach((d, k) => delay.set(k, d)); blast = null; bd = null; }",
    "    if (blast) {\n      blast.forEach(k => clear.add(k)); if (bd) bd.forEach((d, k) => delay.set(k, d)); blast = null; bd = null;\n"
    "      if (combo === 0 && swapKeys.length) { const m = findMatches(); if (m.cells.size) { m.cells.forEach(k => clear.add(k)); spawns = extrasFor(m, swapKeys); } }\n    }")
# V38: bells: a random column that gets new treats, never the column the last bell came down in. A bell that has just dropped out
# leaves a gap only in its own column, so it used to come right back there; now the next one waits for a gap elsewhere
# (after two passes with no other gap it may take the same column). How often bells come stays as it was.
rep("function gravity() {", "let lastBellCol = -1, bellWait = 0;\nfunction gravity() {")
rep("  const bellCol = bellNow ? Math.floor(Math.random() * N) : -1;",
    "  let bellCol = -1;\n"
    "  if (bellNow) {\n"
    "    const free = [], hasBell = c => grid.some(row => row[c] && row[c].type === 'bell');\n"
    "    for (let c = 0; c < N; c++) { for (let r = 0; r < N; r++) if (mask[r][c] && !grid[r][c]) { free.push(c); break; } }\n"
    "    const pick0 = Math.floor(Math.random() * N);\n"
    "    if (onBoard && !free.some(c => c >= pick0)) bellNow = false;\n"
    "    else {\n"
    "      let pool = free.filter(c => c !== lastBellCol && !hasBell(c));\n"
    "      if (!pool.length && !onBoard && ++bellWait > 2) pool = free;\n"
    "      if (pool.length) { bellCol = pool[Math.floor(Math.random() * pool.length)]; bellWait = 0; } else bellNow = false;\n"
    "    }\n"
    "  }")
rep("      if (bellNow && (c >= bellCol || c === N - 1 || !onBoard) && i === slots.length - 1) { cell = mk('bell'); bellsLeft--; bellNow = false; }",
    "      if (bellNow && c === bellCol && i === slots.length - 1) { cell = mk('bell'); bellsLeft--; bellNow = false; lastBellCol = c; }")
# (the column a bell just dropped out of counts as well, also for the bells that were on the board from the start)
rep("    n++; grid[low][c] = null;\n    const el = els.get(x.id), [px, py] = cellXY(low * N + c);",
    "    n++; grid[low][c] = null; lastBellCol = c;\n    const el = els.get(x.id), [px, py] = cellXY(low * N + c);")
# V35: the game is called Freyr Match now
rep('<title>Whisker Match</title>', '<title>Freyr Match</title>')
open(D + os.environ.get('OUT12', 'game.html'), 'w').write(s)
print('patched', len(s), 'levels', len(LV))
