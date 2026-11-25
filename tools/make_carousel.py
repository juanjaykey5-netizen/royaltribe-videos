"""Gerador de carrossel (Instagram 1080x1350, 4:5) - Aljava GC. Uso: python3 tools/make_carousel.py spec.json outdir
spec: {"theme": "<tema de themes.py>", "brand": {"logo": "brand/aljava_transparente.png", "handle": "@aljava.gc.ofc"},
 "slides": [ {type: capa|texto|versus|verso|convite|cta, ...} ]}
Identidade fixa em todos os slides: logo no topo, moldura dourada dupla, chip de rotulo, contador N/total e @ embaixo.
Varia por dia: tema (cores+fonte) e desenho fofinho (art.py).
ZONA SEGURA: conteudo entre x=120..960 e y=200..1150 (o grid do perfil corta as laterais para 3:4 = x 34..1046; topo/base livres de UI)."""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import themes, art as ART
W, H = 1080, 1350
X0, X1, Y0, Y1 = 120, 960, 200, 1150
WHITE = (245, 242, 236)
SHADOW = (0, 0, 0)  # sombra sutil (2 px)

def font(path, size):
    return ImageFont.truetype(path, size)

class Ctx:
    def __init__(s, spec):
        th = themes.THEMES[spec.get('theme', 'lavanda')]; s.th = th
        s.bold, s.med = themes.FONTS[spec['font'] if spec.get('font') in themes.FONTS else th['font']]  # "font": sobrescreve a fonte do tema (seletor)
        s.bg0, s.bg1, s.a1, s.a2 = th['bg0'], th['bg1'], th['a1'], th['a2']
        br = spec.get('brand', {}); s.logo = Image.open(os.path.join(HERE, '..', br.get('logo', 'brand/aljava_transparente.png'))).convert('RGBA')
        s.handle = br.get('handle', '@aljava.gc.ofc'); s.n = len(spec['slides'])

def background(c):
    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1); d.line([(0, y), (W, y)], fill=tuple(int(c.bg0[i] + (c.bg1[i] - c.bg0[i]) * t) for i in range(3)))
    bl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bl)
    for (x, y, r, col, a) in [(160, 260, 260, c.a2, 34), (930, 520, 300, c.a1, 26), (260, 1100, 320, c.bg1, 120), (900, 1230, 200, c.a2, 30)]:
        bd.ellipse([x - r, y - r, x + r, y + r], fill=tuple(col[:3]) + (a,))
    bl = bl.filter(ImageFilter.GaussianBlur(70)); img = Image.alpha_composite(img.convert('RGBA'), bl)
    return img

def over(img, draw_fn):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(lay)); img.alpha_composite(lay)

