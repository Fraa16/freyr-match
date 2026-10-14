"""V28 performance benchmark: heavy scenes on a phone-sized page (390x844 at 3x), CPU throttled like a phone.
Per scene: frame times from requestAnimationFrame, long tasks, and the main-thread split (script, style, layout).
usage: GAME=game.html THROTTLE=4 SCENES=cascade,combo,bowl,bowlbowl,finale RUNS=2 OUT=perf.json python3 perf28.py"""
import os, sys, json, statistics
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import veteran
GAME = os.environ.get('GAME', 'game.html')
THROTTLE = float(os.environ.get('THROTTLE', '4'))
SCENES = os.environ.get('SCENES', 'cascade,combo,bowl,bowlbowl,finale').split(',')
RUNS = int(os.environ.get('RUNS', '2'))
DPR = float(os.environ.get('DPR', '3'))
HN = open(D + '/harness.js').read()
WAIT_MAP = """async () => { mapSkip = true; for (let i = 0; i < 160 && mapAnimating; i++) await new Promise(r => setTimeout(r, 50)); }"""
SEED = """(() => { let a = 1; window.__seed = s => { a = s >>> 0; }; Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; })();"""
FRESH = r"""(fixed) => {
  const types = [0, 1, 2, 3, 4, 5];
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) grid[r][c] = mask[r][c] ? mk(types[Math.floor(Math.random() * types.length)]) : null;
  for (const [r, c, t, dir] of fixed) { const x = mk(t); if (dir) x.dir = dir; grid[r][c] = x; }
  for (let it = 0; it < 60; it++) {
    const m = findMatches().cells; if (!m.size) break;
    for (const k of m) { const r = k / N | 0, c = k % N; if (!fixed.some(f => f[0] === r && f[1] === c)) grid[r][c] = mk(types[Math.floor(Math.random() * types.length)]); }
  }
  render(false);
}"""
IDLE = """() => !busy && !(typeof winRunning !== 'undefined' && winRunning) && parts.length === 0 && (typeof vfx === 'undefined' || vfx.length === 0) && (typeof lights === 'undefined' || lights.length === 0) && !document.querySelector('.fly')"""
REC_ON = """() => { window.__lt = []; try { const o = new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push(e.duration); }); o.observe({ type: 'longtask' }); window.__lto = o; } catch (e) {}
  window.__rec = { t: [], on: true }; const loop = t => { if (!window.__rec.on) return; window.__rec.t.push(t); requestAnimationFrame(loop); }; requestAnimationFrame(loop); }"""
REC_OFF = """() => { window.__rec.on = false; if (window.__lto) window.__lto.disconnect(); return { t: window.__rec.t, lt: window.__lt }; }"""
METRICS = ['TaskDuration', 'ScriptDuration', 'LayoutDuration', 'RecalcStyleDuration', 'LayoutCount', 'RecalcStyleCount']

def stats(ts):
    d = [ts[i + 1] - ts[i] for i in range(len(ts) - 1)]
    if not d: return {}
    s = sorted(d)
    q = lambda f: s[min(len(s) - 1, int(len(s) * f))]
    span = (ts[-1] - ts[0]) / 1000
    return dict(frames=len(d), span=round(span, 2), fps=round(len(d) / span, 1), p50=round(q(.5), 1), p95=round(q(.95), 1), p99=round(q(.99), 1),
                max=round(s[-1], 1), jank=round(100 * sum(1 for x in d if x > 20) / len(d), 1), bad=sum(1 for x in d if x > 50))

