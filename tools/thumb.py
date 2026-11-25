"""Thumbnail 1080x1920. uso: python3 thumb.py "LINHA BRANCA" "DESTAQUE" "subtitulo" saida.png [tema]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
l1, l2, sub, out = sys.argv[1:5]
th = themes.THEMES[sys.argv[5] if len(sys.argv) > 5 else 'royal']
W, H = 1080, 1920
b0, b1 = th['bg0'], th['bg1']
bg = Image.new('RGB', (W, H)); d = ImageDraw.Draw(bg)
for y in range(H):
    k = y / H; d.line([(0, y), (W, y)], fill=tuple(int(b0[i] * (1 - k) + b1[i] * k) for i in range(3)))
glow = Image.new('RGB', (W, H), (0, 0, 0)); ImageDraw.Draw(glow).ellipse([260, 700, 1100, 1500], fill=tuple(int(c * 0.55) for c in th['a2']))
bg = ImageChops.add(bg, glow.filter(ImageFilter.GaussianBlur(170)))
FB, FM = themes.FONTS[th['font']]
def fit(txt, maxw, start, path=FB):
    s = start
    while ImageFont.truetype(path, s).getlength(txt) > maxw: s -= 4
    return ImageFont.truetype(path, s)
d = ImageDraw.Draw(bg)
def center(txt, y, font, fill):
    x = (W - font.getlength(txt)) / 2
    d.text((x + 4, y + 6), txt, font=font, fill=(0, 0, 0)); d.text((x, y), txt, font=font, fill=fill)
center(l1, 700, fit(l1, 860, 130), (255, 255, 255))
center(l2, 860, fit(l2, 860, 190), th['a1'])
center(sub, 1120, fit(sub, 860, 56, FM), tuple(min(255, c + 90) for c in th['a2']))
lg = Image.open((sys.argv[6] if len(sys.argv) > 6 else os.path.join(themes.ROOT, 'brand', 'royal_signature_transparente.png'))).convert('RGBA'); lg.thumbnail((300, 300))
bg.paste(lg, ((W - lg.width) // 2, 340), lg)
bg.save(out)
