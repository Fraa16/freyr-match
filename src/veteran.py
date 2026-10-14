"""regression tests play as a player who has seen every lesson; the lesson tests clear this themselves"""
import json
ALL = ['basics', 'cat', 'laser', 'milk', 'nip', 'boxes', 'bowl', 'purr', 'hard', 'bells', 'combo', 'boosts', 'locks', 'streak', 'paw',
       'box2', 'gold', 'milk2', 'hard2', 'claw', 'blanket', 'swap', 'wet', 'picnic', 'boss', 'chest',
       'box3', 'order', 'gift', 'cukes', 'clock', 'feather', 'turbo', 'superpounce', 'goldrush']
INIT = "try { if (!localStorage.getItem('wm-learn')) localStorage.setItem('wm-learn', '%s'); if (!localStorage.getItem('wm-intro')) localStorage.setItem('wm-intro', '1'); } catch (e) {}" % json.dumps({k: True for k in ALL})
def veteran(pg): pg.add_init_script(INIT)
_veteran_plain = veteran
SNAP = "window.__ls0 = JSON.stringify(Object.assign({}, localStorage));"
def _stable_reload(pg):
    """make reloads keep localStorage. In this sandbox Chromium sometimes drops the writes made just before
    a reload (V17 too, about 1 in 6). Compare what the new page starts with and restore + reload again if needed."""
    pg.add_init_script(SNAP)
    orig = pg.reload
    def reload(*a, **k):
        want = pg.evaluate('JSON.stringify(Object.assign({}, localStorage))'); W = json.loads(want)
        for attempt in range(6):
            pg.wait_for_timeout(150)
            r = orig(*a, **k)
            G = json.loads(pg.evaluate('window.__ls0 || "{}"'))
            if all(G.get(key) == v for key, v in W.items()): return r
            pg.evaluate('(s) => { localStorage.clear(); const o = JSON.parse(s); for (const k in o) localStorage.setItem(k, o[k]); }', want)
        return r
    pg.reload = reload
SKIP_WAKE = "() => { try { if (introRun && introRun.kind === 'wake') { mapSkip = true; return true; } } catch (e) {} return false; }"
def _skip_wake(pg):
    """V30: every start Freyr naps by his level until a tap. The regression tests skip that (test_v30 covers it)."""
    try:
        if pg.evaluate(SKIP_WAKE): pg.wait_for_function("!introRun", timeout=6000, polling=50)
    except Exception: pass
def _wrap_nav(pg):
    for name in ('reload', 'goto'):
        orig = getattr(pg, name)
        def nav(*a, _orig=orig, **k):
            r = _orig(*a, **k); _skip_wake(pg); return r
        setattr(pg, name, nav)
def veteran(pg):
    _veteran_plain(pg)
    _stable_reload(pg)
    _wrap_nav(pg)
SEEN_INTRO = "try { if (!localStorage.getItem('wm-intro')) localStorage.setItem('wm-intro', '1'); } catch (e) {}"
def seen_intro(pg):
    """the lesson tests start as new players but have seen the intro (test_intro covers it); reloads keep localStorage too"""
    pg.add_init_script(SEEN_INTRO)
    _stable_reload(pg)
    _wrap_nav(pg)
