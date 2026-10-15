#!/bin/bash
# regression suite for V18; each test writes r_<name>.txt
cd "$(dirname "$0")"
python3 mk_test12.py && NOFIX27=1 NOFIX35=1 NO36=1 LV12=levels12test.json OUT12=gametest.html python3 patch12.py > /dev/null
t() { local name=$1; shift; echo "== $name $(date +%T)" >> r_all.log; timeout 1200 "$@" > r_$name.txt 2>&1; echo "   exit $? $(date +%T)" >> r_all.log; }
rm -f r_all.log
GAME=gametest.html t new12 python3 test_new12.py
t gate python3 test_gate.py
t learn python3 test_learn.py "" 1 0
t kit python3 test_kit.py
t learnpause python3 test_learnpause.py
t chestlesson python3 test_chestlesson.py
t chestwalk python3 test_chestwalk.py
t jar python3 test_jar.py
t r1 python3 test_r1.py
t r2 python3 test_r2.py
t feat python3 test_feat.py
t bell python3 test_bell.py
t shapes python3 test_shapes.py
t fire python3 test_fire.py
t levels python3 test_levels.py 1,2,9,13,18,24,40,61,64,80,100,137,155,160
t soak python3 test_soak.py game.html 61,63,68,73,77,80,84,88,95,100,104,109,120,133,137,140,144,152,158,160 14
t small python3 test_small.py
t narrow python3 test_narrow.py
t walk python3 test_walk.py
t walk12 python3 test_walk12.py
t states python3 test_states.py
t replay python3 test_replay.py
t win python3 test_win.py
t zoom python3 test_zoom.py
t fps python3 test_fps.py
t music python3 test_music_rt.py
t flow python3 test_flow.py
t skip python3 test_skip.py
t intro python3 test_intro.py
t purr python3 test_purr.py
t v27 python3 test_v27.py
t paw python3 test_paw.py
t v30 python3 test_v30.py
t save35 python3 test_save35.py
t v36 python3 test_v36.py
t v38 python3 test_v38.py
t levels36 python3 test_levels.py 161,162,168,181,196,201,211,220,240,257,260
GAME=game.html t v40 python3 test_v40.py
t v41 python3 test_v41.py
t card41 python3 test_card41.py
t start41 python3 test_start41.py 1
echo "== done $(date +%T)" >> r_all.log
