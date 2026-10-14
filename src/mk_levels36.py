"""Levels 161-260 (20 new worlds) for Freyr Match, written as compact recipes and turned into level defs.
New in these worlds: belts (Förderband), dark cells ('d', Nacht-Felder) and the rainbow fish ('r' / wildRate).
The moves here are first guesses; tune36.py sets them with the bot and writes fix36.json.
usage: python3 mk_levels36.py   -> levels36.json, worlds36.json"""
import json, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'

WORLDS = [('Apfelhain', 'im Apfelhain'), ('Wolkenbäckerei', 'in der Wolkenbäckerei'), ('Laternenstadt', 'in der Laternenstadt'), ('Sardinenhafen', 'im Sardinenhafen'),
          ('Kräutergarten', 'im Kräutergarten'), ('Kissenwolken', 'in den Kissenwolken'), ('Sternwarte', 'in der Sternwarte'), ('Wellenstrand', 'am Wellenstrand'),
          ('Sonnenblumenfeld', 'im Sonnenblumenfeld'), ('Himmelsbrücke', 'auf der Himmelsbrücke'), ('Mondsee', 'am Mondsee'), ('Schatzinsel', 'auf der Schatzinsel'),
          ('Pilzwald', 'im Pilzwald'), ('Zeppelinhafen', 'im Zeppelinhafen'), ('Eulenwald', 'im Eulenwald'), ('Korallengarten', 'im Korallengarten'),
          ('Erdbeerfest', 'beim Erdbeerfest'), ('Himmelsschloss', 'im Himmelsschloss'), ('Sternenzelt', 'im Sternenzelt'), ('Katzenparadies', 'im Katzenparadies')]

# ---------------- board shapes ----------------
M = {
    'full':   ['........'] * 8,
    'round':  [' ...... '] + ['........'] * 6 + [' ...... '],
    'diamond': ['  ....  ', ' ...... '] + ['........'] * 4 + [' ...... ', '  ....  '],
    'hour':   ['........', ' ...... ', '  ....  ', '  ....  ', '  ....  ', '  ....  ', ' ...... ', '........'],
    'donut':  ['........'] * 3 + ['...  ...'] * 2 + ['........'] * 3,
    'plus':   ['  ....  '] * 2 + ['........'] * 4 + ['  ....  '] * 2,
    'heart':  [' ..  .. ', '........', '........', '........', '........', ' ...... ', '  ....  ', '   ..   '],
    'arch':   ['........'] * 4 + ['...  ...'] * 4,
    'cat':    ['.      .', '..    ..', '........', '........', '........', '........', ' ...... ', '  ....  '],
    'wide':   [' ...... '] * 8,
    'stairs': ['....    ', '.....   ', '......  ', '....... ', '........', '........', '........', '........'],
    'h':      ['..    ..', '..    ..', '........', '........', '........', '........', '..    ..', '..    ..'],
    'bowl':   ['.      .', '..    ..', '...  ...', '........', '........', '........', ' ...... ', '  ....  '],
    'twin':   ['...  ...'] * 3 + ['........'] * 2 + ['...  ...'] * 3,
    'fish':   ['  ...   ', ' .....  ', '....... ', '........', '........', '....... ', ' .....  ', '  ...   '],
    'cup':    ['........', '........', '........', '........', '........', ' ...... ', '  ....  ', '  ....  '],
}
def rect(r0, c0, r1, c1): return [(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)]
def mir(cells): return sorted(set(cells + [(r, 7 - c) for r, c in cells]))
def row(r, c0=0, c1=7): return rect(r, c0, r, c1)
def build(mask, feats):
    g = [list(x) for x in M[mask]]
    for ch, cells in feats:
        for r, c in cells:
            if g[r][c] != ' ': g[r][c] = ch
    return [''.join(x) for x in g]

# ---------------- the 100 levels ----------------
# keys: n name, m mask, f features [(char, cells)], belts [[row, dir]], wr wildRate, plus the usual level keys
L = {}
def lv(no, **k): L[no] = k

