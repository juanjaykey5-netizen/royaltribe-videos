import sys, math, subprocess, os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FD = '/usr/share/fonts/truetype/google-fonts/'
HERE = os.path.dirname(os.path.abspath(__file__))
FONTMAP = {}  # 'Poppins-Bold'/'Poppins-Medium' -> caminho do tema
BG0 = (8, 20, 48); BG1 = (20, 44, 98)
BLOBS = [(40, 80, 160, 70), (24, 194, 156, 38), (245, 183, 0, 30), (60, 100, 190, 60)]
GOLD = (245, 183, 0)
TEAL = (24, 194, 156)
WHITE = (255, 255, 255)
MUTED = (170, 186, 214)
RED = (255, 110, 110)
DARK = (8, 20, 48)

OLD_DURS = [4.5, 7.5, 7.0, 10.6, 7.8, 5.0]   # tempos em que as animacoes das cenas foram desenhadas
DURS = list(OLD_DURS)
_tj = os.environ.get('TIMING_JSON', os.path.join(HERE, 'timing.json'))
if os.path.exists(_tj):
    import json as _json
    DURS = _json.load(open(_tj))['durs']
SPEED = [o / d for o, d in zip(OLD_DURS, DURS)]  # acelera a animacao junto com a cena mais curta
STARTS = [sum(DURS[:i]) for i in range(len(DURS))]
TOTAL = sum(DURS)

G = 1.0  # global alpha for the scene fade


@lru_cache(maxsize=None)
def F(name, size):
    path = FONTMAP.get(name) or (FD + name + '.ttf')
    return ImageFont.truetype(path, int(size))


def cl(x): return max(0.0, min(1.0, x))
def eo3(x): x = cl(x); return 1 - (1 - x) ** 3
def eob(x):
    c1 = 1.70158; c3 = c1 + 1; x = cl(x)
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def pr(t, t0, d): return cl((t - t0) / d)


@lru_cache(maxsize=1)
def bg_base():
    im = Image.new('RGB', (270, 480))
    d = ImageDraw.Draw(im)
    for y in range(480):
        k = y / 479
        c = tuple(int(BG0[i] * (1 - k) + BG1[i] * k) for i in range(3))
        d.line([(0, y), (270, y)], fill=c)
    return im


