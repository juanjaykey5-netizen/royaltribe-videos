import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
# uso: python3 thumb.py "LINHA BRANCA" "DESTAQUE AMARELO" "subtitulo" saida.png
l1,l2,sub,out=sys.argv[1:5]
W,H=1080,1920
bg=Image.new("RGB",(W,H),(8,16,48))
d=ImageDraw.Draw(bg)
for y in range(H):
    t=y/H; d.line([(0,y),(W,y)],fill=(int(8+12*t),int(16+14*t),int(48+40*t)))
glow=Image.new("RGB",(W,H),(0,0,0)); g=ImageDraw.Draw(glow); g.ellipse([300,700,1100,1500],fill=(14,70,90))
glow=glow.filter(ImageFilter.GaussianBlur(160))
from PIL import ImageChops
bg=ImageChops.add(bg,glow)
F="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
import glob
c=glob.glob("/usr/share/fonts/**/Poppins-Bold.ttf",recursive=True)+glob.glob("/home/claude/**/Poppins-Bold.ttf",recursive=True)
F=c[0]
def fit(txt,maxw,start):
    s=start
    while ImageFont.truetype(F,s).getlength(txt)>maxw: s-=4
    return ImageFont.truetype(F,s)
d=ImageDraw.Draw(bg)
def center(txt,y,font,fill):
    w=font.getlength(txt); x=(W-w)/2
    d.text((x+4,y+6),txt,font=font,fill=(0,0,0)); d.text((x,y),txt,font=font,fill=fill)
f1=fit(l1,860,130); center(l1,700,f1,(255,255,255))
f2=fit(l2,860,190); center(l2,860,f2,(245,184,0))
f3=fit(sub,860,56); center(sub,1120,f3,(190,205,230))
lg=Image.open("/home/claude/vid/brand/royal_signature_transparente.png").convert("RGBA")
lg.thumbnail((300,300))
bg.paste(lg,((W-lg.width)//2,340),lg)
bg.save(out)