def wide_background(c, n):
    """Fundo panoramico (n*W x H): os slides sao fatias dele, entao linha, brilhos e desenhos atravessam as emendas."""
    import math
    WW = W * n; img = Image.new('RGB', (WW, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1); d.line([(0, y), (WW, y)], fill=tuple(int(c.bg0[i] + (c.bg1[i] - c.bg0[i]) * t) for i in range(3)))
    bl = Image.new('RGBA', (WW, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bl)
    for k in range(n * 2):
        x = int(W * (k + 0.5) / 2 * 1.0 + (k % 3) * 40); y = [260, 980, 560, 1180, 380, 820][k % 6]; r = [260, 300, 220, 320, 240, 280][k % 6]
        col = [c.a2, c.a1, c.bg1, c.a2][k % 4]; a = [34, 26, 120, 30][k % 4]
        bd.ellipse([x - r, y - r, x + r, y + r], fill=tuple(col[:3]) + (a,))
    bl = bl.filter(ImageFilter.GaussianBlur(70)); img = Image.alpha_composite(img.convert('RGBA'), bl); d = ImageDraw.Draw(img)
    # linhas douradas continuas no topo e na base
    d.line([(0, 44), (WW, 44)], fill=c.a1 + (255,), width=4); d.line([(0, 60), (WW, 60)], fill=c.a1 + (110,), width=2)
    d.line([(0, H - 44), (WW, H - 44)], fill=c.a1 + (255,), width=4); d.line([(0, H - 60), (WW, H - 60)], fill=c.a1 + (110,), width=2)
    # fio ondulado que atravessa todos os slides (y ~ 1185)
    pts = [(x, 1186 + 14 * math.sin(x / 150.0)) for x in range(0, WW + 1, 6)]
    d.line(pts, fill=c.a1 + (200,), width=4, joint='curve')
    for k in range(0, n * 6):
        x = int(WW * (k + 0.5) / (n * 6)); y = 1186 + 14 * math.sin(x / 150.0); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=c.a2 + (255,))
    return img

def seam_art(img, c, n, kinds):
    for k in range(1, n):
        kind = kinds[(k - 1) % len(kinds)]; sz = 210; im = ART.draw(kind, sz)
        img.alpha_composite(im, (int(W * k - sz / 2), int(1186 - sz / 2 - 6)))

def frame(img, c):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([44, 44, W - 44, H - 44], 44, outline=c.a1 + (255,), width=4)
    over(img, lambda dd: dd.rounded_rectangle([60, 60, W - 60, H - 60], 34, outline=c.a1 + (110,), width=2))

def wrap(txt, f, maxw):
    words, lines, cur = txt.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if f.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fit(txt, path, maxw, maxh, smax, smin, lh=1.22):
    for s in range(smax, smin - 1, -2):
        f = font(path, s); ls = wrap(txt, f, maxw)
        if len(ls) * s * lh <= maxh and all(f.getlength(l) <= maxw for l in ls): return f, ls, s
    f = font(path, smin); return f, wrap(txt, f, maxw), smin

def text_block(d, txt, path, x, y, maxw, maxh, smax, smin, fill, align='left', lh=1.22, shadow=True):
    f, ls, s = fit(txt, path, maxw, maxh, smax, smin, lh); yy = y
    for l in ls:
        w = f.getlength(l); xx = x if align == 'left' else x + (maxw - w) / 2
        if shadow: d.text((xx + 2, yy + 3), l, font=f, fill=SHADOW)
        d.text((xx, yy), l, font=f, fill=fill); yy += s * lh
    return yy

def chip(img, c, text, x, y, alert=False):
    d = ImageDraw.Draw(img); f = font(c.bold, 34); tw = f.getlength(text); pad = 28
    h = 64; icon = 44 if alert else 0
    bw = tw + pad * 2 + (icon + 12 if alert else 0)
    d.rounded_rectangle([x, y, x + bw, y + h], 32, fill=(255, 196, 64, 255) if alert else c.a1 + (255,))
    tx = x + pad
    if alert:
        cx, cy = x + pad + 20, y + h / 2
        d.polygon([(cx, cy - 20), (cx + 22, cy + 17), (cx - 22, cy + 17)], fill=(60, 30, 20, 255))
        g = font(c.bold, 26); d.text((cx - g.getlength('!') / 2, cy - 14), '!', font=g, fill=(255, 196, 64, 255)); tx += icon + 12
    d.text((tx, y + h / 2 - 20), text, font=f, fill=(40, 24, 16, 255))
    return bw

def logo_top(img, c, h=118):
    lg = c.logo.resize((int(c.logo.width * h / c.logo.height), h), Image.LANCZOS)
    img.alpha_composite(lg, ((W - lg.width) // 2, 78))

def footer(img, c, i):
    d = ImageDraw.Draw(img); f = font(c.med, 28)
    d.text((100, H - 112), f'{i}/{c.n}', font=f, fill=WHITE + (200,))
    hw = f.getlength(c.handle); d.text((W - 100 - hw, H - 112), c.handle, font=f, fill=c.a1 + (255,))

def art_at(img, kind, cx, cy, size):
    im = ART.draw(kind, size); img.alpha_composite(im, (int(cx - size / 2), int(cy - size / 2)))

def slide(c, s, i, bg=None):
    if bg is None: img = background(c); frame(img, c)
    else: img = bg
    d = ImageDraw.Draw(img); t = s['type']
    if t == 'capa':
        logo_top(img, c, 150)
        chip(img, c, s.get('chip', 'ALERTA BÍBLICO'), X0, 290, alert=True)
        y = text_block(d, s['title'], c.bold, X0, 385, X1 - X0, 400, 104, 64, WHITE, lh=1.12)
        text_block(d, s['sub'], c.med, X0, y + 16, X1 - X0, 180, 44, 30, c.a2 + (255,))
        art_at(img, s.get('art', 'estrela'), 540, 1000, 280)
        f = font(c.bold, 32); d.text((X1 - f.getlength('ARRASTE') - 56, 1086), 'ARRASTE', font=f, fill=c.a1 + (255,))
        d.line([(X1 - 44, 1104), (X1, 1104)], fill=c.a1 + (255,), width=6); d.polygon([(X1 + 2, 1104), (X1 - 14, 1092), (X1 - 14, 1116)], fill=c.a1 + (255,))
    else:
        logo_top(img, c, 104)
        if t == 'texto':
            chip(img, c, s.get('label', 'CONTEXTO'), X0, 230, alert=s.get('alert', False))
            y = text_block(d, s['title'], c.bold, X0, 330, X1 - X0, 300, 88, 52, c.a1 + (255,), lh=1.12)
            lim = 940 if s.get('art') else 1060
            y = text_block(d, s['body'], c.med, X0, y + 30, X1 - X0, lim - y - 30, 56, 34, WHITE, lh=1.32)
            if s.get('source'):
                text_block(d, 'Fonte: ' + s['source'], c.med, X0, 1090, X1 - X0, 60, 26, 20, WHITE[:3] + (190,), shadow=False)
            if s.get('art'): art_at(img, s['art'], 850, 1030, 200)
        elif t == 'versus':
            chip(img, c, s.get('label', 'MITO x TEXTO'), X0, 230)
            for k, (lab, txt, col) in enumerate([(s['a_label'], s['a_text'], (255, 120, 120)), (s['b_label'], s['b_text'], (140, 225, 160))]):
                y0 = 330 + k * 400
                over(img, lambda dd, y0=y0: dd.rounded_rectangle([X0, y0, X1, y0 + 360], 36, fill=(0, 0, 0, 80)))
                d = ImageDraw.Draw(img); d.rounded_rectangle([X0, y0, X1, y0 + 360], 36, outline=col + (255,), width=4)
                d.text((X0 + 36, y0 + 28), lab, font=font(c.bold, 34), fill=col + (255,))
                text_block(d, txt, c.bold if k else c.med, X0 + 36, y0 + 92, X1 - X0 - 72, 240, 56, 34, WHITE, lh=1.22)
        elif t == 'verso':
            chip(img, c, s.get('label', 'O QUE O TEXTO DIZ'), X0, 230)
            d.text((X0, 300), '“', font=font(c.bold, 220), fill=c.a1 + (255,))
            y = text_block(d, s['text'], c.med, X0, 470, X1 - X0, 470, 62, 36, WHITE, lh=1.3)
            f = font(c.bold, 44); d.text((X0, y + 30), s['ref'], font=f, fill=c.a1 + (255,))
            f2 = font(c.med, 28); d.text((X0, y + 92), s.get('foot', 'Almeida Revista e Corrigida'), font=f2, fill=WHITE[:3] + (200,))
            if s.get('art'): art_at(img, s['art'], 860, 1040, 190)
        elif t == 'convite':
            chip(img, c, 'ESTUDE COM A GENTE', X0, 230)
            y = text_block(d, s['title'], c.bold, X0, 330, X1 - X0, 280, 78, 50, c.a1 + (255,), lh=1.12)
            yy = y + 30
            for b in s['bullets']:
                d.ellipse([X0, yy + 6, X0 + 52, yy + 58], fill=c.a1 + (255,)); d.line([(X0 + 14, yy + 33), (X0 + 24, yy + 44), (X0 + 40, yy + 20)], fill=(40, 24, 16, 255), width=7)
                yy = text_block(d, b, c.med, X0 + 76, yy, X1 - X0 - 76, 140, 42, 30, WHITE, lh=1.22) + 22
            d.rounded_rectangle([X0, 1010, X1, 1110], 50, fill=c.a1 + (255,))
            bf = font(c.bold, 40); bt = s.get('button', 'Chame no direct: ESTUDAR'); d.text((X0 + (X1 - X0 - bf.getlength(bt)) / 2, 1034), bt, font=bf, fill=(40, 24, 16, 255))
        elif t == 'cta':
            lg = c.logo.resize((int(c.logo.width * 360 / c.logo.height), 360), Image.LANCZOS); img.alpha_composite(lg, ((W - lg.width) // 2, 230))
            y = text_block(d, s['title'], c.bold, X0, 640, X1 - X0, 160, 70, 46, c.a1 + (255,), align='center', lh=1.12)
            y = text_block(d, s['sub'], c.med, X0, y + 20, X1 - X0, 200, 42, 30, WHITE, align='center', lh=1.25)
            text_block(d, s.get('aviso', 'Reflexão cristã e educativa. Não substitui a sua igreja local.'), c.med, X0, 1050, X1 - X0, 90, 28, 22, WHITE[:3] + (200,), align='center', shadow=False)
            art_at(img, s.get('art', 'coracao'), 850, 420, 160)
    footer(img, c, i)
    return img.convert('RGB')

def photo_bg(bg, path, tint=0.42, fade=130):
    """Cola uma ilustracao (IA, 2:3) como fundo do slide: cobre 1080x1350, escurece com a cor do tema (texto legivel)
    e dissolve as bordas esquerda/direita para o fundo continuo do carrossel."""
    path = path if os.path.isabs(path) else os.path.join(HERE, '..', path)
    im = Image.open(path).convert('RGB'); sc = W / im.width
    im = im.resize((W, int(im.height * sc)), Image.LANCZOS); y0 = max(0, int((im.height - H) * 0.42)); im = im.crop((0, y0, W, y0 + H))
    shade = Image.new('RGB', (W, H), tuple(bg.getpixel((W // 2, H // 2))[:3]))
    a = Image.new('L', (1, H))
    for y in range(H): a.putpixel((0, y), int(255 * min(1, tint + 0.22 * (1 - abs(y / H - 0.5) * 2))))
    im = Image.composite(shade, im, a.resize((W, H)))
    m = Image.new('L', (W, 1))
    for x in range(W): m.putpixel((x, 0), int(255 * min(1, x / fade, (W - 1 - x) / fade)))
    out = bg.copy(); out.paste(im, (0, 0), m.resize((W, H))); return out

def build(spec_path, outdir):
    spec = json.load(open(spec_path)); os.makedirs(outdir, exist_ok=True); c = Ctx(spec); n = c.n
    imgs = spec.get('imagens') or []
    pos = {}
    if imgs: pos = {max(1, min(n, round(1 + k * (n - 1) / max(1, len(imgs) - 1)))): im for k, im in enumerate(imgs)} if len(imgs) > 1 else {1: imgs[0]}
    if spec.get('continuo', True):  # carrossel continuo (panoramico)
        wide = wide_background(c, n); seam_art(wide, c, n, spec.get('seam_art', ['estrela', 'nuvem', 'ovelha', 'pomba', 'sol', 'coracao', 'arca']))
        for i, s in enumerate(spec['slides'], 1):
            bg = wide.crop((W * (i - 1), 0, W * i, H)).copy()
            if i in pos: bg = photo_bg(bg, pos[i], spec.get('foto_tint', 0.42))
            slide(c, s, i, bg=bg).save(os.path.join(outdir, f'slide_{i:02d}.png'), optimize=True)
        wide.convert('RGB').resize((W * n // 4, H // 4)).save(os.path.join(outdir, 'panorama_previa.png'))
    else:
        for i, s in enumerate(spec['slides'], 1):
            slide(c, s, i).save(os.path.join(outdir, f'slide_{i:02d}.png'), optimize=True)
    print('ok', n, 'slides')

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
