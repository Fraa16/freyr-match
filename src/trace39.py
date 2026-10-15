"""a timeline trace of one playground demo: how much time goes to script, style, layout, paint and raster
usage: python3 trace39.py "Demo name" [rate]"""
import os, sys, json, collections
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
NAME = sys.argv[1]; RATE = float(sys.argv[2]) if len(sys.argv) > 2 else 4
OUT = os.environ.get('TRACE', '/tmp/trace39.json')
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 402, 'height': 874}, device_scale_factor=3, has_touch=True, is_mobile=True)
    pg.goto('file://' + D + '/' + os.environ.get('GAME', 'game39p.html')); pg.wait_for_timeout(900); fonts(pg)
    pg.evaluate("localStorage.setItem('wm-music','off'); localStorage.setItem('wm-pair40','off')")
    pg.evaluate("() => { try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1500)
    pg.click('#p39btn'); pg.wait_for_timeout(200); pg.click('#p39 .p39grid button:text-is("Doppel-Festmahl")'); pg.wait_for_timeout(9000)
    if os.environ.get('JS'): pg.evaluate(os.environ['JS'])
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': RATE})
    b.start_tracing(page=pg, path=OUT, categories=['devtools.timeline', 'disabled-by-default-devtools.timeline', 'blink', 'cc', 'gpu'])
    pg.click('#p39btn'); pg.wait_for_timeout(200); pg.click(f'#p39 .p39grid button:text-is("{NAME}")'); pg.wait_for_timeout(5000)
    b.stop_tracing()
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
    b.close()
ev = json.load(open(OUT)); ev = ev['traceEvents'] if isinstance(ev, dict) else ev
tot = collections.Counter(); cnt = collections.Counter(); mx = collections.Counter()
for e in ev:
    if e.get('ph') == 'X' and 'dur' in e:
        tot[e['name']] += e['dur']; cnt[e['name']] += 1; mx[e['name']] = max(mx[e['name']], e['dur'])
for k in ['FunctionCall', 'TimerFire', 'FireAnimationFrame', 'EventDispatch', 'UpdateLayoutTree', 'Layout', 'PrePaint', 'Paint', 'PaintImage', 'RasterTask', 'CompositeLayers', 'Layerize', 'UpdateLayer', 'Commit', 'GPUTask', 'ImageDecodeTask', 'Decode Image', 'ScheduleStyleRecalculation', 'HitTest', 'IntersectionObserverController::computeIntersections', 'ParseHTML', 'MajorGC', 'MinorGC', 'V8.GC_SCAVENGER', 'ThreadControllerImpl::RunTask']:
    if tot[k]: print(f'{k:28s} {tot[k] / 1000:8.0f}ms  n={cnt[k]:5d}  max={mx[k] / 1000:6.1f}ms')
print('-- top by total')
for k, v in tot.most_common(25): print(f'{k:40s} {v / 1000:8.0f}ms n={cnt[k]}')
