"""tests run without network: the game's fonts come from the local fonts/ folder (same files the web app ships)"""
import os
_F = 'file://' + os.path.dirname(os.path.abspath(__file__)) + '/fonts/'
_FACES = [('Lilita One', 400, 'lilita-one-latin-400-normal.woff2'), ('Nunito', 700, 'nunito-latin-700-normal.woff2'),
          ('Nunito', 800, 'nunito-latin-800-normal.woff2'), ('Nunito', 900, 'nunito-latin-900-normal.woff2'),
          ('M PLUS Rounded 1c', 700, 'm-plus-rounded-1c-latin-700-normal.woff2'), ('M PLUS Rounded 1c', 800, 'm-plus-rounded-1c-latin-800-normal.woff2')]
FONTCSS = '\n'.join(f"@font-face{{font-family:'{f}';font-weight:{w};src:url({_F}{n}) format('woff2')}}" for f, w, n in _FACES)
def fonts(pg):
    pg.add_style_tag(content=FONTCSS)
    pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(400)
