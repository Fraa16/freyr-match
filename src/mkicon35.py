"""app icons for the home screen: Freyr's head on a pink to violet tile"""
import os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); OUT = D + '/icons'; os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 600, 'height': 600})
    pg.goto('file://' + D + '/game.html'); pg.wait_for_timeout(300)
    cat = pg.evaluate("(() => { const d = document.createElement('div'); d.innerHTML = CAT_SVG; d.querySelectorAll('.m-o,.m-y').forEach(e => e.remove()); return d.innerHTML; })()")
    def tile(size, head, dy, name, round_=False):
        html = f'''<html><body style="margin:0;background:transparent">
<div id="t" style="width:{size}px;height:{size}px;position:relative;overflow:hidden;{'border-radius:22%;' if round_ else ''}
 background:radial-gradient(circle at 50% 46%,rgba(255,255,255,.28) 0 {size*.30}px,rgba(255,255,255,0) {size*.46}px),
 radial-gradient(circle,rgba(255,255,255,.14) 0 {size*.012}px,transparent {size*.013}px) 0 0/{size*.09}px {size*.09}px,
 linear-gradient(150deg,#FF8CC6 0%,#E65AB4 38%,#8A49DB 100%)">
 <div style="position:absolute;left:{(size-head)/2}px;top:{(size-head)/2+dy}px;width:{head}px;height:{head}px;filter:drop-shadow(0 {size*.018}px 0 rgba(70,20,90,.28))">{cat.replace('<svg ', '<svg width="100%" height="100%" ', 1)}</div>
</div></body></html>'''
        pg.set_viewport_size({'width': size, 'height': size}); pg.set_content(html); pg.wait_for_timeout(100)
        pg.locator('#t').screenshot(path=OUT + '/' + name, omit_background=True)
    tile(1024, 760, 30, 'icon-1024.png')
    tile(512, 380, 15, 'icon-512.png')
    tile(192, 142, 6, 'icon-192.png')
    tile(180, 134, 5, 'apple-touch-icon.png')
    tile(512, 300, 12, 'icon-maskable-512.png')
    tile(64, 50, 2, 'favicon-64.png')
    tile(360, 268, 10, 'preview-round.png', round_=True)
    b.close()
print('ok')
