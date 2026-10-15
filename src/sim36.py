"""bot sweep (V36: also the board problems and the moves used per run). heart sweep (V30): like audit_sim, but writes every run with the moves left, to see how often each heart count comes up.
audit sweep: plays every level fast (timers instant) with the casual bot and checks the board after every turn.
usage: python3 audit_sim.py L1,L2,.. RUNS OUT   (levels can be ranges like 1-80)"""
import sys, os, json, time, re
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
def parse(spec):
    out = []
    for part in spec.split(','):
        if '-' in part: a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else: out.append(int(part))
    return out
LEVELS = parse(sys.argv[1])
RUNS = int(sys.argv[2])
OUT = sys.argv[3]
OVR = json.load(open(os.environ['OVR'])) if os.environ.get('OVR') else None   # level overrides {L: {field: value}} for tuning without a rebuild
s = open(os.path.join(D, os.environ.get('SRC', 'game.html'))).read().replace("const sleep = ms => FF.on ? Promise.resolve() : ffWait(ms);", "const sleep = ms => new Promise(r => setTimeout(r, ms));").replace("const later = (ms, fn) => ms > 0 && !FF.on ? ffLater(ms, fn) : fn();", "const later = (ms, fn) => ms > 0 ? setTimeout(fn, ms) : fn();")
for old, new in [
    ("const sleep = ms => new Promise(r => setTimeout(r, ms));", "const sleep = ms => Promise.resolve();"),
    ("const later = (ms, fn) => ms > 0 ? setTimeout(fn, ms) : fn();", "const later = (ms, fn) => fn();"),
    ("const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;", "const REDUCED = true;"),
]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
s = re.sub(r'<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>', '', s)
simfile = os.path.join(D, 'asim_%d.html' % os.getpid())
open(simfile, 'w').write(s)

