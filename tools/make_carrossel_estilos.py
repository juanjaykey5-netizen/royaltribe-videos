#!/usr/bin/env python3
"""Carrosseis de financas com ESTILOS visuais bem diferentes entre si (alem do padrao make_carousel_fin.py).
Uso: python3 tools/make_carrossel_estilos.py spec.json outdir [ig|tiktok|both]
spec = {"estilo": "jornal|poster|quiz", "theme": cor, "font": fonte(opcional), "handle": "@...", "slides": [...]}
Tipos de slide (todos os estilos): cover(kicker,l1,hl,sub)  point(tag,n,title,body[])  mito(myth,fact,ref)  list(title,items[])
  q(question,options[],answer,why)  cta(l1,hl,sub,kw,disc)
Estilos:
  jornal  papel creme, faixa escura com logo, manchete em serifa, carimbo MITO/FATO ou numero, linhas de coluna
  poster  blocos de cor cheia (alternando), tipografia gigante, numero enorme de fundo, sem cartoes
  quiz    fundo escuro de listras diagonais continuas, alternativas A/B/C, resposta com check verde
Mesmas zonas seguras do make_carousel_fin.py (usa o mesmo FORMATS). Conteudo sempre centralizado na zona segura."""
import json, os, sys, math
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_carousel_fin as C
import themes as TH
INK = (24, 22, 28); CREAM = (246, 240, 226); GREEN = (46, 190, 120); RED = (214, 52, 52)

