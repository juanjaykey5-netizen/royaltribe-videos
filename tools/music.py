import numpy as np, subprocess
SR=44100; DUR=42.4; BPM=92
beat=60/BPM; bar=beat*4
n=int(SR*DUR); t=np.arange(n)/SR
mix=np.zeros(n)
def hz(m): return 440*2**((m-69)/12)
# C - G - Am - F, triads (midi)
chords=[(48,[60,64,67]),(43,[59,62,67]),(45,[60,64,69]),(41,[60,65,69])]
def add(sig,start):
    i=int(start*SR); j=min(n,i+len(sig))
    if i<n: mix[i:j]+=sig[:j-i]
nb=int(DUR/bar)+1
for b in range(nb):
    root,tri=chords[b%4]; s0=b*bar
    L=int((bar+0.6)*SR); tt=np.arange(L)/SR
    # pad
    env=np.minimum(tt/0.5,1)*np.exp(-np.maximum(tt-bar,0)*6)
    pad=np.zeros(L)
    for m in tri:
        for det in (-0.12,0.12):
            f=hz(m-12)*2**(det/12)
            pad+=np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt)
    add(0.05*pad*env,s0)
    # bass on beats 1 and 3
    for k in (0,2):
        Lb=int(1.1*SR); tb=np.arange(Lb)/SR
        add(0.30*np.sin(2*np.pi*hz(root)*tb)*np.exp(-tb*3.2)*np.minimum(tb/0.01,1),s0+k*beat)
    # arpeggio, 8th notes
    seq=[tri[0],tri[1],tri[2],tri[1]+12,tri[2],tri[1],tri[0]+12,tri[1]]
    for k,m in enumerate(seq):
        La=int(0.9*SR); ta=np.arange(La)/SR
        f=hz(m)
        pl=(np.sin(2*np.pi*f*ta)+0.3*np.sin(2*np.pi*2*f*ta))*np.exp(-ta*6)*np.minimum(ta/0.005,1)
        add(0.09*pl,s0+k*beat/2)
    # soft hat on off-beats
    for k in range(4):
        Lh=int(0.08*SR); th=np.arange(Lh)/SR
        rng=np.random.default_rng(b*4+k)
        h=np.diff(rng.standard_normal(Lh+1))*np.exp(-th*60)
        add(0.07*h,s0+k*beat+beat/2)
# simple echo
d=int(0.33*SR); e=mix.copy(); e[d:]+=0.28*mix[:-d]; mix=e
mix*=np.minimum(t/1.0,1)*np.minimum((DUR-t)/2.0,1)
mix=mix/np.max(np.abs(mix))*0.6
st=np.stack([mix,np.roll(mix,int(0.012*SR))],1)
pcm=(st*32767).astype('<i2').tobytes()
p=subprocess.run(['ffmpeg','-y','-loglevel','error','-f','s16le','-ar',str(SR),'-ac','2','-i','-','-b:a','192k','audio/musica.mp3'],input=pcm)
print('ok',p.returncode)