def background(tg):
    im = bg_base().copy().convert('RGBA')
    ov = Image.new('RGBA', (270, 480), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    specs = [(60, 90, 70, 0.0, BLOBS[0]), (210, 190, 90, 1.7, BLOBS[1]),
             (90, 330, 80, 3.1, BLOBS[2]), (220, 430, 60, 4.4, BLOBS[3])]
    for (x, y, r, ph, col) in specs:
        cx = x + 18 * math.sin(tg * 0.5 + ph)
        cy = y + 22 * math.cos(tg * 0.4 + ph)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    ov = ov.filter(ImageFilter.GaussianBlur(14))
    im = Image.alpha_composite(im, ov).convert('RGB')
    return im.resize((W, H), Image.BILINEAR)



def _over(img, layer, pos):
    """Alpha-composite RGBA layer onto RGBA/RGB img at pos, clipped to the canvas."""
    x, y = int(pos[0]), int(pos[1])
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(img.width, x + layer.width), min(img.height, y + layer.height)
    if x1 <= x0 or y1 <= y0:
        return
    part = layer.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    box = (x0, y0, x1, y1)
    base = img.crop(box).convert('RGBA')
    img.paste(Image.alpha_composite(base, part).convert(img.mode), (x0, y0))


def T(img, txt, x, y, size, fill=WHITE, a=1.0, font='Poppins-Bold', anchor='mm', scale=1.0, shadow=True):
    a = a * G
    if a <= 0.01 or scale <= 0.01:
        return
    f = F(font, size * scale)
    bb = f.getbbox(txt, anchor=anchor)
    pad = 16
    lw, lh = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    ox, oy = pad - bb[0], pad - bb[1]
    layer = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if shadow:
        d.text((ox + 3, oy + 5), txt, font=f, anchor=anchor, fill=(0, 0, 0, int(110 * a)))
    d.text((ox, oy), txt, font=f, anchor=anchor, fill=tuple(fill) + (int(255 * a),))
    _over(img, layer, (int(x - ox), int(y - oy)))


def RR(img, box, r, fill, a=1.0, outline=None, width=0):
    a = a * G
    if a <= 0.01:
        return
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = 6
    layer = Image.new('RGBA', (x1 - x0 + pad * 2, y1 - y0 + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = None if fill is None else tuple(fill[:3]) + (int((fill[3] if len(fill) > 3 else 255) * a),)
    o = None if outline is None else tuple(outline[:3]) + (int(255 * a),)
    d.rounded_rectangle([pad, pad, pad + x1 - x0, pad + y1 - y0], radius=r, fill=f, outline=o, width=width)
    _over(img, layer, (x0 - pad, y0 - pad))


def circle(img, cx, cy, r, fill, a=1.0, outline=None, width=0):
    a = a * G
    if a <= 0.01 or r <= 0:
        return
    pad = 6
    s = int(r * 2 + pad * 2)
    layer = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = None if fill is None else tuple(fill[:3]) + (int(255 * a),)
    o = None if outline is None else tuple(outline[:3]) + (int(255 * a),)
    d.ellipse([pad, pad, pad + 2 * r, pad + 2 * r], fill=f, outline=o, width=width)
    _over(img, layer, (int(cx - r - pad), int(cy - r - pad)))


LOGO_PATH = os.path.join(HERE, '..', 'brand', 'royal_signature_transparente.png')
LIGHT = (230, 231, 232)


@lru_cache(maxsize=None)
def _logo(h):
    lg = Image.open(LOGO_PATH).convert('RGBA')
    return lg.resize((int(lg.width * h / lg.height), h), Image.LANCZOS)


def logo(img, x, top, h, a=1.0, center=False):
    a = a * G
    if a <= 0.01:
        return _logo(int(h)).width
    lg = _logo(int(h))
    if a < 0.999:
        al = lg.getchannel('A').point(lambda v: int(v * a))
        lg = lg.copy(); lg.putalpha(al)
    px = int(x - lg.width / 2) if center else int(x)
    _over(img, lg, (px, int(top)))
    return lg.width


def check(img, cx, cy, size, p, color=DARK, w=10):
    # animated check mark, p in 0..1
    pts = [(cx - size * 0.5, cy), (cx - size * 0.12, cy + size * 0.4), (cx + size * 0.5, cy - size * 0.38)]
    d = ImageDraw.Draw(img)
    seg1 = cl(p / 0.4)
    seg2 = cl((p - 0.4) / 0.6)
    if seg1 > 0:
        e = (pts[0][0] + (pts[1][0] - pts[0][0]) * seg1, pts[0][1] + (pts[1][1] - pts[0][1]) * seg1)
        d.line([pts[0], e], fill=color, width=w, joint='curve')
    if seg2 > 0:
        e = (pts[1][0] + (pts[2][0] - pts[1][0]) * seg2, pts[1][1] + (pts[2][1] - pts[1][1]) * seg2)
        d.line([pts[1], e], fill=color, width=w, joint='curve')


# ---------------- scenes ----------------

def scene1(img, t):
    d = DURS[0]
    la = eo3(pr(t, 0.0, 0.4))
    lw = logo(img, 60, 245, 92, a=la)
    T(img, 'ROYAL SIGNATURE', 60 + lw + 20, 291, 32, LIGHT, a=0.95 * la, anchor='lm', font='Poppins-Bold')
    T(img, 'Chegou nos EUA', W / 2, 440, 86, WHITE, a=eo3(pr(t, 0.1, 0.4)))
    T(img, 'e o seu crédito é', W / 2, 550, 86, WHITE, a=eo3(pr(t, 0.4, 0.4)))
    s = eob(pr(t, 0.9, 0.55))
    T(img, 'ZERO?', W / 2, 730, 210, GOLD, a=cl(pr(t, 0.9, 0.2)), scale=max(0.01, s))
    # card
    slide = eo3(pr(t, 1.5, 0.7))
    cy = 1170 + (1 - slide) * 700 + 14 * math.sin(t * 2.2)
    ang = -8 + 3 * math.sin(t * 1.6)
    cw, ch = 720, 450
    layer = Image.new('RGBA', (cw + 40, ch + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([24, 28, 24 + cw, 28 + ch], radius=38, fill=(0, 0, 0, 90))
    ld.rounded_rectangle([20, 20, 20 + cw, 20 + ch], radius=38, fill=GOLD + (255,))
    ld.rounded_rectangle([20, 20, 20 + cw, 20 + 120], radius=38, fill=(212, 154, 0, 255))
    ld.rectangle([20, 90, 20 + cw, 140], fill=(212, 154, 0, 255))
    ld.rounded_rectangle([70, 190, 190, 270], radius=14, fill=(255, 225, 130, 255), outline=(180, 120, 0, 255), width=3)
    ld.text((70, 340), 'SCORE', font=F('Poppins-Bold', 40), fill=DARK + (255,))
    ld.text((70, 380), '???', font=F('Poppins-Bold', 78), fill=DARK + (255,))
    ld.text((20 + cw - 50, 420 - 20), 'sem histórico', font=F('Poppins-Medium', 32), fill=(120, 80, 0, 255), anchor='rm')
    layer = layer.rotate(ang, resample=Image.BICUBIC, expand=True)
    al = layer.getchannel('A').point(lambda v: int(v * G * cl(pr(t, 1.5, 0.3))))
    layer.putalpha(al)
    _over(img, layer, (int(W / 2 - layer.width / 2), int(cy - layer.height / 2)))
    T(img, 'Histórico de crédito de outro país', W / 2, 1520, 42, MUTED, a=eo3(pr(t, 2.8, 0.5)), font='Poppins-Medium')
    T(img, 'geralmente não vale aqui', W / 2, 1572, 42, MUTED, a=eo3(pr(t, 3.0, 0.5)), font='Poppins-Medium')


def scene2(img, t):
    T(img, 'Seu score tem', W / 2, 300, 76, WHITE, a=eo3(pr(t, 0.1, 0.4)))
    T(img, '5 pilares', W / 2, 400, 100, GOLD, a=eo3(pr(t, 0.3, 0.4)))
    items = [('Pagar em dia', 35, GOLD), ('Quanto você deve', 30, GOLD), ('Tempo de histórico', 15, TEAL),
             ('Crédito novo', 10, TEAL), ('Mix de crédito', 10, TEAL)]
    y0, gap = 600, 165
    for i, (lab, pct, col) in enumerate(items):
        t0 = 0.9 + 0.75 * i
        y = y0 + i * gap
        a = eo3(pr(t, t0, 0.35))
        T(img, lab, 100, y, 44, WHITE, a=a, anchor='lm', font='Poppins-Bold')
        p = eo3(pr(t, t0 + 0.1, 0.7))
        T(img, f'{int(round(pct * p))}%', 980, y, 52, col, a=a, anchor='rm')
        RR(img, (100, y + 40, 980, y + 82), 21, (255, 255, 255, 40), a=a)
        wfill = 880 * (pct / 40.0) * p
        if wfill > 8:
            RR(img, (100, y + 40, 100 + wfill, y + 82), 21, col + (255,), a=a)
    T(img, 'Pesos aproximados do FICO  |  Fonte: myFICO', W / 2, 1450, 36, MUTED, a=eo3(pr(t, 5.0, 0.5)), font='Poppins-Medium')


def scene3(img, t):
    T(img, 'Os 2 que mais pesam', W / 2, 290, 72, WHITE, a=eo3(pr(t, 0.1, 0.4)))
    # block A
    a = eo3(pr(t, 0.6, 0.4))
    p = eo3(pr(t, 0.6, 0.8))
    T(img, f'{int(round(35 * p))}%', 80, 560, 190, GOLD, a=a, anchor='lm')
    T(img, 'Pagar', 560, 520, 62, WHITE, a=a, anchor='lm')
    T(img, 'em dia', 560, 600, 62, WHITE, a=a, anchor='lm')
    for i in range(6):
        ti = 1.4 + 0.35 * i
        cx = 150 + i * 150
        circle(img, cx, 770, 42, None, a=eo3(pr(t, 1.2, 0.3)), outline=(255, 255, 255), width=4)
        if t > ti:
            circle(img, cx, 770, 42, TEAL, a=1.0)
            check(img, cx, 770, 40, pr(t, ti, 0.25), w=8)
    T(img, 'mês pago em dia', W / 2, 860, 40, MUTED, a=eo3(pr(t, 3.4, 0.4)), font='Poppins-Medium')
    # block B
    b = eo3(pr(t, 3.2, 0.4))
    pb = eo3(pr(t, 3.2, 0.8))
    T(img, f'{int(round(30 * pb))}%', 80, 1040, 190, GOLD, a=b, anchor='lm')
    T(img, 'Usar pouco', 560, 1000, 62, WHITE, a=b, anchor='lm')
    T(img, 'do limite', 560, 1080, 62, WHITE, a=b, anchor='lm')
    gy = 1260
    RR(img, (100, gy, 980, gy + 60), 30, (255, 255, 255, 40), a=b)
    fw = 880 * 0.22 * eo3(pr(t, 4.0, 0.9))
    if fw > 8:
        RR(img, (100, gy, 100 + fw, gy + 60), 30, TEAL + (255,), a=b)
    mx = 100 + 880 * 0.30
    d = ImageDraw.Draw(img)
    if b * G > 0.5:
        d.line([(mx, gy - 14), (mx, gy + 74)], fill=GOLD, width=6)
    T(img, 'limite 30%', mx, gy - 40, 38, GOLD, a=b, font='Poppins-Bold')
    T(img, 'ex.: 22% do limite usado', 100, gy + 110, 40, TEAL, a=eo3(pr(t, 4.6, 0.4)), anchor='lm', font='Poppins-Bold')
    T(img, 'Meta: ficar abaixo de 30% (CFPB)', W / 2, 1500, 42, WHITE, a=eo3(pr(t, 5.4, 0.5)), font='Poppins-Medium')


def scene4(img, t):
    T(img, '3 jeitos de começar', W / 2, 270, 70, WHITE, a=eo3(pr(t, 0.1, 0.4)))
    T(img, 'do zero', W / 2, 360, 100, GOLD, a=eo3(pr(t, 0.3, 0.4)))
    cards = [
        ('1', 'Cartão garantido', 'Você faz um depósito reembolsável', 'que costuma definir o seu limite.'),
        ('2', 'Credit-builder loan', 'Parcelas pagas em dia ajudam', 'a formar o seu histórico.'),
        ('3', 'Usuário autorizado', 'Entra no cartão de alguém de confiança.', 'Escolha quem paga em dia.'),
    ]
    tops = [500, 790, 1080]
    for i, (n, ti, l1, l2) in enumerate(cards):
        t0 = 0.8 + 2.7 * i
        s = eob(pr(t, t0, 0.6))
        a = cl(pr(t, t0, 0.25))
        dx = (1 - s) * 900
        x0, y0 = 60 + dx, tops[i]
        RR(img, (x0, y0, x0 + 960, y0 + 250), 34, (255, 255, 255, 30), a=a)
        RR(img, (x0, y0, x0 + 14, y0 + 250), 7, GOLD + (255,), a=a)
        circle(img, x0 + 100, y0 + 125, 52, GOLD, a=a)
        T(img, n, x0 + 100, y0 + 122, 60, DARK, a=a, shadow=False)
        T(img, ti, x0 + 185, y0 + 62, 46, WHITE, a=a, anchor='lm')
        T(img, l1, x0 + 185, y0 + 140, 34, MUTED, a=a, anchor='lm', font='Poppins-Medium')
        T(img, l2, x0 + 185, y0 + 190, 34, MUTED, a=a, anchor='lm', font='Poppins-Medium')
    nb = eo3(pr(t, 8.4, 0.5))
    RR(img, (90, 1400, 990, 1500), 50, None, a=nb, outline=TEAL, width=4)
    T(img, 'Sem SSN? Alguns emissores aceitam ITIN.', W / 2, 1450, 36, TEAL, a=nb, font='Poppins-Bold')


def scene5(img, t):
    T(img, 'REGRA DE OURO', W / 2, 430, 54, GOLD, a=eo3(pr(t, 0.1, 0.4)), font='Poppins-Bold')
    T(img, 'Pague em dia.', W / 2, 620, 104, WHITE, a=cl(pr(t, 0.5, 0.2)), scale=max(0.01, eob(pr(t, 0.5, 0.5))))
    T(img, 'Use menos de', W / 2, 800, 90, WHITE, a=cl(pr(t, 1.5, 0.2)), scale=max(0.01, eob(pr(t, 1.5, 0.5))))
    T(img, '30% do limite.', W / 2, 920, 104, GOLD, a=cl(pr(t, 2.2, 0.2)), scale=max(0.01, eob(pr(t, 2.2, 0.5))))
    w = eo3(pr(t, 3.2, 0.5))
    RR(img, (80, 1130, 1000, 1360), 36, (255, 110, 110, 40), a=w, outline=RED, width=4)
    T(img, 'Atenção: cartão tem juros e taxas.', W / 2, 1210, 40, RED, a=w, font='Poppins-Bold')
    T(img, 'Sempre que puder, pague a fatura inteira.', W / 2, 1290, 36, WHITE, a=w, font='Poppins-Medium')


def scene6(img, t):
    T(img, 'Salva esse vídeo', W / 2, 440, 98, GOLD, a=cl(pr(t, 0.2, 0.2)), scale=max(0.01, eob(pr(t, 0.2, 0.5))))
    T(img, 'e segue para mais dicas', W / 2, 600, 60, WHITE, a=eo3(pr(t, 0.9, 0.4)))
    T(img, 'de dinheiro nos EUA', W / 2, 680, 60, WHITE, a=eo3(pr(t, 1.1, 0.4)))
    la = eo3(pr(t, 1.6, 0.6))
    logo(img, W / 2, 800 + (1 - la) * 40, 400, a=la, center=True)
    T(img, 'ROYAL SIGNATURE', W / 2, 1250, 46, LIGHT, a=eo3(pr(t, 2.0, 0.5)), font='Poppins-Bold')
    da = eo3(pr(t, 2.8, 0.5))
    T(img, 'Conteúdo educacional. Não é aconselhamento financeiro.', W / 2, 1350, 32, MUTED, a=da, font='Poppins-Medium')
    T(img, 'Cartões e empréstimos têm juros, taxas e riscos.', W / 2, 1400, 32, MUTED, a=da, font='Poppins-Medium')
    T(img, 'Fontes: myFICO, CFPB, Experian, Capital One', W / 2, 1450, 32, MUTED, a=da, font='Poppins-Medium')


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6]


# Safe zone (social UI): content lives in the SRC band and is scaled into the DST area.
# Keeps clear: top ~290 px (status bar / search / header), bottom ~540 px (username, caption,
# progress bar), right ~190 px (like/comment/share buttons), left ~110 px.
SRC_Y0, SRC_Y1 = 235, 1600
SAFE_K = 0.77
DST_Y0 = 320
DST_CX = 540   # centrado (antes 500 deixava o conteudo para a esquerda)


def frame(si, t):
    global G
    d = DURS[si]
    G = min(1.0, t / 0.25 if si > 0 else 1.0, (d - t) / 0.25 if si < len(DURS) - 1 else 1.0)
    G = max(0.0, G)
    tg = STARTS[si] + t
    img = background(tg)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    SCENES[si](layer, t * SPEED[si])
    band = layer.crop((0, SRC_Y0, W, SRC_Y1))
    bw, bh = int(band.width * SAFE_K), int(band.height * SAFE_K)
    band = band.resize((bw, bh), Image.LANCZOS)
    _over(img, band, (int(DST_CX - bw / 2), DST_Y0))
    return img


def render(si, out):
    d = DURS[si]
    n = int(round(d * FPS))
    tmp = out + '.part.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        im = frame(si, k / FPS)
        p.stdin.write(im.tobytes())
    p.stdin.close()
    rc = p.wait()
    if rc == 0:
        os.rename(tmp, out)
    else:
        raise SystemExit(rc)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        si, t, out = int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
        frame(si, t).save(out)
    elif mode == 'scene':
        render(int(sys.argv[2]), sys.argv[3])
