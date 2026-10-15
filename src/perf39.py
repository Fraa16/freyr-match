"""how smooth are the extras? plays playground demos with a slowed-down CPU and measures the main thread:
long tasks (over 50 ms, the moments the screen freezes) and frame gaps, for the old and new effects, with and without sound.
usage: python3 perf39.py [demos] [rate]"""
import os, sys, json, time
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
GAME = os.environ.get('GAME', 'game39p.html')
DEMOS = (sys.argv[1] if len(sys.argv) > 1 else 'Festmahl + Flitzer,Festmahl + Minze,Festmahl + Laser,Doppel-Festmahl,Festmahl').split(',')
RATE = float(sys.argv[2]) if len(sys.argv) > 2 else 4
VARIANTS = [v for v in os.environ.get('VARIANTS', 'old,new,new-mute').split(',')]
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 402, 'height': 874}, device_scale_factor=3, has_touch=True, is_mobile=True)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/' + GAME); pg.wait_for_timeout(900); fonts(pg)
    pg.evaluate("localStorage.setItem('wm-music','off'); localStorage.setItem('wm-pair40','off')")
    pg.evaluate("() => { try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1500)
    pg.evaluate("""() => { window.__lt = []; try { new PerformanceObserver(l => { for (const e of l.getEntries()) __lt.push([e.startTime, e.duration]); }).observe({ entryTypes: ['longtask'] }); } catch (e) {}
      window.__fr = []; let last = performance.now(); const loop = t => { __fr.push([t, t - last]); last = t; requestAnimationFrame(loop); }; requestAnimationFrame(loop); }""")
    cdp = pg.context.new_cdp_session(pg)
    def demo(name):
        pg.click('#p39btn'); pg.wait_for_timeout(250)
        # the same board and the same dice every time, so runs can be compared
        pg.evaluate("() => { let a = 1234567; Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }")
        pg.evaluate('window.__p39t = 0'); pg.click(f'#p39 .p39grid button:text-is("{name}")')
        pg.wait_for_function('window.__p39t > 0', timeout=30000)
        t0 = pg.evaluate('window.__p39t'); pg.wait_for_timeout(7000 if 'Doppel' in name else 4500)
        pg.evaluate('T = typeof T_waitIdle; 0') if False else None
        return pg.evaluate("""(t0) => { const lt = __lt.filter(([s]) => s >= t0 - 50), fr = __fr.filter(([t]) => t >= t0 && t <= t0 + 4000).map(x => x[1]);
          fr.sort((a, b) => a - b);
          return { lt: lt.length, ltSum: Math.round(lt.reduce((a, x) => a + x[1], 0)), ltMax: Math.round(Math.max(0, ...lt.map(x => x[1]))),
                   frames: fr.length, gaps50: fr.filter(x => x > 50).length, gap: Math.round(fr[fr.length - 1] || 0), p95: Math.round(fr[Math.floor(fr.length * .95)] || 0) }; }""", t0)
    # one warm-up round so sprites and sounds exist
    pg.click('#p39btn'); pg.wait_for_timeout(200); pg.click('#p39 .p39grid button:text-is("Doppel-Festmahl")'); pg.wait_for_timeout(9000)
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': RATE})
    res = {}
    for v in VARIANTS:
        pg.evaluate("(v) => { FX39 = v !== 'old'; soundOn = v !== 'new-mute'; }", v)
        for n in DEMOS:
            pg.evaluate('window.__lt.length = 0')
            r = demo(n); res[(v, n)] = r
            print(f'{v:9s} {n:20s} longtasks {r["lt"]:2d} sum {r["ltSum"]:5d}ms max {r["ltMax"]:4d}ms | frames {r["frames"]:3d} gaps>50ms {r["gaps50"]:2d} worst {r["gap"]:4d}ms p95 {r["p95"]:3d}ms', flush=True)
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
    print('errors', errs[:3])
    b.close()
