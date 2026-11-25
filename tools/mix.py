import subprocess, sys, numpy as np
SR=44100
narr, music_path, video, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
DUR=42.4
def decode(path, ch):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-vn','-ac',str(ch),'-ar',str(SR),'-f','s16le','-'],capture_output=True,check=True).stdout
    x=np.frombuffer(raw,dtype='<i2').astype(np.float64)/32768
    return x.reshape(-1,ch) if ch>1 else x
v=decode(narr,1)
m=decode(music_path,2)
N=int(DUR*SR)
cuts=[(0,3.396),(3.396,10.475),(10.475,15.464),(15.464,25.652),(25.652,32.967),(32.967,37.251)]
place=[0.15,4.65,12.15,19.15,29.75,37.55]
voice=np.zeros(N)
for (a,b),p in zip(cuts,place):
    seg=v[int(a*SR):int(b*SR)].copy()
    f=int(0.02*SR); seg[:f]*=np.linspace(0,1,f); seg[-f:]*=np.linspace(1,0,f)
    i=int(p*SR); j=min(N,i+len(seg)); voice[i:j]+=seg[:j-i]
# voz: normaliza para RMS da fala = -17 dBFS
act=np.abs(voice)>0.01
g=10**(-17/20)/np.sqrt((voice[act]**2).mean())
voice*=g
# envelope da voz para abaixar a musica enquanto fala
env=np.abs(voice)
k=int(0.05*SR); env=np.convolve(env,np.ones(k)/k,mode='same')
env=(env>0.02).astype(float)
# suaviza ataque (60ms) e liberacao (400ms)
sm=np.zeros(N); c=0.0
a_up=1-np.exp(-1/(0.06*SR)); a_dn=1-np.exp(-1/(0.40*SR))
for i in range(N):
    c+= (a_up if env[i]>c else a_dn)*(env[i]-c); sm[i]=c
mm=np.zeros((N,2)); L=min(N,len(m)); mm[:L]=m[:L]
mrms=np.sqrt((mm**2).mean())
mm*=10**(-23/20)/mrms           # musica ~ -23 dBFS nas pausas
duck=10**(-9/20)                # -9 dB enquanto a voz fala
gain=1-(1-duck)*sm
mm*=gain[:,None]
mix=mm+voice[:,None]
pk=np.abs(mix).max()
if pk>0.95: mix=np.tanh(mix/pk*1.2)/np.tanh(1.2)*0.95
pcm=(np.clip(mix,-1,1)*32767).astype('<i2').tobytes()
tmp=out+'.part.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',video,'-f','s16le','-ar',str(SR),'-ac','2','-i','-','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(DUR),'-movflags','+faststart',tmp],input=pcm,check=True)
import os; os.rename(tmp,out)
print('ok')
