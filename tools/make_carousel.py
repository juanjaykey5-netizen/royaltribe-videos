#!/usr/bin/env python3
"""Gera carrossel Instagram 1080x1350 (4:5) com identidade Royal Signature.
Uso: python3 tools/make_carousel.py spec.json outdir      -> outdir/slide_01.jpg ... (JPEG, pronto para vidIQ)
spec = {"theme": "royal|esmeralda|ameixa|grafite|oceano|por-do-sol", "handle": "@realstart.consultantofc", "slides": [...]}
Tipos: cover(kicker,l1,hl,sub) alert(tag,title,body[],big?) tip(n,title,body[]) list(title,items[]) compare(title,a:{h,items[]},b:{h,items[]}) cta(l1,hl,sub,kw,disc)
ZONA SEGURA: margens 110 px nos lados (o grid do perfil corta ~34 px de cada lado), topo 150 (contador 1/N) e base 170 (pontinhos).
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import themes as TH
W, H = 1080, 1350
MX = 110                 # margem lateral
TOP, BOT = 230, 260      # conteudo so entre y=TOP e y=H-BOT (logo em cima; pontinhos/@ embaixo)
LOGO = os.path.join(HERE, '..', 'brand', 'royal_signature_transparente.png')
WHITE = (255, 255, 255); MUTED = (190, 202, 224); RED = (255, 92, 92)
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
class Ctx:
    def __init__(s, name):
        t = TH.THEMES[name]; s.name = name
        s.bold, s.reg = TH.FONTS[t['font']]
        s.bg0, s.bg1, s.a1, s.a2 = t['bg0'], t['bg1'], t['a1'], t['a2']
    def B(s, n): return font(s.bold, n)
    def R(s, n): return font(s.reg, n)
def background(c, variant=0):
    img = Image.new('RGB', (W, H), c.bg0)
    px = Image.new('RGB', (1, H))
    for y in range(H):
        k = y / (H - 1)
        px.putpixel((0, y), tuple(int(c.bg0[i] + (c.bg1[i] - c.bg0[i]) * k) for i in range(3)))
    img = px.resize((W, H))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    pos = [(-120, 180, 520), (1000, 620, 460), (300, 1250, 560)]
    for i, (x, y, r) in enumerate(pos):
        x, y = (x + variant * 160) % 1200 - 60, (y + variant * 90) % 1500 - 60
        col = c.a2 if i % 2 == 0 else c.a1
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (34,))
    ov = ov.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img.convert('RGBA'), ov)
    return img
def wrap(d, txt, f, maxw):
    out, cur = [], ''
    for w in txt.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out
def fit(d, txt, fn, size, maxw, maxlines, minsize=34):
    while size > minsize:
        ls = wrap(d, txt, fn(size), maxw)
        if len(ls) <= maxlines and all(d.textlength(l, font=fn(size)) <= maxw for l in ls): return size, ls
        size -= 4
    return minsize, wrap(d, txt, fn(minsize), maxw)
def text(d, xy, s, f, fill, anchor='la', shadow=True):
    x, y = xy
    if shadow: d.text((x + 2, y + 3), s, font=f, fill=(0, 0, 0, 90), anchor=anchor)
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)
def block(d, ls, f, x, y, fill, lh, anchor='la'):
    for l in ls:
        text(d, (x, y), l, f, fill, anchor); y += lh
    return y
def chrome(img, c, i, n, handle):
    d = ImageDraw.Draw(img)
    lg = Image.open(LOGO).convert('RGBA'); h = 140; lg = lg.resize((int(lg.width * h / lg.height), h), Image.LANCZOS)
    img.alpha_composite(lg, (MX, 52))                             # logo sempre no mesmo lugar (canto sup. esquerdo)
    for k in range(n):                                            # pontinhos (acima da zona do indicador do IG)
        cx = W // 2 + (k - (n - 1) / 2) * 30
        d.ellipse([cx - 7, H - 205, cx + 7, H - 191], fill=c.a1 if k == i else (255, 255, 255, 70))
    text(d, (W // 2, H - 150), handle, c.R(30), MUTED, 'mm', False)
    if i < n - 1:
        text(d, (W - MX - 44, H - 150), 'arraste', c.R(28), c.a1, 'rm', False)
        x = W - MX - 24; y = H - 150
        d.line([x - 12, y - 11, x, y, x - 12, y + 11], fill=c.a1, width=5, joint='curve')
def cover(img, c, s, i, n, handle):
    d = ImageDraw.Draw(img); mw = W - 2 * MX
    y = 300
    if s.get('kicker'):
        d.rounded_rectangle([MX, y, MX + d.textlength(s['kicker'], font=c.B(32)) + 56, y + 62], 31, fill=c.a1)
        text(d, (MX + 28, y + 31), s['kicker'], c.B(32), c.bg0, 'lm', False); y += 120
    sz, ls = fit(d, s['l1'], c.B, 88, mw, 3); y = block(d, ls, c.B(sz), MX, y, WHITE, int(sz * 1.18))
    sz, ls = fit(d, s['hl'], c.B, 128, mw, 3); y = block(d, ls, c.B(sz), MX, y + 10, c.a1, int(sz * 1.12))
    if s.get('sub'):
        sz, ls = fit(d, s['sub'], c.R, 42, mw, 3); block(d, ls, c.R(sz), MX, y + 30, MUTED, int(sz * 1.35))
def alert(img, c, s, i, n, handle):
    d = ImageDraw.Draw(img); mw = W - 2 * MX; y = 300
    tag = s.get('tag', 'ALERTA')
    wtag = d.textlength(tag, font=c.B(34)) + 64
    d.rounded_rectangle([MX, y, MX + wtag, y + 64], 14, fill=RED)
    text(d, (MX + 32, y + 32), '⚠  ' if False else tag, c.B(34), WHITE, 'lm', False); y += 110
    if s.get('big'):
        sz, ls = fit(d, s['big'], c.B, 190, mw, 1); text(d, (MX, y), ls[0], c.B(sz), c.a1); y += int(sz * 1.2)
    sz, ls = fit(d, s['title'], c.B, 70, mw, 4); y = block(d, ls, c.B(sz), MX, y, WHITE, int(sz * 1.2)) + 24
    for b in s.get('body', []):
        sz, ls = fit(d, b, c.R, 40, mw - 50, 3)
        d.ellipse([MX, y + 14, MX + 18, y + 32], fill=c.a2)
        y = block(d, ls, c.R(sz), MX + 44, y, (232, 238, 250), int(sz * 1.35)) + 22
def tip(img, c, s, i, n, handle):
    d = ImageDraw.Draw(img); mw = W - 2 * MX; y = 300
    d.ellipse([MX, y, MX + 130, y + 130], fill=c.a1)
    text(d, (MX + 65, y + 68), str(s['n']), c.B(78), c.bg0, 'mm', False); y += 180
    sz, ls = fit(d, s['title'], c.B, 74, mw, 3); y = block(d, ls, c.B(sz), MX, y, WHITE, int(sz * 1.2)) + 26
    for b in s.get('body', []):
        sz, ls = fit(d, b, c.R, 42, mw, 4); y = block(d, ls, c.R(sz), MX, y, (232, 238, 250), int(sz * 1.38)) + 20
def lst(img, c, s, i, n, handle):
    d = ImageDraw.Draw(img); mw = W - 2 * MX; y = 300
    sz, ls = fit(d, s['title'], c.B, 70, mw, 3); y = block(d, ls, c.B(sz), MX, y, WHITE, int(sz * 1.2)) + 30
    for it in s['items']:
        sz, ls = fit(d, it, c.R, 42, mw - 110, 2)
        hh = max(96, len(ls) * int(sz * 1.3) + 36)
        d.rounded_rectangle([MX, y, W - MX, y + hh], 22, fill=(255, 255, 255, 30))
        d.rounded_rectangle([MX, y, MX + 10, y + hh], 5, fill=c.a1)
        d.ellipse([MX + 34, y + hh // 2 - 22, MX + 78, y + hh // 2 + 22], fill=c.a2)
        cx, cy = MX + 56, y + hh // 2
        d.line([cx - 10, cy, cx - 3, cy + 8, cx + 11, cy - 8], fill=c.bg0, width=6, joint='curve')
        block(d, ls, c.R(sz), MX + 104, y + (hh - len(ls) * int(sz * 1.3)) // 2 + 2, WHITE, int(sz * 1.3)); y += hh + 20
def compare(img, c, s, i, n, handle):
    d = ImageDraw.Draw(img); mw = W - 2 * MX; y = 300
    sz, ls = fit(d, s['title'], c.B, 62, mw, 2); y = block(d, ls, c.B(sz), MX, y, WHITE, int(sz * 1.2)) + 30
    cw = (mw - 24) // 2; hmax = [0, 0]
    for k, (side, col) in enumerate(((s['a'], RED), (s['b'], c.a2))):
        x0 = MX + k * (cw + 24); yy = y
        rows = [fit(d, it, c.R, 36, cw - 56, 4, 28) for it in side['items']]
        hh = 120 + sum(len(l2) * int(sz2 * 1.3) + 26 for sz2, l2 in rows) + 20
        hh = max(hh, 440) if k == 0 else hh
        hmax[k] = hh
        d.rounded_rectangle([x0, yy, x0 + cw, yy + hh], 26, fill=(255, 255, 255, 34))
        d.rounded_rectangle([x0, yy, x0 + cw, yy + 14], 7, fill=col)
        text(d, (x0 + 28, yy + 44), side['h'], c.B(40), col, 'la', False); yy += 120
        for sz2, l2 in rows:
            yy = block(d, l2, c.R(sz2), x0 + 28, yy, WHITE, int(sz2 * 1.3)) + 26
def cta(img, c, s, i, n, handle):
    d = ImageDraw.Draw(img); mw = W - 2 * MX; y = 300
    sz, ls = fit(d, s['l1'], c.B, 78, mw, 3); y = block(d, ls, c.B(sz), MX, y, WHITE, int(sz * 1.2))
    sz, ls = fit(d, s['hl'], c.B, 110, mw, 2); y = block(d, ls, c.B(sz), MX, y + 6, c.a1, int(sz * 1.12)) + 20
    if s.get('sub'):
        sz, ls = fit(d, s['sub'], c.R, 40, mw, 3); y = block(d, ls, c.R(sz), MX, y, (232, 238, 250), int(sz * 1.35)) + 30
    kw = s.get('kw', 'CONSULTORIA')
    bw = W - 2 * MX; d.rounded_rectangle([MX, y, MX + bw, y + 150], 30, fill=c.a1)
    text(d, (W // 2, y + 46), 'Mande no direct a palavra', c.R(34), c.bg0, 'mm', False)
    text(d, (W // 2, y + 105), kw, c.B(60), c.bg0, 'mm', False); y += 190
    if s.get('disc'):
        sz, ls = fit(d, s['disc'], c.R, 26, mw, 4, 22); block(d, ls, c.R(sz), MX, y, MUTED, int(sz * 1.35))
KINDS = {'cover': cover, 'alert': alert, 'tip': tip, 'list': lst, 'compare': compare, 'cta': cta}
def build(spec_path, outdir):
    spec = json.load(open(spec_path)); os.makedirs(outdir, exist_ok=True)
    c = Ctx(spec.get('theme', 'royal')); handle = spec.get('handle', '@realstart.consultantofc'); sl = spec['slides']; n = len(sl)
    outs = []
    for i, s in enumerate(sl):
        img = background(c, variant=i % 3)
        chrome(img, c, i, n, handle)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        KINDS[s['type']](layer, c, s, i, n, handle)
        bb = layer.getbbox()
        if bb:                                         # centraliza o conteudo na faixa segura (TOP..H-BOT)
            top, bot = TOP, H - BOT
            dy = int((top + bot) / 2 - (bb[1] + bb[3]) / 2)
            if bb[1] + dy < top: dy = top - bb[1]
            if bb[3] + dy > bot: print('AVISO: slide %d passa da zona segura em %d px' % (i + 1, bb[3] + dy - bot))
            layer = layer.transform(layer.size, Image.AFFINE, (1, 0, 0, 0, 1, -dy))
        img = Image.alpha_composite(img, layer)
        p = os.path.join(outdir, 'slide_%02d.jpg' % (i + 1)); img.convert('RGB').save(p, quality=92, subsampling=0); outs.append(p)
    return outs
if __name__ == '__main__':
    for p in build(sys.argv[1], sys.argv[2]): print(p)