BOT = r'''
(() => {
  for (const f of ['burst','confetti','flyToCat','floatText','callout','say','chime','sparkle','coin','thud','extraSound','chomp','buzz','shake','fanfare','sad','blip','nope','jingle','whoosh','boing','pew','splorch','fluff','slurp','catYuck'])
    if (typeof window[f] === 'function') window[f] = () => {};
  window.__res = null;
  window.winSequence = async () => { window.__res = { won: true, left: moves }; };
  window.showEnd = (won) => { if (!window.__res) window.__res = { won: !!won, left: 0, rang: typeof clockRang !== 'undefined' && clockRang }; };
  let reshuffles = 0;
  const rs0 = reshuffle;
  window.reshuffle = reshuffle = function () { reshuffles++; return rs0(); };
  function check(tag) {
    const p = [], ids = new Set();
    for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
      const x = grid[r][c];
      if (!mask[r][c]) { if (x) p.push(tag + ' tile in hole ' + r + ',' + c); continue; }
      if (!x) { p.push(tag + ' empty ' + r + ',' + c); continue; }
      if (ids.has(x.id) && x.type !== 'boss') p.push(tag + ' dup id ' + r + ',' + c); ids.add(x.id);
      if (x.type == null) p.push(tag + ' no type ' + r + ',' + c);
    }
    for (const g of goals) { const n = remaining(g); if (!(n >= 0)) p.push(tag + ' bad remaining ' + g.kind + ' ' + n); }
    if (boss && boss.hp > 0) { let n = 0; for (const [r, c] of bossCellsAt(boss.r, boss.c)) if (grid[r][c] && grid[r][c].type === 'boss') n++; if (n !== 4) p.push(tag + ' boss cells ' + n); }
    return p;
  }
  window.auditLevel = async (L) => {
    level = L; maxLevel = L; window.__res = null; reshuffles = 0;
    startLevel();
    document.getElementById('introOv').classList.remove('show'); busy = false;
    const probs = [], start = { moves: countMoves(), has: hasMove(), matches: findMatches().cells.size };
    if (!start.has) probs.push('no move at start');
    if (start.matches) probs.push('matches at start');
    probs.push(...check('start'));
    let used = 0, stuck = 0, noMoveAfterTurn = 0;
    for (let guard = 0; guard < 120 && !window.__res; guard++) {
      if (purr >= PURR_MAX && moves > 0 && Math.random() < .7) {
        const t = bestPounce(); aim = { kind: 'pounce' }; await doAim(t.r, t.c);
        if (busy) probs.push('busy after pounce');
        probs.push(...check('pounce'));
        if (window.__res) break;
      }
      const mv = rankMoves();
      if (!mv.length) {
        noMoveAfterTurn++;
        reshuffle();
        if (!rankMoves().length) { stuck++; probs.push('STUCK: no move after reshuffle (moves left ' + moves + ')'); break; }
        continue;
      }
      let pick;
      if (Math.random() < .5) { mv.sort((a, b) => b.v - a.v); pick = mv[Math.floor(Math.random() * Math.ceil(mv.length / 2))]; }
      else { mv.forEach(m => m.n = m.v + Math.random() * 2); mv.sort((a, b) => b.n - a.n); pick = mv[0]; }
      await trySwap(pick.r, pick.c, pick.r2, pick.c2); used++;
      if (busy) probs.push('busy after turn');
      if (!window.__res) probs.push(...check('turn ' + used));
      if (probs.length > 12) break;
    }
    return { ...(window.__res || { won: false, left: 0 }), cm: cfg.moves, used, reshuffles, noMoveAfterTurn, stuck, probs: [...new Set(probs)].slice(0, 8), start };
  };
})();
'''
out = open(os.path.join(D, OUT), 'w')
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + simfile); pg.evaluate('localStorage.clear()')
    if os.environ.get('LS'): pg.evaluate('(o) => { for (const [k, v] of Object.entries(o)) localStorage.setItem(k, v); }', json.loads(os.environ['LS']))   # e.g. LS='{"wm-pair40":"off"}'
    pg.reload(); pg.wait_for_timeout(600)
    pg.evaluate(BOT)
    n = 0
    for L in LEVELS:
        t0 = time.time(); res = []
        for i in range(RUNS):
            if n % 20 == 0:
                pg.reload(); pg.wait_for_timeout(300); pg.evaluate(BOT)
                if OVR: pg.evaluate('(o) => { for (const [k, v] of Object.entries(o)) Object.assign(LEVELS[+k - 1], v); }', OVR)
            n += 1
            ne = len(errs)
            try:
                r = pg.evaluate('(L) => auditLevel(L)', L)
            except Exception as e:
                r = {'won': False, 'probs': ['EXC ' + str(e)[:200]], 'used': 0, 'reshuffles': 0, 'noMoveAfterTurn': 0, 'stuck': 0, 'start': {}}
                pg.reload(); pg.wait_for_timeout(300); pg.evaluate(BOT)
            if len(errs) > ne: r['probs'] = r.get('probs', []) + ['PAGEERR ' + e for e in errs[ne:]]
            res.append(r)
        out.write(json.dumps({'L': L, 'runs': [[1 if r['won'] else 0, r.get('left', 0), r.get('cm', 0), r.get('used', 0)] for r in res],
                              'probs': sorted(set(x for r in res for x in r.get('probs', [])))[:8], 'stuck': sum(r.get('stuck', 0) for r in res),
                              'resh': sum(r.get('reshuffles', 0) for r in res)}) + '\n'); out.flush()
        continue
        wins = sum(1 for r in res if r['won'])
        probs = sorted(set(x for r in res for x in r['probs']))
        row = {'L': L, 'win': wins / RUNS, 'resh': sum(r['reshuffles'] for r in res), 'nomove': sum(r['noMoveAfterTurn'] for r in res),
               'stuck': sum(r['stuck'] for r in res), 'startMoves': min(r['start'].get('moves', 99) for r in res), 'probs': probs[:10], 't': round(time.time() - t0, 1)}
        out.write(json.dumps(row) + '\n'); out.flush()
        print(json.dumps(row), flush=True)
    b.close()
os.remove(simfile)