# W33 Apfelhain: the belt
lv(161, n='Erste Fahrt', m='full', belts=[[4, 1]], collect=[[0, 24]], moves=22, intro='belt', colors=5)
lv(162, n='Apfelernte', m='round', belts=[[3, 1], [5, -1]], collect=[[1, 30]], moves=22)
lv(163, n='Kistenband', m='full', f=[('b', mir(rect(0, 0, 1, 1)) + mir([(2, 0)]))], belts=[[5, 1]], collect=[[2, 26]], moves=22)
lv(164, n='Rollende Äpfel', m='diamond', f=[('m', rect(6, 2, 6, 5)), ('m', rect(7, 2, 7, 5))], belts=[[3, -1]], collect=[[3, 28]], moves=22)
lv(165, n='Großes Laufband', m='full', f=[('B', mir([(0, 0), (0, 1)])), ('M', rect(7, 0, 7, 7))], belts=[[2, 1], [5, -1]], collect=[[4, 34]], moves=24, hard=1)
# W34 Wolkenbäckerei
lv(166, n='Brötchenband', m='cup', f=[('k', rect(6, 2, 7, 5))], belts=[[3, 1]], cover=0, collect=[[5, 26]], moves=22)
lv(167, n='Hefezopf', m='full', f=[('b', mir(rect(0, 0, 0, 2)))], belts=[[3, 1], [5, -1]], collect=[[0, 50], [2, 40]], moves=38, long=1)
lv(168, n='Glöckchen-Express', m='round', f=[('g', [(0, 2), (0, 5)])], belts=[[4, 1]], bells=4, moves=24, intro='mix_beltbells')
lv(169, n='Puderzucker', m='hour', f=[('n', [(3, 2), (3, 5)])], belts=[[0, 1], [7, -1]], collect=[[1, 30]], moves=22)
lv(170, n='Backofenhitze', m='full', f=[('C', mir([(3, 0)])), ('w', rect(6, 1, 6, 6))], belts=[[4, 1], [5, -1]], collect=[[3, 36]], moves=25, hard=1)
# W35 Laternenstadt
lv(171, n='Laternenweg', m='twin', f=[('w', mir([(0, 1), (2, 1)]))], belts=[[3, 1], [4, -1]], collect=[[4, 32]], moves=22)
lv(172, n='Nachtschicht', m='full', f=[('p', mir([(1, 1)])), ('k', rect(6, 0, 7, 7))], belts=[[4, -1]], moves=24)
lv(173, n='Lichterkette', m='round', f=[('a', mir([(2, 2)]))], belts=[[2, 1], [5, 1]], clock=14, collect=[[5, 30]], moves=23)
lv(174, n='Doppelband', m='full', belts=[[3, 1], [4, -1]], make=[['cat', 2], ['laser', 2]], moves=20)
lv(175, n='Stadtfest', m='plus', f=[('u', mir([(0, 2)])), ('b', mir([(2, 0), (5, 0)]))], belts=[[3, 1], [4, -1]], collect=[[0, 34]], moves=24, hard=1)
# W36 Sardinenhafen
lv(176, n='Fischkutter', m='fish', f=[('m', rect(3, 2, 4, 5))], belts=[[3, 1], [4, 1]], collect=[[0, 32]], moves=22)
lv(177, n='Ladekran', m='full', f=[('B', mir([(0, 0), (1, 0)])), ('k', rect(7, 1, 7, 6))], belts=[[3, -1], [5, 1]], cover=0, collect=[[2, 54]], moves=40, long=1)
lv(178, n='Netzflicker', m='full', f=[('w', mir([(1, 1), (1, 3), (6, 1), (6, 3)]))], belts=[[3, 1], [4, -1]], moves=22)
lv(179, n='Hafenkante', m='arch', f=[('n', mir([(6, 0), (7, 1)]))], belts=[[2, -1]], collect=[[3, 30]], moves=22)
lv(180, n='Sturmflut', m='full', f=[('V', rect(1, 3, 2, 4)), ('n', mir([(6, 0)])), ('M', rect(7, 2, 7, 5))], belts=[[4, 1], [5, -1]], boss=55, moves=28, hard=2)

