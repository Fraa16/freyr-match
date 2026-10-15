"""V41: Freyr's letter and the test level, the pair rule as the game's own.
N1 a returning player gets the letter on start (no wake-up scene), Freyr reads it line by line
N2 the letter can't be closed: Escape, a tap beside it, the browser's back key do nothing; the button comes once it is read (a tap speeds it up)
N3 the button starts the test level: no life spent, the coach shows the first step
N4 the coach steps: a Flitzekatze is made, shown, set off with two of its treats; two extras together; two bowls
N5 the free part: 3 extras alone; the level ends with Freyr's card, the letter is marked as read
N6 nothing else changed: level, lives, treats, hearts, streak
N7 leaving the test level from the pause menu brings the letter back
N8 a new player never gets the letter
N9 the lessons for new players teach the pair rule (cat, laser, nip), and the level cards say so
N10 the letter in the dark theme and on a small phone (screenshots)"""
import os, sys, json
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
GAME = os.environ.get('GAME', 'game.html')
SHOTS = D + '/shots41'; os.makedirs(SHOTS, exist_ok=True)
fails = []
def ok(m, c, info=None):
    print(('OK   ' if c else 'FAIL ') + m + ('' if c or info is None else '  ' + json.dumps(info)[:500]))
    if not c: fails.append(m)
