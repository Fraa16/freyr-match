"""(run in a folder with cleanN.wav made from the recordings, see chomp37.json src for which ones) builds the chomp bank: the best crunches from Freyr's recordings, cleaned, evened out, one per 0.45 s slot"""
import numpy as np, scipy.io.wavfile as wf, scipy.signal as ss, json, subprocess, base64, random
SR = 48000; SLOT = .45; PRE = .03; LEN = .33
def load(f): sr, x = wf.read(f); return (x.astype(np.float32) / 32768) if x.dtype == np.int16 else x.astype(np.float32)
def band(x, lo, hi): b, a = ss.butter(4, [lo / (SR / 2), hi / (SR / 2)], 'band'); return ss.filtfilt(b, a, x)
def env(x, win=.005): n = int(SR * win); return np.sqrt(np.convolve(x * x, np.ones(n) / n, 'same'))
cands = []
for i in range(6):
    x = load(f'clean{i}.wav'); hi = env(band(x, 2000, 12000)); lo = env(band(x, 150, 900))
    fl = ss.medfilt(hi[::48], 201); fl = np.repeat(fl, 48)[:len(hi)]
    pk, _ = ss.find_peaks(hi, height=fl * 4 + 1e-4, distance=int(.12 * SR), prominence=fl * 3)
    allpk = list(pk)
    for j, p in enumerate(pk):
        s0 = p - int(.012 * SR); s1 = s0 + int(LEN * SR)
        if s0 < 0 or s1 > len(x): continue
        # the slice ends before the next crunch that is at least half as loud
        for q in allpk[j + 1:]:
            if q >= s1: break
            if hi[q] > .5 * hi[p] and q - s0 > int(.06 * SR): s1 = q - int(.015 * SR); break
        if s1 - s0 < int(.14 * SR): continue
        seg = x[s0:s1].copy()
        # the attack has to be the loudest part
        if np.max(np.abs(seg[int(.06 * SR):])) > .8 * np.max(np.abs(seg[:int(.06 * SR)])): continue
        if len(seg) > int(.2 * SR) and np.max(np.abs(seg[int(.18 * SR):])) > .45 * np.max(np.abs(seg[:int(.06 * SR)])): continue
        crest = hi[p] / (np.median(fl[s0:s1]) + 1e-6)
        low = float(np.mean(lo[s0:s1]) / (np.mean(hi[s0:s1]) + 1e-6))
        # a crunch: sharp start, broadband, not drowned in low rumble; also: no clipping
        if crest < 7 or low > 1.6 or np.max(np.abs(seg)) > .98: continue
        cands.append({'src': i, 't': p / SR, 'crest': float(crest), 'low': low, 'seg': seg})
print('candidates', len(cands), {i: sum(c['src'] == i for c in cands) for i in range(6)})
# best per source, the new recordings first (the old one only fills up)
quota = {1: 10, 2: 5, 3: 7, 4: 12, 5: 3, 0: 4}
pick = []
for s, q in quota.items():
    cs = sorted([c for c in cands if c['src'] == s], key=lambda c: -(c['crest'] / (1 + c['low'])))[:q]
    pick += cs
print('picked', len(pick), {s: sum(c['src'] == s for c in pick) for s in quota})
# even them out: the loudness of the first 120 ms is the same for all, peaks stay below -1.5 dBFS
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
old_level = np.median([rms(c['seg'][:int(.06 * SR)]) for c in cands if c['src'] == 0]) if any(c['src'] == 0 for c in cands) else .08
target = old_level * 1.5
bank = np.zeros(int(SR * SLOT * len(pick)), np.float32); offs = []
random.Random(7).shuffle(pick)
for j, c in enumerate(pick):
    seg = c['seg'] * (target / rms(c['seg'][:int(.06 * SR)]))
    pkv = np.max(np.abs(seg));
    if pkv > .9: seg *= .9 / pkv
    n = len(seg); fi = int(.003 * SR); fo = int(.07 * SR)
    seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
    a = int(SR * (j * SLOT + PRE)); bank[a:a + n] = seg; offs.append(round(j * SLOT, 3))
wf.write('bank.wav', SR, (bank * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'bank.wav', '-ar', '44100', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '56k', 'bank.mp3'], check=True)
b64 = base64.b64encode(open('bank.mp3', 'rb').read()).decode()
json.dump({'offs': offs, 'b64': b64, 'slot': SLOT, 'n': len(pick), 'src': [(c['src'], round(c['t'], 3)) for c in pick]}, open('bank.json', 'w'))
print('bank', len(pick), 'slices', round(len(bank) / SR, 1), 's, mp3', len(open('bank.mp3', 'rb').read()), 'bytes, b64', len(b64), 'old level %.4f target %.4f' % (old_level, target))