# W37 Kräutergarten: the night cells
lv(181, n='Gute Nacht', m='full', f=[('d', rect(0, 0, 1, 7))], collect=[[1, 22]], moves=22, intro='dark', colors=5)
lv(182, n='Minzbeet', m='round', f=[('d', mir(rect(0, 1, 2, 2)))], collect=[[4, 26]], moves=22)
lv(183, n='Schattenbeet', m='full', f=[('d', rect(0, 2, 3, 5)), ('b', mir([(4, 0), (5, 0)]))], moves=22)
lv(184, n='Mondkraut', m='diamond', f=[('d', rect(2, 0, 3, 7)), ('m', rect(6, 2, 6, 5))], moves=22)
lv(185, n='Nachtfalter', m='full', f=[('d', mir(rect(0, 0, 3, 1)) + rect(0, 2, 0, 5)), ('w', rect(5, 2, 5, 5))], collect=[[2, 28]], moves=24, hard=1)
# W38 Kissenwolken
lv(186, n='Kissenschlacht', m='cup', f=[('d', rect(0, 0, 1, 7)), ('k', rect(6, 2, 7, 5))], cover=0, moves=24)
lv(187, n='Federbett', m='full', f=[('d', rect(0, 0, 2, 7))], collect=[[5, 44], [3, 40]], moves=38, long=1)
lv(188, n='Daunendecke', m='round', f=[('d', mir(rect(2, 0, 5, 1))), ('k', rect(3, 3, 4, 4))], cover=0, moves=23)
lv(189, n='Schlummerland', m='hour', f=[('d', rect(2, 2, 5, 5)), ('g', [(0, 3), (0, 4)])], bells=3, moves=24)
lv(190, n='Albtraum', m='full', f=[('d', rect(0, 0, 3, 7)), ('n', mir([(5, 1)])), ('u', mir([(7, 0)]))], moves=26, hard=1)
# W39 Sternwarte
lv(191, n='Fernrohr', m='plus', f=[('d', rect(0, 2, 2, 5)), ('a', mir([(4, 1)]))], clock=14, collect=[[0, 26]], moves=22)
lv(192, n='Sternbild', m='full', f=[('d', [(0, 1), (1, 3), (0, 5), (2, 6), (3, 4), (2, 2), (3, 0), (1, 7)])], collect=[[3, 30]], moves=22)
lv(193, n='Mondfinsternis', m='donut', f=[('d', rect(2, 2, 5, 5)), ('p', mir([(0, 0)]))], moves=22)
lv(194, n='Komet', m='diamond', f=[('d', rect(0, 2, 2, 5)), ('C', [(7, 3), (7, 4)])], collect=[[1, 30]], moves=24)
lv(195, n='Schwarzes Loch', m='full', f=[('d', rect(1, 1, 6, 6)), ('V', rect(3, 3, 4, 4))], boss=40, moves=28, hard=1)
# W40 Wellenstrand
lv(196, n='Nachtband', m='full', f=[('d', rect(0, 0, 2, 7))], belts=[[4, 1]], collect=[[0, 26]], moves=23, intro='mix_beltdark')
lv(197, n='Ebbe', m='round', f=[('d', rect(0, 1, 1, 6)), ('M', rect(6, 1, 7, 6))], belts=[[3, -1]], moves=38, long=1)
lv(198, n='Flut', m='full', f=[('d', mir(rect(5, 0, 7, 1))), ('n', [(0, 3), (0, 4)])], belts=[[2, 1]], moves=24)
lv(199, n='Muschelsuche', m='fish', f=[('d', rect(3, 0, 4, 7)), ('p', [(1, 2), (6, 2)])], belts=[[2, 1], [5, -1]], moves=24)
lv(200, n='Leuchtfeuer', m='full', f=[('d', rect(0, 0, 3, 7)), ('V', rect(6, 3, 7, 4))], belts=[[4, 1], [5, -1]], boss=45, turbo=1, moves=28, hard=2)

