"""Corta silencios da narracao (sem mudar a velocidade da fala) e gera timing.json.
uso: python3 trim_narr.py audio/narracao.mp3 CUTS_JSON audio/narracao_curta.wav timing.json"""
import subprocess, sys, json, wave, numpy as np
SR = 44100
src, cuts_json, out_wav, out_json = sys.argv[1:5]
CUTS = json.load(open(cuts_json))          # lista de [ini, fim] por cena, em segundos no mp3
LEAD, TAIL, TAIL_LAST, GAP_MAX, PAD = 0.10, 0.22, 0.50, 0.14, 0.03
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
hop = int(SR * 0.01)
n = len(x) // hop
db = np.array([20 * np.log10(np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) + 1e-9) for i in range(n)])
thr = np.percentile(db, 95) - 35
sp = db > thr
spans, s0 = [], None
for i, v in enumerate(sp):
    if v and s0 is None: s0 = i
    if not v and s0 is not None: spans.append([s0, i]); s0 = None
if s0 is not None: spans.append([s0, n])
mer = [spans[0]]
for a in spans[1:]:
    if (a[0] - mer[-1][1]) * 0.01 < 0.12: mer[-1][1] = a[1]
    else: mer.append(a)
mer = [[a * 0.01, b * 0.01] for a, b in mer]
def fade(seg, f=int(0.010 * SR)):
    seg = seg.copy(); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f); return seg
lines, durs, places, t_scene = [], [], [], 0.0
wav = []
off = 0
for k, (c0, c1) in enumerate(CUTS):
    mine = [s for s in mer if c0 <= (s[0] + s[1]) / 2 < c1]
    pieces = []
    for j, (a, b) in enumerate(mine):
        a2 = max(c0, a - PAD) if j == 0 else a - 0.0
        b2 = min(c1, b + PAD) if j == len(mine) - 1 else b
        pieces.append(x[int(a2 * SR):int(b2 * SR)])
        if j < len(mine) - 1:
            gap = mine[j + 1][0] - b
            keep = min(gap, GAP_MAX)
            pieces.append(x[int(b * SR):int((b + keep / 2) * SR)])
            pieces.append(x[int((mine[j + 1][0] - keep / 2) * SR):int(mine[j + 1][0] * SR)])
    seg = fade(np.concatenate(pieces))
    ln = len(seg) / SR
    tail = TAIL_LAST if k == len(CUTS) - 1 else TAIL
    dur = LEAD + ln + tail
    wav.append(seg)
    lines.append({'offset': off, 'length': len(seg), 'place': t_scene + LEAD})
    off += len(seg); durs.append(dur); t_scene += dur
allv = np.concatenate(wav)
with wave.open(out_wav, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(allv, -1, 1) * 32767).astype('<i2').tobytes())
json.dump({'durs': [round(d, 3) for d in durs], 'total': round(t_scene, 3), 'lines': lines, 'sr': SR}, open(out_json, 'w'))
print('durs', [round(d, 2) for d in durs], 'total', round(t_scene, 2), '(antes 42.4)')
