"""Builds the web app for GitHub Pages from game.html:
fonts served from the site (works offline), manifest + icons for the home screen, a service worker, the install hint.
usage: python3 mk_site35.py [OUTDIR]   (default: ../docs, the folder GitHub Pages serves)"""
import os, sys, json, shutil, hashlib, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else D + '../docs') + '/'
FONTDIR = D + 'fonts/'   # woff2 files from the @fontsource npm packages (latin subset)
ICONDIR = D + 'icons/'   # made by mkicon35.py
NAME, THEME, BG = 'Freyr Match', '#3B2380', '#3B2380'

s = open(D + 'game.html').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)

# fonts: the same three families, now from the site itself (latin subset covers German)
FONTS = [('Lilita One', 'lilita-one', [400]), ('Nunito', 'nunito', [700, 800, 900]), ('M PLUS Rounded 1c', 'm-plus-rounded-1c', [700, 800])]
os.makedirs(OUT + 'fonts', exist_ok=True); os.makedirs(OUT + 'icons', exist_ok=True)
face, font_files = [], []
for fam, slug, weights in FONTS:
    for w in weights:
        fn = f'{slug}-latin-{w}-normal.woff2'
        shutil.copy(FONTDIR + fn, OUT + 'fonts/' + fn); font_files.append('fonts/' + fn)
        face.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(fonts/{fn}) format('woff2')}}")
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n', '')
rep('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n', '')
rep('<link href="https://fonts.googleapis.com/css2?family=Lilita+One&family=Nunito:wght@700;800;900&family=M+PLUS+Rounded+1c:wght@700;800&display=swap" rel="stylesheet">',
    '<link rel="preload" href="fonts/lilita-one-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n<style>' + '\n'.join(face) + '</style>')
assert 'fonts.googleapis' not in s and 'fonts.gstatic' not in s

# home screen: manifest, icons, full screen with the status bar over the game
head = '\n'.join([
    f'<meta name="description" content="Match-3 mit Freyr, dem weißen Maine Coon.">',
    f'<meta name="theme-color" content="{THEME}">',
    '<meta name="mobile-web-app-capable" content="yes">',
    '<meta name="apple-mobile-web-app-capable" content="yes">',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
    f'<meta name="apple-mobile-web-app-title" content="{NAME}">',
    '<link rel="manifest" href="manifest.webmanifest">',
    '<link rel="icon" type="image/png" sizes="64x64" href="icons/favicon-64.png">',
    '<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">',
    '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">',
])
rep('<title>Freyr Match</title>', '<title>Freyr Match</title>\n' + head)
i = s.rfind('</style>', 0, s.find('</head>')); s = s[:i] + open(D + 'pwa35.css').read() + s[i:]
rep("\naddEventListener('resize', sizeFx);\n", '\n' + open(D + 'pwa35.js').read() + "\naddEventListener('resize', sizeFx);\n")
open(OUT + 'index.html', 'w').write(s)

ICONS = ['icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png', 'icons/apple-touch-icon.png', 'icons/favicon-64.png']
for ic in ICONS: shutil.copy(ICONDIR + os.path.basename(ic), OUT + ic)
man = {
    'name': NAME, 'short_name': NAME, 'description': 'Match-3 mit Freyr, dem weißen Maine Coon.', 'lang': 'de', 'dir': 'ltr',
    'id': './', 'start_url': './', 'scope': './', 'display': 'standalone', 'orientation': 'portrait',
    'background_color': BG, 'theme_color': THEME, 'categories': ['games'],
    'icons': [{'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
              {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
              {'src': 'icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]}
open(OUT + 'manifest.webmanifest', 'w').write(json.dumps(man, ensure_ascii=False, indent=2) + '\n')

core = ['./', 'manifest.webmanifest'] + ICONS + font_files
h = hashlib.sha256()
for f in ['index.html', 'manifest.webmanifest'] + ICONS + font_files: h.update(open(OUT + f, 'rb').read())
ver = h.hexdigest()[:10]
sw = open(D + 'sw35.js').read().replace('__VERSION__', ver).replace('__CORE__', json.dumps(core))
open(OUT + 'sw.js', 'w').write(sw)
open(OUT + '.nojekyll', 'w').write('')
print('site', OUT, 'version', ver, 'index', len(s))