# W41 Sonnenblumenfeld: the rainbow fish
lv(201, n='Regenbogen', m='full', f=[('r', [(3, 3), (4, 5)])], wr=0.04, collect=[[2, 26]], moves=22, intro='wild', colors=5)
lv(202, n='Sonnenschein', m='round', f=[('r', mir([(2, 2)]))], wr=0.035, collect=[[0, 30], [5, 26]], moves=24)
lv(203, n='Blütenstaub', m='heart', f=[('r', [(4, 3)]), ('m', rect(1, 1, 2, 6))], wr=0.03, moves=22)
lv(204, n='Bienenflug', m='full', f=[('w', mir(rect(2, 0, 2, 2))), ('r', [(5, 2), (5, 5)])], wr=0.03, collect=[[4, 30]], moves=22)
lv(205, n='Erntefest', m='full', f=[('B', mir(rect(0, 0, 1, 1))), ('r', [(4, 2), (4, 5)])], wr=0.03, make=[['nip', 2]], collect=[[1, 30]], moves=24, hard=1)
# W42 Himmelsbrücke
lv(206, n='Brückenzoll', m='h', f=[('r', [(3, 3)]), ('g', mir([(0, 0)]))], wr=0.03, bells=3, moves=22)
lv(207, n='Wolkenkratzer', m='stairs', f=[('r', [(5, 4)]), ('b', [(0, 0), (1, 0), (2, 0)])], wr=0.03, collect=[[3, 50], [0, 44]], moves=40, long=1)
lv(208, n='Seiltanz', m='full', f=[('n', [(3, 3), (3, 4), (4, 3), (4, 4)]), ('r', mir([(6, 1)]))], wr=0.03, moves=23)
lv(209, n='Windböe', m='wide', f=[('a', [(2, 2), (2, 5), (5, 3)]), ('r', [(4, 4)])], wr=0.04, clock=14, clockRate=0.015, collect=[[5, 30]], moves=22)
lv(210, n='Gewitter', m='full', f=[('u', mir([(1, 1), (5, 2)])), ('k', rect(7, 0, 7, 7)), ('r', [(3, 3)])], wr=0.03, cover=0, moves=26, hard=1)
# W43 Mondsee
lv(211, n='Spiegelung', m='round', f=[('d', rect(4, 0, 7, 7)), ('r', [(1, 2), (1, 5)])], wr=0.035, moves=23, intro='mix_darkfish')
lv(212, n='Mondfische', m='fish', f=[('d', rect(0, 0, 2, 7)), ('r', [(4, 3)])], wr=0.04, collect=[[0, 32]], moves=23)
lv(213, n='Nebelbank', m='full', f=[('d', mir(rect(0, 0, 7, 1))), ('r', [(3, 3), (4, 4)])], wr=0.03, collect=[[2, 30]], moves=24)
lv(214, n='Glühfische', m='donut', f=[('d', rect(0, 2, 2, 5)), ('p', mir([(5, 0)])), ('r', [(6, 3)])], wr=0.03, moves=23)
lv(215, n='Seeungeheuer', m='full', f=[('d', rect(0, 0, 2, 7)), ('V', rect(4, 3, 5, 4)), ('r', mir([(7, 1)]))], wr=0.03, boss=50, moves=28, hard=1)
# W44 Schatzinsel
lv(216, n='Schatzkarte', m='full', f=[('w', mir([(0, 0), (1, 1), (2, 2)])), ('r', [(5, 3)])], belts=[[4, 1]], wr=0.03, goldrush=8, moves=23)
lv(217, n='Flaschenpost', m='round', f=[('d', rect(0, 1, 1, 6)), ('m', rect(6, 1, 7, 6))], belts=[[3, -1]], wr=0.03, collect=[[1, 40]], moves=40, long=1)
lv(218, n='Kokosnuss', m='cup', f=[('C', [(0, 0), (0, 7)]), ('g', [(0, 3), (0, 4)])], belts=[[4, 1]], bells=3, moves=24)
lv(219, n='Piratenband', m='full', f=[('p', mir([(0, 1)])), ('u', mir([(6, 0)]))], belts=[[3, 1], [4, -1]], wr=0.03, moves=24)
lv(220, n='Goldkiste', m='full', f=[('d', rect(0, 0, 1, 7)), ('C', mir([(3, 0), (4, 0)])), ('V', rect(6, 3, 7, 4))], belts=[[5, 1]], wr=0.03, boss=55, turbo=1, moves=29, hard=2)

