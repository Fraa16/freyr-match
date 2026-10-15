"""CPU profile of one playground demo (slowed CPU): which functions take the time
usage: python3 prof39.py "Demo name" [rate]"""
import os, sys, json, collections
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
NAME = sys.argv[1]; RATE = float(sys.argv[2]) if len(sys.argv) > 2 else 4
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 402, 'height': 874}, device_scale_factor=3, has_touch=True, is_mobile=True)
    pg.goto('file://' + D + '/' + os.environ.get('GAME', 'game39p.html')); pg.wait_for_timeout(900); fonts(pg)
    pg.evaluate("localStorage.setItem('wm-music','off'); localStorage.setItem('wm-pair40','off')")
    pg.evaluate("() => { try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1500)
    pg.click('#p39btn'); pg.wait_for_timeout(200); pg.click('#p39 .p39grid button:text-is("Doppel-Festmahl")'); pg.wait_for_timeout(9000)
    if os.environ.get('MUTE'): pg.evaluate('soundOn = false')
    if os.environ.get('OLD'): pg.evaluate('FX39 = false')
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': RATE})
    cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 200}); cdp.send('Profiler.start')
    pg.click('#p39btn'); pg.wait_for_timeout(200); pg.click(f'#p39 .p39grid button:text-is("{NAME}")'); pg.wait_for_timeout(6000)
    prof = cdp.send('Profiler.stop')['profile']
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
    b.close()
nodes = {n['id']: n for n in prof['nodes']}
dt = collections.Counter()
samples, deltas = prof['samples'], prof['timeDeltas']
for s, d in zip(samples, deltas): dt[s] += d
selft = collections.Counter()
for nid, t in dt.items():
    cf = nodes[nid]['callFrame']; key = f"{cf['functionName'] or '(anon)'}:{cf['lineNumber'] + 1}" if cf['url'] else cf['functionName'] or cf['url'] or '?'
    selft[key] += t
# inclusive time by function: walk parents
parent = {}
for n in prof['nodes']:
    for c in n.get('children', []): parent[c] = n['id']
incl = collections.Counter()
for nid, t in dt.items():
    seen = set(); x = nid
    while x is not None:
        cf = nodes[x]['callFrame']; key = f"{cf['functionName'] or '(anon)'}:{cf['lineNumber'] + 1}" if cf['url'] else cf['functionName'] or '?'
        if key not in seen: incl[key] += t; seen.add(key)
        x = parent.get(x)
tot = sum(dt.values())
print('total ms', round(tot / 1000))
print('-- self'); [print(f'{v / 1000:8.0f}ms  {k}') for k, v in selft.most_common(22)]
print('-- inclusive'); [print(f'{v / 1000:8.0f}ms  {k}') for k, v in incl.most_common(30)]