def lum(col): return 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
def on(col): return INK if lum(col) > 150 else (255, 255, 255)
def mix(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

class Ctx(C.Ctx):
    def __init__(s, name, font=None):
        super().__init__(name)
        if font: s.bold, s.reg = TH.FONTS[font]

def logo_badge(img, bg=(10, 12, 18), x=None):
    d = ImageDraw.Draw(img); lg = Image.open(C.LOGO).convert('RGBA'); h = C.LOGO_H - 20
    lg = lg.resize((int(lg.width * h / lg.height), h), Image.LANCZOS)
    x = C.MX if x is None else x
    d.rounded_rectangle([x - 16, C.LOGO_Y - 8, x + lg.width + 16, C.LOGO_Y + h + 18], 20, fill=bg + (255,))
    img.alpha_composite(lg, (x, C.LOGO_Y + 4))

def dots(img, c, i, n, col):
    d = ImageDraw.Draw(img)
    for k in range(n):
        cx = C.W // 2 + (k - (n - 1) / 2) * 30
        d.ellipse([cx - 7, C.DOTS_Y - 7, cx + 7, C.DOTS_Y + 7], fill=col if k == i else col + (70,) if len(col) == 3 else col)
    if i < n - 1:
        C.text(d, (C.W - C.MX - 44, C.ARROW_Y), 'arraste', c.R(28), col, 'rm', False)
        x, y = C.W - C.MX - 24, C.ARROW_Y
        d.line([x - 12, y - 11, x, y, x - 12, y + 11], fill=col, width=5, joint='curve')

# ---------------------------------------------------------------- JORNAL
def jornal_bg(c, n):
    W, H = C.W, C.H; WW = W * n
    img = Image.new('RGB', (WW, H), CREAM); d = ImageDraw.Draw(img)
    for x in range(0, WW, 4):                                   # leve textura de papel
        d.line([x, 0, x, H], fill=mix(CREAM, (230, 222, 204), 0.25 + 0.2 * math.sin(x / 37.0)), width=1)
    img = img.convert('RGBA'); ov = Image.new('RGBA', (WW, H), (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
    y0 = C.LOGO_Y + C.LOGO_H + 40
    o.rectangle([0, 0, WW, y0 - 26], fill=INK + (255,))          # faixa escura continua (abriga a logo)
    o.rectangle([0, y0 - 18, WW, y0 - 12], fill=c.a1 + (255,))
    for yy in (C.H - C.BOT + 10, C.H - C.BOT + 18): o.line([0, yy, WW, yy], fill=INK + (255,), width=2 if yy % 2 else 5)
    for k in range(1, n):                                          # filete de coluna nas emendas
        o.line([k * W, y0 + 20, k * W, C.H - C.BOT], fill=INK + (60,), width=2)
    return Image.alpha_composite(img, ov), y0

def jornal_chrome(img, c, i, n, handle, y0):
    d = ImageDraw.Draw(img); logo_badge(img, bg=INK)
    C.text(d, (C.W - C.MX, C.LOGO_Y + 70), 'EDIÇÃO ESPECIAL  •  Nº %02d' % (i + 1), c.B(28), (222, 218, 211), 'rm', False)
    C.text(d, (C.W // 2, C.HANDLE_Y or C.DOTS_Y + 50), handle, c.R(28), INK, 'mm', False) if C.HANDLE_Y else None
    dots(img, c, i, n, INK)

def jornal_slide(layer, c, s, i, n, ac):
    d = ImageDraw.Draw(layer); mw = C.W - 2 * C.MX; y = 300; t = s['type']
    if t == 'cover':
        if s.get('kicker'): C.text(d, (C.MX, y), s['kicker'].upper(), c.B(34), ac, 'la', False); y += 70
        sz, ls = C.fit(d, s['l1'], c.B, 84, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y, INK, int(sz * 1.16), )
        sz, ls = C.fit(d, s['hl'], c.B, 130, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y + 8, ac, int(sz * 1.1))
        d.line([C.MX, y + 24, C.MX + 220, y + 24], fill=INK, width=6)
        if s.get('sub'): sz, ls = C.fit(d, s['sub'], c.R, 42, mw, 3); C.block(d, ls, c.R(sz), C.MX, y + 54, (70, 66, 74), int(sz * 1.35))
    elif t == 'point':
        d.rounded_rectangle([C.MX, y, C.MX + d.textlength(s.get('tag', 'REPORTAGEM'), font=c.B(32)) + 52, y + 56], 8, fill=ac)
        C.text(d, (C.MX + 26, y + 28), s.get('tag', 'REPORTAGEM'), c.B(32), on(ac), 'lm', False); y += 100
        sz, ls = C.fit(d, s['title'], c.B, 76, mw, 4); y = C.block(d, ls, c.B(sz), C.MX, y, INK, int(sz * 1.14)) + 12
        d.line([C.MX, y, C.W - C.MX, y], fill=INK, width=3); y += 30
        for b in s.get('body', []):
            sz, ls = C.fit(d, b, c.R, 40, mw, 4); y = C.block(d, ls, c.R(sz), C.MX, y, (50, 46, 54), int(sz * 1.36)) + 22
    elif t == 'mito':
        d.rounded_rectangle([C.MX, y, C.MX + 210, y + 70], 10, outline=RED, width=6)
        C.text(d, (C.MX + 105, y + 36), 'MITO', c.B(46), RED, 'mm', False); y += 110
        sz, ls = C.fit(d, s['myth'], c.R, 54, mw, 3); y0 = y; y = C.block(d, ls, c.R(sz), C.MX, y, (110, 104, 112), int(sz * 1.3), )
        for k, l in enumerate(ls):                                    # risca a frase do mito
            yy = y0 + k * int(sz * 1.3) + int(sz * .55); d.line([C.MX - 6, yy, C.MX + d.textlength(l, font=c.R(sz)) + 6, yy], fill=RED, width=6)
        y += 40; d.rounded_rectangle([C.MX, y, C.MX + 210, y + 70], 10, fill=GREEN)
        C.text(d, (C.MX + 105, y + 36), 'FATO', c.B(46), (255, 255, 255), 'mm', False); y += 110
        sz, ls = C.fit(d, s['fact'], c.B, 58, mw, 4); y = C.block(d, ls, c.B(sz), C.MX, y, INK, int(sz * 1.25)) + 14
        if s.get('ref'): sz, ls = C.fit(d, s['ref'], c.R, 28, mw, 2, 22); C.block(d, ls, c.R(sz), C.MX, y, (90, 86, 94), int(sz * 1.3))
    elif t == 'list':
        sz, ls = C.fit(d, s['title'], c.B, 72, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y, INK, int(sz * 1.15)) + 14
        d.line([C.MX, y, C.W - C.MX, y], fill=INK, width=3); y += 30
        for k, it in enumerate(s['items']):
            sz, ls = C.fit(d, it, c.R, 42, mw - 90, 2); C.text(d, (C.MX, y), '%d.' % (k + 1), c.B(sz + 6), ac, 'la', False)
            y = C.block(d, ls, c.R(sz), C.MX + 80, y, INK, int(sz * 1.3)) + 24
    elif t == 'cta':
        sz, ls = C.fit(d, s['l1'], c.B, 74, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y, INK, int(sz * 1.16))
        sz, ls = C.fit(d, s['hl'], c.B, 108, mw, 2); y = C.block(d, ls, c.B(sz), C.MX, y + 6, ac, int(sz * 1.1)) + 18
        if s.get('sub'): sz, ls = C.fit(d, s['sub'], c.R, 40, mw, 3); y = C.block(d, ls, c.R(sz), C.MX, y, (60, 56, 64), int(sz * 1.35)) + 26
        d.rounded_rectangle([C.MX, y, C.W - C.MX, y + 150], 14, fill=INK)
        C.text(d, (C.W // 2, y + 46), 'Mande no direct a palavra', c.R(34), (222, 218, 211), 'mm', False)
        C.text(d, (C.W // 2, y + 105), s.get('kw', 'CONSULTORIA'), c.B(60), c.a1, 'mm', False); y += 186
        if s.get('disc'): sz, ls = C.fit(d, s['disc'], c.R, 26, mw, 4, 22); C.block(d, ls, c.R(sz), C.MX, y, (90, 86, 94), int(sz * 1.35))

# ---------------------------------------------------------------- POSTER
def poster_colors(c, i, n):
    cyc = [(c.a1, 'a1'), (c.bg0, 'bg'), (c.a2, 'a2'), (c.bg1, 'bg')]
    col, kind = cyc[i % 4]
    if i == 0: col, kind = c.a1, 'a1'
    if i == n - 1: col, kind = c.bg0, 'bg'
    return col, kind

def poster_slide(layer, c, s, i, n, bgc, kind):
    d = ImageDraw.Draw(layer); mw = C.W - 2 * C.MX; y = 300; t = s['type']
    fg = on(bgc); hi = c.a1 if kind == 'bg' else (INK if lum(bgc) > 150 else (255, 255, 255))
    if kind != 'bg': hi = on(bgc)
    if t == 'point' and s.get('n'):                                  # numero enorme de fundo
        d.text((C.W - C.MX + 40, C.H // 2 - 20), str(s['n']), font=c.B(900), fill=mix(bgc, fg, .13), anchor='rm')
    if t == 'cover':
        if s.get('kicker'): C.text(d, (C.MX, y), s['kicker'].upper(), c.B(34), fg, 'la', False); d.line([C.MX, y + 54, C.MX + 120, y + 54], fill=fg, width=6); y += 90
        sz, ls = C.fit(d, s['l1'].upper(), c.B, 92, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y, fg, int(sz * 1.06), )
        sz, ls = C.fit(d, s['hl'].upper(), c.B, 150, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y + 14, (255, 255, 255) if lum(bgc) < 150 else INK, int(sz * 1.02))
        if s.get('sub'): sz, ls = C.fit(d, s['sub'], c.R, 42, mw, 3); C.block(d, ls, c.R(sz), C.MX, y + 36, fg, int(sz * 1.35))
    elif t == 'point':
        C.text(d, (C.MX, y), s.get('tag', 'PONTO %s' % s.get('n', '')).upper(), c.B(36), c.a1 if kind == 'bg' else fg, 'la', False); y += 70
        sz, ls = C.fit(d, s['title'].upper(), c.B, 84, mw, 4); y = C.block(d, ls, c.B(sz), C.MX, y, fg, int(sz * 1.05)) + 30
        for b in s.get('body', []):
            sz, ls = C.fit(d, b, c.R, 42, mw - 40, 4); d.rectangle([C.MX, y + 6, C.MX + 10, y + 6 + len(ls) * int(sz * 1.35) - 12], fill=fg)
            y = C.block(d, ls, c.R(sz), C.MX + 34, y, fg, int(sz * 1.35)) + 26
    elif t == 'mito':
        C.text(d, (C.MX, y), 'DIZEM QUE', c.B(34), fg, 'la', False); y += 60
        sz, ls = C.fit(d, s['myth'], c.R, 52, mw, 3); y0 = y; y = C.block(d, ls, c.R(sz), C.MX, y, fg, int(sz * 1.3))
        for k, l in enumerate(ls):
            yy = y0 + k * int(sz * 1.3) + int(sz * .55); d.line([C.MX - 6, yy, C.MX + d.textlength(l, font=c.R(sz)) + 6, yy], fill=fg, width=7)
        y += 40; C.text(d, (C.MX, y), 'NA VERDADE', c.B(34), fg, 'la', False); y += 60
        sz, ls = C.fit(d, s['fact'].upper(), c.B, 64, mw, 4); y = C.block(d, ls, c.B(sz), C.MX, y, fg, int(sz * 1.1)) + 14
        if s.get('ref'): sz, ls = C.fit(d, s['ref'], c.R, 28, mw, 2, 22); C.block(d, ls, c.R(sz), C.MX, y, fg, int(sz * 1.3))
    elif t == 'list':
        sz, ls = C.fit(d, s['title'].upper(), c.B, 78, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y, fg, int(sz * 1.05)) + 30
        for k, it in enumerate(s['items']):
            sz, ls = C.fit(d, it, c.R, 42, mw - 100, 2); C.text(d, (C.MX, y - 6), '%02d' % (k + 1), c.B(sz + 18), c.a1 if kind == 'bg' else fg, 'la', False)
            y = C.block(d, ls, c.R(sz), C.MX + 110, y, fg, int(sz * 1.3)) + 28
    elif t == 'cta':
        sz, ls = C.fit(d, s['l1'].upper(), c.B, 72, mw, 3); y = C.block(d, ls, c.B(sz), C.MX, y, fg, int(sz * 1.06))
        sz, ls = C.fit(d, s['hl'].upper(), c.B, 112, mw, 2); y = C.block(d, ls, c.B(sz), C.MX, y + 6, c.a1, int(sz * 1.04)) + 24
        if s.get('sub'): sz, ls = C.fit(d, s['sub'], c.R, 40, mw, 3); y = C.block(d, ls, c.R(sz), C.MX, y, fg, int(sz * 1.35)) + 26
        d.rectangle([C.MX, y, C.W - C.MX, y + 150], fill=c.a1)
        C.text(d, (C.W // 2, y + 46), 'MANDE NO DIRECT A PALAVRA', c.B(30), on(c.a1), 'mm', False)
        C.text(d, (C.W // 2, y + 106), s.get('kw', 'CONSULTORIA'), c.B(60), on(c.a1), 'mm', False); y += 186
        if s.get('disc'): sz, ls = C.fit(d, s['disc'], c.R, 26, mw, 4, 22); C.block(d, ls, c.R(sz), C.MX, y, fg, int(sz * 1.35))

# ---------------------------------------------------------------- QUIZ
def quiz_bg(c, n):
    W, H = C.W, C.H; WW = W * n
    img = Image.new('RGB', (WW, H), c.bg0).convert('RGBA'); ov = Image.new('RGBA', (WW, H), (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
    for x in range(-H, WW + H, 150):                                # listras diagonais continuas
        o.polygon([(x, H), (x + 70, H), (x + 70 + H * .6, 0), (x + H * .6, 0)], fill=mix(c.bg0, c.a2, .10) + (255,))
    ov2 = Image.new('RGBA', (WW, H), (0, 0, 0, 0)); g = ImageDraw.Draw(ov2)
    for k in range(n + 1): g.ellipse([k * W - 300, H // 2 - 300, k * W + 300, H // 2 + 300], fill=c.a1 + (26,))
    img = Image.alpha_composite(img, ov); return Image.alpha_composite(img, ov2.filter(ImageFilter.GaussianBlur(100)))

def quiz_slide(layer, c, s, i, n):
    d = ImageDraw.Draw(layer); mw = C.W - 2 * C.MX; y = 300; t = s['type']
    if t == 'q':
        ans = s.get('answer'); reveal = s.get('reveal', False)
        d.rounded_rectangle([C.MX, y, C.MX + 250, y + 62], 31, fill=c.a1)
        C.text(d, (C.MX + 125, y + 32), 'QUIZ %s' % s.get('num', ''), c.B(32), c.bg0, 'mm', False); y += 100
        sz, ls = C.fit(d, s['question'], c.B, 62, mw, 4); y = C.block(d, ls, c.B(sz), C.MX, y, (255, 255, 255), int(sz * 1.2)) + 26
        for k, o in enumerate(s['options']):
            ok = reveal and k == ans; dim = reveal and k != ans
            sz, ls = C.fit(d, o, c.R, 40, mw - 150, 2); hh = max(104, len(ls) * int(sz * 1.3) + 40)
            fill = (46, 190, 120, 235) if ok else (255, 255, 255, 18 if dim else 36)
            d.rounded_rectangle([C.MX, y, C.W - C.MX, y + hh], 26, fill=fill, outline=(c.a1 if not reveal else (46, 190, 120)) + (255,) if not dim else None, width=3)
            d.ellipse([C.MX + 24, y + hh // 2 - 31, C.MX + 86, y + hh // 2 + 31], fill=(c.bg0 if ok else c.a1))
            C.text(d, (C.MX + 55, y + hh // 2 + 2), 'ABC'[k], c.B(36), (255, 255, 255) if ok else c.bg0, 'mm', False)
            C.block(d, ls, c.R(sz), C.MX + 114, y + (hh - len(ls) * int(sz * 1.3)) // 2 + 2, (10, 40, 24) if ok else ((150, 160, 180) if dim else (255, 255, 255)), int(sz * 1.3)); y += hh + 20
        if reveal and s.get('why'):
            sz, ls = C.fit(d, s['why'], c.R, 34, mw, 4, 26); y += 8; C.block(d, ls, c.R(sz), C.MX, y, (226, 232, 246), int(sz * 1.35))
        elif not reveal: C.text(d, (C.MX, y + 10), 'Qual é a certa? Arraste para ver.', c.R(32), c.a1, 'la', False)
    else:
        C.KINDS[t](layer, c, s, i, n, '')

# ---------------------------------------------------------------- BUILD
def build(spec_path, outdir, fmt='ig'):
    C.use_format(fmt); spec = json.load(open(spec_path)); os.makedirs(outdir, exist_ok=True)
    c = Ctx(spec.get('theme', 'royal'), spec.get('font')); est = spec.get('estilo', 'jornal')
    handle = spec.get('handle', '@realstart.consultantofc'); sl = spec['slides']; n = len(sl); outs = []
    if est == 'jornal': wide, y0 = jornal_bg(c, n)
    elif est == 'quiz': wide = quiz_bg(c, n)
    for i, s in enumerate(sl):
        if est == 'poster':
            bgc, kind = poster_colors(c, i, n); img = Image.new('RGBA', (C.W, C.H), bgc + (255,))
            d = ImageDraw.Draw(img); d.rectangle([0, 0, C.W, 10], fill=on(bgc))
            logo_badge(img, bg=(10, 12, 18)); dots(img, c, i, n, on(bgc))
            if C.HANDLE_Y: C.text(d, (C.W // 2, C.HANDLE_Y), handle, c.R(30), on(bgc), 'mm', False)
        else:
            img = wide.crop((i * C.W, 0, (i + 1) * C.W, C.H))
            if est == 'jornal': jornal_chrome(img, c, i, n, handle, y0)
            else:
                C.chrome(img, c, i, n, handle)
        layer = Image.new('RGBA', (C.W, C.H), (0, 0, 0, 0))
        if est == 'jornal': jornal_slide(layer, c, s, i, n, mix(c.a1, INK, .35) if lum(c.a1) > 150 else c.a1)
        elif est == 'poster': poster_slide(layer, c, s, i, n, bgc, kind)
        else: quiz_slide(layer, c, s, i, n)
        bb = layer.getbbox()
        if bb:
            top, bot = C.TOP, C.H - C.BOT; dy = int((top + bot) / 2 - (bb[1] + bb[3]) / 2)
            if bb[1] + dy < top: dy = top - bb[1]
            if bb[3] + dy > bot: print('AVISO: slide %d passa da zona segura em %d px' % (i + 1, bb[3] + dy - bot))
            layer = layer.transform(layer.size, Image.AFFINE, (1, 0, 0, 0, 1, -dy))
        img = Image.alpha_composite(img, layer)
        p = os.path.join(outdir, 'slide_%02d.jpg' % (i + 1)); img.convert('RGB').save(p, quality=92, subsampling=0); outs.append(p)
    return outs

if __name__ == '__main__':
    fmt = sys.argv[3] if len(sys.argv) > 3 else 'ig'
    if fmt == 'both':
        for p in build(sys.argv[1], sys.argv[2], 'ig'): print(p)
        for p in build(sys.argv[1], os.path.join(sys.argv[2], 'tiktok'), 'tiktok'): print(p)
    else:
        for p in build(sys.argv[1], sys.argv[2], fmt): print(p)