# W45-W52: everything together
lv(221, n='Fliegenpilz', m='round', f=[('d', [(1, 2), (1, 5), (2, 3), (2, 4)]), ('b', mir([(5, 0), (6, 1)]))], belts=[[4, 1]], collect=[[5, 30]], moves=23)
lv(222, n='Moosweg', m='full', f=[('k', rect(0, 0, 7, 0) + rect(0, 7, 7, 7)), ('r', [(3, 3)])], wr=0.03, cover=0, moves=24)
lv(223, n='Pilzkreis', m='donut', f=[('u', [(2, 2), (2, 5), (5, 2), (5, 5)]), ('d', rect(0, 0, 0, 7))], collect=[[2, 30]], moves=24)
lv(224, n='Wichtelpfad', m='full', f=[('w', rect(6, 0, 6, 7)), ('d', rect(0, 0, 1, 7))], belts=[[3, 1]], moves=24)
lv(225, n='Waldgeist', m='full', f=[('d', rect(0, 0, 2, 7)), ('n', mir([(4, 0), (5, 1)])), ('r', [(3, 2), (3, 5)])], belts=[[6, -1]], wr=0.03, collect=[[0, 30]], moves=26, hard=1)
lv(226, n='Startbahn', m='wide', f=[('g', [(0, 2), (0, 5)]), ('d', rect(6, 1, 7, 6))], belts=[[3, 1]], bells=3, moves=24)
lv(227, n='Luftschiff', m='fish', f=[('k', rect(3, 0, 4, 7)), ('r', [(1, 2), (6, 2)])], belts=[[2, 1], [5, -1]], wr=0.03, cover=0, collect=[[3, 44]], moves=42, long=1)
lv(228, n='Ballast', m='full', f=[('C', mir([(0, 0), (0, 1), (1, 0)])), ('d', rect(2, 2, 3, 5))], wr=0.03, moves=25)
lv(229, n='Wolkenpost', m='round', f=[('p', mir([(2, 1), (5, 1)])), ('a', [(3, 3), (4, 4)])], belts=[[4, -1]], clock=14, moves=24)
lv(230, n='Sturmfahrt', m='full', f=[('d', rect(0, 0, 1, 7)), ('V', rect(3, 3, 4, 4)), ('u', mir([(6, 1)]))], belts=[[6, 1]], wr=0.03, boss=55, turbo=1, moves=29, hard=1)
lv(231, n='Eulenruf', m='cat', f=[('d', rect(0, 0, 3, 7)), ('r', [(5, 3)])], wr=0.03, collect=[[4, 30]], moves=24)
lv(232, n='Baumhaus', m='arch', f=[('w', rect(3, 0, 3, 7)), ('d', rect(0, 0, 1, 7))], wr=0.03, moves=24)
lv(233, n='Nachtwanderung', m='full', f=[('d', [(r, (r * 3) % 8) for r in range(8)] + [(r, (r * 3 + 4) % 8) for r in range(8)])], belts=[[3, 1], [4, -1]], moves=24)
lv(234, n='Uhu', m='plus', f=[('d', rect(2, 0, 5, 1) + rect(2, 6, 5, 7)), ('m', rect(3, 3, 4, 4))], wr=0.03, collect=[[1, 30]], moves=24)
lv(235, n='Mitternacht', m='full', f=[('d', rect(0, 0, 3, 7)), ('n', mir([(5, 2)])), ('a', mir([(6, 1)]))], belts=[[5, 1]], wr=0.03, clock=15, moves=27, hard=1)
lv(236, n='Seepferdchen', m='fish', f=[('M', rect(3, 1, 4, 6)), ('r', [(1, 2)])], belts=[[2, -1]], wr=0.03, moves=24)
lv(237, n='Seestern', m='full', f=[('d', rect(0, 0, 1, 7)), ('p', mir([(4, 0)])), ('k', rect(7, 0, 7, 7))], belts=[[3, 1], [5, -1]], wr=0.03, cover=0, collect=[[0, 44]], moves=42, long=1)
lv(238, n='Perlentaucher', m='round', f=[('C', [(3, 3), (3, 4), (4, 3), (4, 4)]), ('d', rect(0, 1, 1, 6))], wr=0.03, moves=25)
lv(239, n='Muränenhöhle', m='twin', f=[('u', mir([(0, 1), (6, 1)])), ('d', rect(3, 0, 4, 7))], belts=[[4, 1]], moves=25)
lv(240, n='Tiefsee', m='full', f=[('d', rect(0, 0, 3, 7)), ('V', rect(5, 3, 6, 4)), ('n', mir([(7, 0)])), ('r', mir([(4, 1)]))], belts=[[4, 1]], wr=0.03, boss=60, turbo=1, moves=30, hard=2)
lv(241, n='Festzelt', m='cup', f=[('g', [(0, 1), (0, 6)]), ('r', [(3, 3)])], belts=[[2, 1]], wr=0.035, bells=4, moves=25)
lv(242, n='Erdbeerbowle', m='full', f=[('M', rect(5, 2, 7, 5)), ('d', mir(rect(0, 0, 1, 1)))], belts=[[3, -1]], wr=0.03, moves=25)
lv(243, n='Tanzfläche', m='full', f=[('k', rect(3, 2, 4, 5))], belts=[[2, 1], [5, -1]], wr=0.035, cover=0, make=[['cat', 3]], moves=24)
lv(244, n='Kuchenbuffet', m='round', f=[('B', mir([(1, 1), (1, 2)])), ('p', [(4, 3), (4, 4)])], wr=0.03, collect=[[5, 34]], moves=25)
lv(245, n='Feuerwerk', m='full', f=[('d', rect(0, 0, 2, 7)), ('u', mir([(4, 0), (6, 2)])), ('w', rect(7, 2, 7, 5))], belts=[[5, 1]], wr=0.03, goldrush=6, moves=27, hard=1)
lv(246, n='Schlosstor', m='arch', f=[('C', mir([(0, 0)])), ('d', rect(0, 2, 1, 5))], wr=0.03, collect=[[2, 32]], moves=25)
lv(247, n='Thronsaal', m='full', f=[('k', rect(0, 0, 0, 7) + rect(7, 0, 7, 7)), ('d', rect(3, 0, 4, 7))], belts=[[2, 1], [5, -1]], wr=0.03, cover=0, collect=[[4, 40]], moves=44, long=1)
lv(248, n='Turmzimmer', m='hour', f=[('d', rect(0, 0, 1, 7)), ('g', [(2, 3)])], wr=0.03, bells=3, moves=25)
lv(249, n='Wendeltreppe', m='stairs', f=[('w', [(3, 3), (4, 4), (5, 5), (6, 6)]), ('d', rect(0, 0, 1, 3))], belts=[[5, 1]], wr=0.03, moves=25)
lv(250, n='Königsball', m='full', f=[('V', rect(3, 3, 4, 4)), ('d', rect(0, 0, 1, 7)), ('C', mir([(6, 0), (7, 0)]))], belts=[[6, -1]], wr=0.03, boss=60, moves=30, hard=1)
lv(251, n='Zeltlager', m='cat', f=[('d', rect(0, 0, 2, 7)), ('n', [(5, 3), (5, 4)])], wr=0.03, moves=25)
lv(252, n='Lagerfeuer', m='full', f=[('a', mir([(3, 2), (5, 1)])), ('d', rect(0, 0, 1, 7))], belts=[[4, 1]], clock=15, clockRate=0.015, wr=0.03, collect=[[3, 32]], moves=25)
lv(253, n='Sternschnuppen-Nacht', m='round', f=[('d', [(r, c) for r in range(8) for c in range(8) if (r + c) % 3 == 0])], wr=0.04, goldrush=8, moves=25)
lv(254, n='Milchstraße', m='full', f=[('M', rect(3, 0, 4, 7)), ('d', rect(0, 0, 1, 7))], belts=[[6, 1]], wr=0.03, moves=26)
lv(255, n='Nordstern', m='full', f=[('d', rect(0, 0, 3, 7)), ('u', mir([(5, 0)])), ('p', mir([(6, 2)])), ('k', rect(7, 3, 7, 4))], belts=[[5, -1]], wr=0.03, cover=0, moves=28, hard=1)
lv(256, n='Ankunft', m='heart', f=[('d', rect(0, 0, 1, 7)), ('m', rect(5, 2, 6, 5))], belts=[[3, 1]], wr=0.035, moves=25)
lv(257, n='Sardinenbuffet', m='full', f=[('p', mir([(0, 0), (0, 2)])), ('d', rect(3, 0, 3, 7))], belts=[[5, 1], [6, -1]], wr=0.03, collect=[[0, 56], [5, 40]], moves=44, long=1)
lv(258, n='Hängematte', m='bowl', f=[('k', rect(6, 1, 7, 6)), ('d', rect(0, 0, 1, 7)), ('r', [(4, 3)])], wr=0.03, cover=0, moves=26)
lv(259, n='Sonnenbad', m='full', f=[('M', rect(6, 0, 7, 7)), ('u', mir([(3, 0)]))], belts=[[4, 1]], wr=0.035, collect=[[2, 34]], moves=26)
lv(260, n='Das zweite Finale', m='full', f=[('d', rect(0, 0, 1, 7)), ('V', rect(3, 3, 4, 4)), ('C', mir([(3, 0)])), ('u', mir([(6, 1)])), ('M', rect(7, 2, 7, 5)), ('r', mir([(5, 2)]))],
   belts=[[5, 1]], wr=0.03, boss=70, turbo=1, bells=2, moves=34, hard=2, intro='mix_newfinale')

