"""(run in a folder with cleanN.wav made from the recordings) chomp bank v2: whole chewing bursts (0.75 s, two to four crunches each) instead of single crunches, so it sounds like eating"""
import numpy as np, scipy.io.wavfile as wf, scipy.signal as ss, json, subprocess, base64, random
SR = 48000; WIN = .75; SLOT = .85; PRE = .03
def load(f): sr, x = wf.read(f); return (x.astype(np.float32) / 32768) if x.dtype == np.int16 else x.astype(np.float32)
def band(x, lo, hi): b, a = ss.butter(4, [lo / (SR / 2), hi / (SR / 2)], 'band'); return ss.filtfilt(b, a, x)
def env(x, win=.005): n = int(SR * win); return np.sqrt(np.convolve(x * x, np.ones(n) / n, 'same'))
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
cands = []
for i in range(6):
    x = load(f'clean{i}.wav'); hi = env(band(x, 2000, 12000)); lo = env(band(x, 150, 900))
    fl = ss.medfilt(hi[::48], 201); fl = np.repeat(fl, 48)[:len(hi)]
    pk, _ = ss.find_peaks(hi, height=fl * 4 + 1e-4, distance=int(.1 * SR), prominence=fl * 3)
    strong = [p for p in pk if hi[p] > np.percentile(hi[pk], 35)]
    for p in strong:
        s0 = p - int(.015 * SR); s1 = s0 + int(WIN * SR)
        if s0 < 0 or s1 > len(x): continue
        seg = x[s0:s1]
        inside = [q for q in pk if s0 <= q < s1 - int(.12 * SR)]
        late = [q for q in inside if q - s0 > int(.28 * SR)]
        low = float(np.mean(lo[s0:s1]) / (np.mean(hi[s0:s1]) + 1e-6))
        if len(inside) < 2 or not late or low > 1.6 or np.max(np.abs(seg)) > .98: continue
        # no single crack louder than twice the first one (those were bangs, not chewing)
        if max(hi[q] for q in inside) > 2.2 * hi[p]: continue
        score = len(inside) * (hi[p] / (np.median(fl[s0:s1]) + 1e-6)) / (1 + low)
        cands.append({'src': i, 's0': s0, 's1': s1, 't': p / SR, 'n': len(inside), 'score': float(score), 'low': low})
print('windows', len(cands), {i: sum(c['src'] == i for c in cands) for i in range(6)})
quota = {1: 4, 2: 4, 3: 4, 4: 8, 5: 2, 0: 4}
pick = []
for s, q in quota.items():
    taken = []
    for c in sorted([c for c in cands if c['src'] == s], key=lambda c: -c['score']):
        if any(not (c['s1'] <= t['s0'] or c['s0'] >= t['s1']) for t in taken): continue
        taken.append(c)
        if len(taken) >= q: break
    pick += taken
print('picked', len(pick), {s: sum(c['src'] == s for c in pick) for s in quota}, 'crunches per burst', [c['n'] for c in pick])
srcs = {i: load(f'clean{i}.wav') for i in range(6)}
old_rms = np.median([rms(srcs[0][c['s0']:c['s1']]) for c in cands if c['src'] == 0])
target = old_rms * 1.35
random.Random(5).shuffle(pick)
bank = np.zeros(int(SR * SLOT * len(pick)), np.float32); offs = []
for j, c in enumerate(pick):
    seg = srcs[c['src']][c['s0']:c['s1']].copy()
    seg *= target / rms(seg)
    pv = np.max(np.abs(seg))
    if pv > .9: seg *= .9 / pv
    fi, fo = int(.004 * SR), int(.14 * SR)
    seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
    a = int(SR * (j * SLOT + PRE)); bank[a:a + len(seg)] = seg; offs.append(round(j * SLOT, 3))
wf.write('bank2.wav', SR, (bank * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'bank2.wav', '-ar', '44100', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '56k', 'bank2.mp3'], check=True)
b64 = base64.b64encode(open('bank2.mp3', 'rb').read()).decode()
json.dump({'offs': offs, 'b64': b64, 'len': WIN, 'slot': SLOT, 'src': [(c['src'], round(c['t'], 3), c['n']) for c in pick]}, open('bank2.json', 'w'))
print('bank2', len(pick), 'bursts', round(len(bank) / SR, 1), 's, b64', len(b64))
