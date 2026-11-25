"""Gera trilhas diferentes. uso: python3 music.py ESTILO saida.mp3 [duracao_s]
estilos: lofi bright calm groove warm"""
import sys, numpy as np, subprocess
SR = 44100
def hz(m): return 440 * 2 ** ((m - 69) / 12)
STY = {
 'lofi':   dict(bpm=92,  ch=[(48,[60,64,67]),(43,[59,62,67]),(45,[60,64,69]),(41,[60,65,69])], arp=[0,1,2,4,2,1,3,1], h=(1,.3), dec=6, pad=.05, bass=(0,2), hat=.07, kick=0, echo=.28),
 'bright': dict(bpm=110, ch=[(50,[62,66,69]),(45,[61,64,69]),(47,[62,66,71]),(43,[62,67,71])], arp=[2,2,1,2,0,2,1,2], h=(1,.5,.2), dec=9, pad=.04, bass=(0,1,2,3), hat=.09, kick=1, echo=.18),
 'calm':   dict(bpm=72,  ch=[(45,[57,60,64]),(41,[57,60,65]),(48,[55,60,64]),(43,[55,59,62])], arp=[0,-1,2,-1,1,-1,2,-1], h=(1,.15), dec=3.2, pad=.09, bass=(0,), hat=0, kick=0, echo=.38),
 'groove': dict(bpm=100, ch=[(40,[59,64,67]),(48,[60,64,67]),(43,[59,62,67]),(50,[62,66,69])], arp=[0,-1,1,-1,2,1,-1,1], h=(1,.6,.3), dec=8, pad=.035, bass=(0,1.5,2,3.5), hat=.1, kick=1, echo=.15),
 'warm':   dict(bpm=84,  ch=[(48,[60,64,67,71]),(45,[60,64,67,69]),(50,[60,65,69,72]),(43,[59,65,67,71])], arp=[0,2,3,2,1,3,2,1], h=(1,.4,.12), dec=4.5, pad=.05, bass=(0,2), hat=.05, kick=0, echo=.3),
}
def gen(style, dur, out):
    p = STY[style]; beat = 60 / p['bpm']; bar = beat * 4; n = int(SR * dur); t = np.arange(n) / SR; mix = np.zeros(n)
    def add(sig, start):
        i = int(start * SR); j = min(n, i + len(sig))
        if i < n: mix[i:j] += sig[:j - i]
    for b in range(int(dur / bar) + 1):
        root, tri = p['ch'][b % 4]; s0 = b * bar
        L = int((bar + .6) * SR); tt = np.arange(L) / SR
        env = np.minimum(tt / .5, 1) * np.exp(-np.maximum(tt - bar, 0) * 6); pad = np.zeros(L)
        for m in tri:
            for det in (-.12, .12):
                f = hz(m - 12) * 2 ** (det / 12); pad += np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * 2 * f * tt)
        add(p['pad'] * pad * env, s0)
        for k in p['bass']:
            tb = np.arange(int(1.1 * SR)) / SR
            add(.30 * np.sin(2 * np.pi * hz(root) * tb) * np.exp(-tb * 3.2) * np.minimum(tb / .01, 1), s0 + k * beat)
        if p['kick']:
            for k in range(4):
                tk = np.arange(int(.25 * SR)) / SR
                add(.28 * np.sin(2 * np.pi * (60 + 90 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 14), s0 + k * beat)
        for k, idx in enumerate(p['arp']):
            if idx < 0: continue
            m = tri[idx % len(tri)] + (12 if idx >= len(tri) else 0); ta = np.arange(int(.9 * SR)) / SR; f = hz(m)
            pl = sum(w * np.sin(2 * np.pi * f * (i + 1) * ta) for i, w in enumerate(p['h'])) * np.exp(-ta * p['dec']) * np.minimum(ta / .005, 1)
            add(.09 * pl, s0 + k * beat / 2)
        if p['hat']:
            for k in range(4):
                th = np.arange(int(.08 * SR)) / SR; rng = np.random.default_rng(b * 4 + k)
                add(p['hat'] * np.diff(rng.standard_normal(len(th) + 1)) * np.exp(-th * 60), s0 + k * beat + beat / 2)
    d = int(.33 * SR); e = mix.copy(); e[d:] += p['echo'] * mix[:-d]; mix = e
    mix *= np.minimum(t / 1.0, 1) * np.minimum((dur - t) / 2.0, 1); mix = mix / np.max(np.abs(mix)) * .6
    st = np.stack([mix, np.roll(mix, int(.012 * SR))], 1)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-b:a', '192k', out], input=(st * 32767).astype('<i2').tobytes(), check=True)
if __name__ == '__main__':
    gen(sys.argv[1], float(sys.argv[3]) if len(sys.argv) > 3 else 75, sys.argv[2])