assert sorted(L) == list(range(161, 261)), [x for x in range(161, 261) if x not in L]
out = []
for no in range(161, 261):
    k = dict(L[no])
    d = {'name': k.pop('n'), 'board': build(k.pop('m'), k.pop('f', [])), 'target': 1000}
    if 'belts' in k: d['belts'] = k.pop('belts')
    if 'wr' in k: d['wildRate'] = k.pop('wr')
    d.update(k)
    # blankets: about two thirds of the board has to be tucked in (0 would mean all of it)
    if any('k' in rr for rr in d['board']) and not d.get('cover'): d['cover'] = round(.62 * sum(ch != ' ' for rr in d['board'] for ch in rr))
    elif 'cover' in d and not d['cover']: d.pop('cover')
    # a few sanity rules: belts on rows with room, boss needs hp
    for r, _ in d.get('belts', []): assert sum(ch != ' ' for ch in d['board'][r]) >= 5, (no, r)
    if any('V' in rr for rr in d['board']): assert d.get('boss'), no
    has_goal = any(ch in ''.join(d['board']) for ch in 'mMbBCknwVpud') or d.get('collect') or d.get('bells') or d.get('make') or d.get('goldrush')
    assert has_goal, no
    out.append(d)
json.dump(out, open(D + 'levels36.json', 'w'), ensure_ascii=False, indent=0)
json.dump(WORLDS, open(D + 'worlds36.json', 'w'), ensure_ascii=False)
print('levels', len(out), 'worlds', len(WORLDS))
