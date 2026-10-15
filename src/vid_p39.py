"""records the playground demos on video and cuts contact sheets of frames (for looking at the animations)
usage: python3 vid_p39.py "Demo A,Demo B" [step_ms] [count]"""
import os, sys, time, json, glob, shutil, subprocess
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from fontfix import fonts
OUT = os.environ.get('OUT', D + '/vid39'); shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
names = sys.argv[1].split(','); STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 100; CNT = int(sys.argv[3]) if len(sys.argv) > 3 else 24
marks = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 402, 'height': 874}, device_scale_factor=1, has_touch=True, is_mobile=True, record_video_dir=OUT, record_video_size={'width': 402, 'height': 874})
    t0 = time.time(); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + D + '/' + os.environ.get('GAME', 'game39p.html')); off = (time.time() - t0) - pg.evaluate('performance.now()') / 1000; pg.wait_for_timeout(900); fonts(pg)
    pg.evaluate("() => { try { if (introRun) mapSkip = true; } catch (e) {} }"); pg.wait_for_timeout(1500)
    # into the playground once first
    pg.click('#p39btn'); pg.wait_for_timeout(250); pg.click('#p39 .p39grid button:text-is("Flitzer")'); pg.wait_for_timeout(4000)
    for n in names:
        pg.click('#p39btn'); pg.wait_for_timeout(250)
        pg.evaluate('window.__p39t = 0'); pg.click(f'#p39 .p39grid button:text-is("{n}")')
        pg.wait_for_function('window.__p39t > 0', timeout=20000); marks.append((n, off + pg.evaluate('window.__p39t') / 1000))
        pg.wait_for_timeout(int(os.environ.get('HOLD', 6000)))
    vid = pg.video.path(); pg.close(); ctx.close(); b.close()
print('errors', errs[:3])
for n, t in marks:
    tag = n.lower().replace(' ', '').replace('+', '_').replace('×', 'x').replace('ü', 'u')
    fr = f'{OUT}/{tag}'; os.makedirs(fr, exist_ok=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t + float(os.environ.get("LEAD", 0)):.2f}', '-i', vid, '-vf', f'fps={1000 / STEP}', '-frames:v', str(CNT), f'{fr}/f%03d.png'], check=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{fr}/f%03d.png', '-vf', 'crop=402:560:0:120,scale=201:280,tile=8x' + str((CNT + 7) // 8), '-frames:v', '1', f'{OUT}/{tag}.png'], check=True)
    print(n, f'{OUT}/{tag}.png')
