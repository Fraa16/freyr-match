"""V39 preview: the playground, the new sounds and animations.
P: the preview starts with everything open, the button and the list are there
D: every demo runs: no page errors, the board is consistent afterwards (new and old)
A: the sounds render offline without errors and without clipping (peak), each one is audible (rms)
V: a video of the double Festmahl and the Kratzer for a look (vid39/)"""
import os, sys, json, glob, shutil
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
GAME = os.environ.get('GAME', 'game39p.html')
HN = open(D + '/harness.js').read()
SHOTS = D + '/shots39'; os.makedirs(SHOTS, exist_ok=True)
VID = D + '/vid39'; shutil.rmtree(VID, ignore_errors=True); os.makedirs(VID)
fails = []
def ok(m, c, info=None):
    print(('OK   ' if c else 'FAIL ') + m + ('' if c or info is None else '  ' + json.dumps(info)[:400]))
    if not c: fails.append(m)
ONLY = os.environ.get('ONLY')
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    ctx = b.new_context(viewport={'width': 402, 'height': 874}, device_scale_factor=2, has_touch=True, is_mobile=True,
                        record_video_dir=VID, record_video_size={'width': 402, 'height': 874})
    pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: print('   console:', m.text[:300]) if 'P39' in m.text else None)
    pg.goto('file://' + D + '/' + GAME); pg.wait_for_timeout(900); fonts(pg)
    pg.evaluate("localStorage.setItem('wm-music','off')")
    pg.evaluate("() => { try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1500)
    st = pg.evaluate("({ maxLevel, onMap, btn: !!document.getElementById('p39btn'), cat: isUnlocked('cat'), bowl: isUnlocked('bowl'), claw: typeof clawAt, fx: FX39 })")
    ok('P1 preview opens with everything unlocked and the button', st['maxLevel'] >= 200 and st['btn'] and st['cat'] and st['bowl'] and st['fx'], st)
    pg.screenshot(path=SHOTS + '/map.png')
    pg.click('#p39btn'); pg.wait_for_timeout(300)
    pg.screenshot(path=SHOTS + '/sheet.png')
    names = pg.evaluate("[...document.querySelectorAll('#p39 .p39grid button')].map(b => b.textContent)")
    ok('P2 the list shows all demos', len(names) >= 14, names)
    pg.click('#p39 .p39x'); pg.wait_for_timeout(200)
    pg.add_script_tag(content=HN)
    def demo(name, wait=4500, shot=None):
        pg.click('#p39btn'); pg.wait_for_timeout(250)
        pg.evaluate('''() => { if (window.__mo39) return; window.__mo39 = 1; const el = document.getElementById('p39'); let was = el.hidden;
          new MutationObserver(() => { if (el.hidden !== was) { was = el.hidden; console.log('P39 hidden=' + el.hidden + ' ' + (new Error().stack || '').split('\\n').slice(1, 4).join(' / ')); } }).observe(el, { attributes: true }); }''')
        if not pg.is_visible(f'#p39 .p39grid button:text-is("{name}")'):
            print('   not visible:', pg.evaluate("({ hidden: document.getElementById('p39').hidden, ov: [...document.querySelectorAll('.overlay.show')].map(o => o.id), top: [...document.querySelectorAll('#p39, #p39btn')].map(e => getComputedStyle(e).zIndex), card: JSON.stringify(document.querySelector('#p39 .p39card').getBoundingClientRect()) })"))
            pg.screenshot(path=SHOTS + '/notvisible.png')
        pg.click(f'#p39 .p39grid button:text-is("{name}")')
        if shot:
            for i, t in enumerate(shot):
                pg.wait_for_timeout(t); pg.screenshot(path=f'{SHOTS}/{shot_name(name)}_{i}.png')
        pg.wait_for_timeout(wait)
        pg.evaluate('T_waitIdle()')
        return pg.evaluate("({ check: T_check(), busy, level, onMap, moves })")
    shot_name = lambda n: n.lower().replace(' ', '').replace('+', '_').replace('×', 'x')
    t0 = pg.evaluate('performance.now()')
    for name in names:
        if ONLY and name not in ONLY.split(','): continue
        r = demo(name, 5000 if 'Festmahl' in name or 'entstehen' in name else 3500,
                 [250, 300, 300, 300, 300] if name in ('Doppel-Festmahl', 'Krallenkratzer') else None)
        ok(f'D new: {name}: board consistent, still in the playground', not r['check'] and not r['busy'] and r['level'] == 1 and not r['onMap'], r)
    # the old ones still work too
    pg.click('#p39btn'); pg.wait_for_timeout(200); pg.click('#p39 .p39seg button[data-v="old"]'); pg.click('#p39 .p39x')
    for name in ['Doppel-Festmahl', 'Krallenkratzer', 'Festmahl + Laser']:
        r = demo(name, 5000)
        ok(f'D old: {name}: board consistent', not r['check'] and not r['busy'], r)
    pg.click('#p39btn'); pg.wait_for_timeout(200); pg.click('#p39 .p39seg button[data-v="new"]'); pg.click('#p39 .p39x')
    ok('no page errors while playing', not errs, errs[:4])
    # A: every sound rendered offline: peak and loudness
    res = pg.evaluate("""async () => {
      const out = {}, keep = { a: actx, m: master };
      const tests = {
        cat: () => SYN.cat(0, 'h'), catBig: () => SYN.cat(0, 'x', true), nip: () => SYN.nip(0, 1), nip2: () => SYN.nip(0, 2),
        laser: () => [0, .15, .3].forEach((t, i) => SYN.laserHit(t, i, (i - 1) * .5)), bowl: () => { SYN.bowl(0); SYN.zaps([200, 260, 320, 380, 440, 500, 560, 620]); },
        spawnCat: () => SYN.spawn('cat'), spawnNip: () => SYN.spawn('nip'), spawnLaser: () => SYN.spawn('laser'), spawnBowl: () => SYN.spawn('bowl'),
        conv: () => { SYN.convStart(0, 12, .045); for (let i = 0; i < 12; i++) SYN.conv(.08 + i * .045, i, 'cat'); },
        boom: () => SYN.boom(0, 1.3), scratch: () => SYN.scratch(.15, .37),
        feast: () => { SYN.feastCharge(0, .62); SYN.feastBang(.62); }, whirl: () => SYN.whirl(0, 1.4),
        combo: () => { for (let i = 0; i < 5; i++) SYN.cat(.1 * i, i % 2 ? 'v' : 'h'); for (let i = 0; i < 4; i++) SYN.nip(.05 + .1 * i, 1); SYN.boom(.05, 1.3); }
      };
      for (const [name, fn] of Object.entries(tests)) {
        const oc = new OfflineAudioContext(2, 48000 * 3.5, 48000);
        actx = oc; master = oc.createGain(); master.gain.value = .9; master.connect(oc.destination);
        fn();
        const buf = await oc.startRendering();
        let peak = 0, sum = 0, n = 0;
        for (let ch = 0; ch < 2; ch++) { const d = buf.getChannelData(ch); for (let i = 0; i < d.length; i++) { const v = Math.abs(d[i]); if (v > peak) peak = v; sum += d[i] * d[i]; n++; } }
        out[name] = { peak: +peak.toFixed(3), rms: +Math.sqrt(sum / n).toFixed(4) };
      }
      actx = keep.a; master = keep.m;
      return out;
    }""")
    for k, v in res.items(): print(f'   sound {k:10s} peak {v["peak"]:.3f} rms {v["rms"]:.4f}')
    ok('A1 no sound clips (peak < 1)', all(v['peak'] < 1 for v in res.values()), res)
    ok('A2 every sound is audible (peak > 0.05)', all(v['peak'] > .05 for v in res.values()), res)
    nb = pg.evaluate('SXB.size'); print('   pre-rendered sounds:', nb, '/', pg.evaluate('Object.keys(SXDEF).length'))
    ok('A3 the sounds were rendered into buffers in the background', nb >= 20, nb)
    ok('no page errors at the end', not errs, errs[:4])
    pg.close(); ctx.close(); b.close()
print('FAILS', len(fails))
