import json, sys, collections
ev = json.load(open(sys.argv[1])); ev = ev['traceEvents'] if isinstance(ev, dict) else ev
X = [e for e in ev if e.get('ph') == 'X' and 'dur' in e]
th = collections.Counter((e['pid'], e['tid']) for e in X if e['name'] == 'FunctionCall').most_common(1)[0][0]
M = [e for e in X if (e['pid'], e['tid']) == th]
tot = collections.Counter(); cnt = collections.Counter()
for e in M: tot[e['name']] += e['dur']; cnt[e['name']] += 1
keys = ['FunctionCall', 'Blink.ForcedStyleAndLayout.UpdateTime', 'UpdateLayoutTree', 'Layout', 'PrePaint', 'Paint', 'Layerize', 'CanvasResourceProviderSharedImage::ProduceCanvasResource', 'Blink.Animate.UpdateTime', 'ParseHTML', 'HitTest']
print(' | '.join(f'{k.split("::")[-1][:22]} {tot[k] / 1000:.0f}ms/{cnt[k]}' for k in keys))