def mapscene(pg, name):
    """on the map: the walk to the next level after a first win, or a long scroll down the map"""
    pg.evaluate('__seed(4242)')
    cdp.send('Performance.enable'); m0 = {m['name']: m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
    if name == 'walk':
        pg.evaluate("() => { document.getElementById('endOv').classList.remove('show'); document.getElementById('introOv').classList.remove('show'); window.__ml = maxLevel; maxLevel = 9; level = 8; }")
        pg.evaluate(REC_ON)
        pg.evaluate("() => { showMap({ from: 8, first: true, oldBest: 0, newH: 3 }); }")
        pg.wait_for_timeout(300)
        pg.wait_for_function('!mapAnimating', timeout=60000, polling=100); pg.wait_for_timeout(300)
        pg.evaluate("() => { maxLevel = window.__ml; document.getElementById('introOv').classList.remove('show'); }")
    else:
        pg.evaluate("() => { document.getElementById('introOv').classList.remove('show'); if (!onMap) showMap(); }"); pg.wait_for_timeout(800)
        pg.evaluate('() => { const m = document.getElementById("map"); m.scrollTop = m.scrollHeight; }'); pg.wait_for_timeout(600)
        pg.evaluate(REC_ON)
        pg.evaluate("""() => new Promise(res => { const m = document.getElementById('map'), from = m.scrollTop, to = Math.max(0, from - 9000), t0 = performance.now();
          const f = now => { const t = Math.min(1, (now - t0) / 3000); m.scrollTop = from + (to - from) * t; if (t < 1) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); })""")
        pg.wait_for_timeout(200)
    r = pg.evaluate(REC_OFF)
    m1 = {m['name']: m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
    st = stats(r['t']); st['long'] = len(r['lt']); st['longmax'] = round(max(r['lt']), 0) if r['lt'] else 0
    for k in METRICS:
        v = m1.get(k, 0) - m0.get(k, 0); st[k] = round(v * 1000) if 'Duration' in k else int(v)
    return st

def scene(pg, name):
    if name in ('walk', 'mapscroll'): return mapscene(pg, name)
    pg.evaluate('__seed(12345)')
    pg.evaluate('() => { moves = 30; goals = [{ kind: "collect", type: 0, n: 400, left: 400 }]; lastRem = []; updateHud(); }')
    if name == 'cascade':
        pg.evaluate(FRESH, [])
        acts = ['best'] * 4
    elif name == 'combo':
        acts = [('fresh', [[3, 3, 'laser'], [3, 4, 1]]), (3, 3, 3, 4), ('fresh', [[4, 2, 'cat', 'h'], [4, 3, 2]]), (4, 2, 4, 3), ('fresh', [[3, 3, 'nip'], [3, 4, 1]]), (3, 3, 3, 4)]
    elif name == 'bowl':
        acts = [('fresh', [[4, 3, 'bowl'], [4, 4, 0]]), (4, 3, 4, 4)]
    elif name == 'bowlbowl':
        acts = [('fresh', [[4, 3, 'bowl'], [4, 4, 'bowl']]), (4, 3, 4, 4)]
    elif name == 'finale':
        acts = [('fresh', [[5, 1, 1], [5, 2, 1], [6, 3, 1], [5, 3, 4]]), ('win', 21)]
    # the board for the scene is set up before recording starts, then every action waits until all is calm
    while acts and isinstance(acts[0], tuple) and acts[0][0] == 'fresh':
        pg.evaluate(FRESH, acts.pop(0)[1])
    pg.wait_for_timeout(300)
    cdp.send('Performance.enable'); m0 = {m['name']: m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
    pg.evaluate(REC_ON)
    for a in acts:
        if a == 'best':
            pg.evaluate('() => { const m = bestMove(); window.__d = false; trySwap(m.r, m.c, m.r2, m.c2).then(() => window.__d = true); }')
        elif isinstance(a, tuple) and a[0] == 'fresh':
            pg.wait_for_function(IDLE, timeout=90000, polling=100); pg.evaluate(FRESH, a[1]); pg.wait_for_timeout(150); continue
        elif isinstance(a, tuple) and a[0] == 'win':
            pg.evaluate(f'() => {{ T_goalNext(1); moves = {a[1]}; updateHud(); window.__d = false; trySwap(6, 3, 5, 3); }}')
            pg.wait_for_function('document.getElementById("endOv").classList.contains("show")', timeout=180000); pg.wait_for_timeout(400)
            continue
        else:
            pg.evaluate(f'() => {{ window.__d = false; trySwap({a[0]}, {a[1]}, {a[2]}, {a[3]}).then(() => window.__d = true); }}')
        pg.wait_for_function('window.__d === true', timeout=120000, polling=100)
        pg.wait_for_function(IDLE, timeout=120000, polling=100)
    r = pg.evaluate(REC_OFF)
    m1 = {m['name']: m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
    st = stats(r['t'])
    st['long'] = len(r['lt']); st['longmax'] = round(max(r['lt']), 0) if r['lt'] else 0
    for k in METRICS:
        v = m1.get(k, 0) - m0.get(k, 0)
        st[k] = round(v * 1000) if 'Duration' in k else int(v)
    return st

if __name__ == '__main__':
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DPR, has_touch=True, is_mobile=True)
        pg = ctx.new_page(); veteran.veteran(pg); pg.add_init_script(SEED)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + D + '/' + GAME)
        pg.evaluate('localStorage.clear(); localStorage.setItem("wm-level", 150); localStorage.setItem("wm-purr-told", "1"); localStorage.setItem("wm-purr-keep", "1"); localStorage.setItem("wm-music", "off")')
        pg.reload(); pg.wait_for_timeout(700); pg.evaluate(WAIT_MAP)
        pg.evaluate('openLevel(1)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500)
        pg.add_script_tag(content=HN); pg.evaluate('T_waitIdle()')
        if os.environ.get('INJECT_CSS'): pg.add_style_tag(content=os.environ['INJECT_CSS'])
        if os.environ.get('INJECT_JS'): pg.evaluate(os.environ['INJECT_JS'])
        cdp = ctx.new_cdp_session(pg)
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': THROTTLE})
        for name in SCENES:
            rs = []
            for i in range(RUNS):
                rs.append(scene(pg, name)); pg.wait_for_timeout(300)
                if name == 'finale':  # back into a level for the next run
                    pg.evaluate("() => { document.getElementById('endOv').classList.remove('show'); showMap(); }"); pg.wait_for_timeout(500); pg.evaluate(WAIT_MAP)
                    pg.evaluate('openLevel(1)'); pg.wait_for_timeout(500); pg.click('#introBtn'); pg.wait_for_timeout(1500); pg.evaluate('T_waitIdle()')
            res[name] = rs
            for st in rs:
                print('%-9s fps %5.1f  p50 %5.1f  p95 %6.1f  p99 %6.1f  max %6.1f  jank%% %5.1f  >50ms %3d  long %3d (max %4d)  script %5d  style %5d (%4d)  layout %5d (%4d)  task %6d  span %.1fs' % (
                    name, st['fps'], st['p50'], st['p95'], st['p99'], st['max'], st['jank'], st['bad'], st['long'], st['longmax'], st['ScriptDuration'], st['RecalcStyleDuration'], st['RecalcStyleCount'],
                    st['LayoutDuration'], st['LayoutCount'], st['TaskDuration'], st['span']), flush=True)
        print('errors', errs[:3])
        b.close()
    json.dump(res, open(D + '/' + os.environ.get('OUT', 'perf.json'), 'w'))