STATE = "() => ({ level, maxLevel, lives, treats, streak: typeof winStreak !== 'undefined' ? winStreak : null, hearts: JSON.stringify(bestHearts()), onMap, news: localStorage.getItem('wm-news41') })"
# plays the coach: does the shown swap, taps Weiter; returns the steps it saw
DRIVE = """async () => {
  const seen = [], t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    await new Promise(r => setTimeout(r, 120));
    if (!TRY41) return { seen, end: 'no try' };
    if (TRY41.count && !tut) return { seen, end: 'free' };
    if (!tut || busy) continue;
    const e = tut.expect, txt = tutEls && tutEls.text.textContent;
    if (e && e.type === 'turn' && e.pair) {
      const [a, b] = e.pair; seen.push(['move', txt]);
      const kinds = [a, b].map(k => { const x = grid[k / N | 0][k % N]; return x.type + (x.col != null ? ':' + x.col : ''); });
      seen[seen.length - 1].push(kinds);
      await trySwap(a / N | 0, a % N, b / N | 0, b % N);
    } else if (!e && tut.res && tutEls && !tutEls.next.hidden) { seen.push(['info', txt]); tutEls.next.click(); }
  }
  return { seen, end: 'timeout' };
}"""
FREE = """async () => {
  const t0 = Date.now(); let turns = 0;
  while (Date.now() - t0 < 90000) {
    await new Promise(r => setTimeout(r, 100));
    if (document.getElementById('news41end')) return { turns, end: 'card', left: goals[0].left, moves };
    if (busy || !TRY41) continue;
    const m = bestMove(); if (!m) continue;
    turns++; await trySwap(m.r, m.c, m.r2, m.c2);
  }
  return { turns, end: 'timeout', left: goals[0] && goals[0].left };
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    def page(w=402, h=874, dark=False):
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True, color_scheme='dark' if dark else 'light')
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.errs = errs
        return pg
    def returning(pg, extra=''):
        pg.goto('file://' + D + '/' + GAME)
        pg.evaluate("localStorage.clear(); localStorage.setItem('wm-intro','1'); localStorage.setItem('wm-level','30'); localStorage.setItem('wm-purr-told','1'); localStorage.setItem('wm-music','off');"
                    "localStorage.setItem('wm-learn', JSON.stringify({basics:1,cat:1,laser:1,nip:1,bowl:1,combo:1,purr:1,chest:1})); " + extra)
        pg.reload(); pg.wait_for_timeout(500); fonts(pg)

    pg = page()
    returning(pg)
    pg.wait_for_selector('#news41', timeout=5000)
    st0 = pg.evaluate(STATE)
    ok('N1 the letter is there on start, over the map, no wake-up scene', pg.evaluate("!!document.getElementById('news41') && onMap && !introRun"))
    pg.wait_for_timeout(2600); pg.screenshot(path=SHOTS + '/1-brief-liest.png')
    shown = pg.evaluate("[...document.querySelectorAll('#news41 .n41l.on')].length"); total = pg.evaluate("document.querySelectorAll('#news41 .n41l').length")
    ok('N1 Freyr reads line by line (after 2.6 s some lines, not all)', 0 < shown < total, [shown, total])
    ok('N1 his mouth and eyes move while reading', pg.evaluate("document.querySelector('#news41 .n41face').classList.contains('read')"))
    ok('N2 no button while he reads', pg.evaluate("document.querySelector('#news41 .n41go').hidden"))
    pg.keyboard.press('Escape'); pg.mouse.click(8, 8); pg.wait_for_timeout(300)
    ok('N2 Escape and a tap beside it do not close it', pg.evaluate("!!document.getElementById('news41') && document.getElementById('news41').classList.contains('show')"))
    pg.click('#news41 .n41paper'); pg.wait_for_timeout(700)
    ok('N2 a tap on the letter shows the rest and the button', pg.evaluate("[...document.querySelectorAll('#news41 .n41l')].every(e => e.classList.contains('on')) && !document.querySelector('#news41 .n41go').hidden"))
    pg.screenshot(path=SHOTS + '/2-brief-ganz.png')
    full = pg.evaluate("(() => { const b = document.querySelector('#news41 .n41body'); b.scrollTop = 1e5; return [b.scrollHeight, b.clientHeight]; })()"); pg.wait_for_timeout(200)
    pg.screenshot(path=SHOTS + '/2b-brief-unten.png')
    ok('N2 the letter text, start to end', pg.evaluate("document.querySelector('#news41 .n41body').textContent").startswith('Post von Freyr') and 'PS: Ich hab Hunger.' in pg.evaluate("document.querySelector('#news41 .n41body').textContent"))
    ok('N2 the only button is the one into the test level', pg.evaluate("[...document.querySelectorAll('#news41 button')].map(b => b.textContent)") == ['Zum Testlevel'])
    pg.click('#news41 .n41go'); pg.wait_for_timeout(1500)
    st1 = pg.evaluate(STATE)
    ok('N3 the test level runs, the letter is gone', pg.evaluate("!!TRY41 && !onMap && !document.getElementById('news41')"))
    ok('N3 no life spent, level unchanged', st1['lives'] == st0['lives'] and st1['level'] == st0['level'] and st1['maxLevel'] == st0['maxLevel'], [st0, st1])
    ok('N3 the coach shows the first step', pg.evaluate("!!tut && tut.id === 'try41' && !tutEls.root.hidden"))
    ok('N3 the goal: 3 extras', pg.evaluate("goals.length === 1 && goals[0].kind === 'fire41' && goals[0].left === 3 && document.getElementById('goals').textContent.includes('3')"))
    pg.screenshot(path=SHOTS + '/3-test-schritt1.png')
    # the steps, with a screenshot of each coach card
    shots = pg.evaluate("""() => { window.__sh = []; const t0 = tutShow; tutShow = function (s) { window.__sh.push(s.text); return t0.apply(this, arguments); }; return true; }""")
    r = pg.evaluate(DRIVE)
    texts = [s[1] for s in r['seen']]
    print('   steps:', json.dumps(r['seen'], ensure_ascii=False)[:1200])
    ok('N4 the coach went through to the free part', r['end'] == 'free', r)
    moves_ = [s for s in r['seen'] if s[0] == 'move']
    ok('N4 Flitzekatze made, shown, set off with two treats, two extras, two bowls',
       len(moves_) == 4 and any('Vier gleiche' in t for t in texts) and any('steckt jetzt das Leckerli' in t for t in texts)
       and any('drei gleiche' in t for t in texts) and any('Zwei Extras miteinander' in t for t in texts) and any('zwei Näpfe' in t for t in texts), r['seen'])
    pair_move = [s for s in moves_ if 'drei gleiche' in s[1]]
    ok('N4 the pair step swaps two plain treats (the extra stays put)', pair_move and all(':' not in k and k.isdigit() for k in pair_move[0][2]), pair_move)
    combo = [s for s in moves_ if 'Zwei Extras' in s[1]]
    ok('N4 the combo step swaps two extras', combo and set(k.split(':')[0] for k in combo[0][2]) == {'cat', 'nip'}, combo)
    ok('N4 nothing counted while the coach shows things', pg.evaluate("goals[0].left") == 3)
    pg.wait_for_timeout(400); pg.screenshot(path=SHOTS + '/4-test-frei.png')
    ok('N5 three coloured extras wait on the board for the free part', pg.evaluate("(() => { let n = 0; for (const row of grid) for (const x of row) if (isColx(x)) n++; return n; })()") >= 2)
    f = pg.evaluate(FREE)
    ok('N5 three extras alone, then Freyr\'s card', f['end'] == 'card', f)
    pg.wait_for_timeout(600); pg.click('#news41end .n41paper'); pg.wait_for_timeout(500)
    pg.screenshot(path=SHOTS + '/5-geschafft.png')
    ok('N5 the letter counts as read', pg.evaluate("localStorage.getItem('wm-news41')") == 'done')
    pg.click('#news41end .n41go'); pg.wait_for_timeout(1600)
    st2 = pg.evaluate(STATE)
    ok('N6 level, lives, treats, hearts, streak as before', all(st2[k] == st0[k] for k in ['level', 'maxLevel', 'lives', 'treats', 'hearts', 'streak']), [st0, st2])
    ok('N6 back on the map, his level card opens', st2['onMap'] and pg.evaluate("$('introOv').classList.contains('show') && level === 30"))
    pg.evaluate("$('introOv').classList.remove('show')")
    pg.reload(); pg.wait_for_timeout(1500)
    ok('N6 after a restart no letter again', pg.evaluate("!document.getElementById('news41')"))
    ok('no page errors (run 1)', not pg.errs, pg.errs[:3]); pg.close()

    # N7: leaving from the pause menu
    pg = page()
    returning(pg); pg.wait_for_selector('#news41'); pg.click('#news41 .n41paper'); pg.wait_for_timeout(600); pg.click('#news41 .n41go'); pg.wait_for_timeout(1500)
    lives0 = pg.evaluate('lives')
    pg.evaluate("tutAbort(); openPause()"); pg.wait_for_timeout(400)
    ok('N7 the pause menu says Testlevel', pg.evaluate("$('pauseWhere').textContent") == 'Testlevel')
    pg.click('#toMap'); pg.wait_for_timeout(1400)
    ok('N7 leaving brings the letter back, no quit card, no life lost', pg.evaluate("!!document.getElementById('news41') && onMap && !TRY41 && !$('quitOv').classList.contains('show')") and pg.evaluate('lives') == lives0)
    ok('N7 still not read', pg.evaluate("localStorage.getItem('wm-news41')") is None)
    ok('no page errors (run 2)', not pg.errs, pg.errs[:3]); pg.close()

    # N8: a new player
    pg = page()
    pg.goto('file://' + D + '/' + GAME); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(1500)
    ok('N8 a new player: the intro film, no letter, and never later', pg.evaluate("!document.getElementById('news41') && localStorage.getItem('wm-news41') === 'done'"))
    pg.close()

    # N9: the lessons for a new player
    pg = page()
    returning(pg, "localStorage.setItem('wm-news41','done'); localStorage.setItem('wm-level','2'); localStorage.setItem('wm-learn', JSON.stringify({basics:1,purr:1,chest:1,milk:1,boxes:1}));")
    pg.wait_for_timeout(800)
    pg.evaluate("() => { document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1200)
    for kind in ['cat', 'laser', 'nip']:
        L = pg.evaluate("(k) => LEVELS.findIndex(d => d.intro === k) + 1", kind)
        pg.evaluate("(L) => { document.querySelectorAll('.overlay.show').forEach(o => o.classList.remove('show')); if (!onMap) showMap(); }", L); pg.wait_for_timeout(500)
        pg.evaluate("(L) => { maxLevel = L; openLevel(L); }", L); pg.wait_for_timeout(700)   # (what a new extra is, depends on what is unlocked at the player's level)
        card = pg.evaluate("$('introNew').textContent + ' | ' + $('tipline').textContent")
        ok('N9 level card %d (%s) explains the pair rule' % (L, kind), 'zwei gleichen Leckerlis' in card, card)
        if kind == 'cat': pg.screenshot(path=SHOTS + '/9-karte-flitzekatze.png')
        pg.click('#introBtn'); pg.wait_for_timeout(1500)
        r = pg.evaluate("""async () => { const seen = [], t0 = Date.now();
          while (Date.now() - t0 < 30000) { await new Promise(r => setTimeout(r, 120));
            if (!tut) return { seen, learnt: !!learnt[cfg.intro] }; if (busy) continue;
            const e = tut.expect;
            if (e && e.type === 'turn' && e.pair) { const [a, b] = e.pair; const ks = [a, b].map(k => grid[k / N | 0][k % N].type); seen.push([tutEls.text.textContent, ks]); if (seen.length === 2) await new Promise(r => setTimeout(r, 300)); await trySwap(a / N | 0, a % N, b / N | 0, b % N); }
            else if (!e && tut.res && !tutEls.next.hidden) tutEls.next.click(); }
          return { seen, timeout: true }; }""")
        ok('N9 lesson %s: made, then set off in a match of three' % kind, r.get('learnt') and len(r['seen']) == 2 and 'drei gleiche' in r['seen'][1][0] and all(isinstance(t, int) for t in r['seen'][1][1]), r)
    ok('no page errors (run 3)', not pg.errs, pg.errs[:3]); pg.close()

    # N10: dark theme, small phone
    for name, kw in [('10-dunkel', {'dark': True}), ('10b-klein', {'w': 375, 'h': 667})]:
        pg = page(**kw); returning(pg); pg.wait_for_selector('#news41'); pg.wait_for_timeout(500); pg.click('#news41 .n41paper'); pg.wait_for_timeout(700)
        pg.screenshot(path=SHOTS + '/' + name + '.png')
        ok('N10 %s: the button is on screen' % name, pg.evaluate("(() => { const r = document.querySelector('#news41 .n41go').getBoundingClientRect(); return r.bottom <= innerHeight && r.top > 0; })()"))
        ok('no page errors (%s)' % name, not pg.errs, pg.errs[:3]); pg.close()
    b.close()
print('FAILS', len(fails))
for f in fails: print('  ', f)
