"""Gerador de ESTILOS variados (sem o anel, sem stickers, sem caixas numeradas do gerador padrao).
uso: python3 tools/make_estilos.py spec.json outdir   -> outdir/silent.mp4
spec: {"estilo": "cinetico|mito|quiz", "theme": "...", "durs": [...], "brand": {...opcional},
       "scenes": [{"type": "kin|mito|quizq|quizans", "bg": "liso|split|listras|bokeh", "img": "imagens/arquivo.jpg (opcional: fundo de imagem IA com zoom lento)", ...}]}
Cenas:
  kin     lines[], hl[indices destacados], sub, ref, logo(bool)   texto cinetico: 1 linha entra por vez
  mito    myth, text, ref, foot                                   tela dividida: o que dizem x o que esta escrito
  quizq   q, opts[3], (barra de contagem regressiva)              pergunta
  quizans q, opts[3], correct(0-2), text, ref                     resposta com versiculo
Fundos: liso (degrade + faixa de luz), split (escuro em cima, creme embaixo), listras (diagonais em movimento), bokeh (o padrao).
"""
import sys, os, json, math, subprocess
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make as M
from make import W, H, T, RR, circle, eo3, eob, pr, cl, F, Image, ImageDraw, ImageFilter
import make_template as MT

CREAM = (250, 244, 232)
SPLIT_Y = 810          # y (quadro inteiro) da divisao do fundo 'split'
_bokeh = M.background


def mix(a, b, k): return tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3))


def bg_liso(tg):
    im = Image.new('RGB', (270, 480)); d = ImageDraw.Draw(im)
    for y in range(480):
        d.line([(0, y), (270, y)], fill=mix(M.BG0, M.BG1, y / 479))
    ov = Image.new('RGBA', (270, 480), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    off = (tg * 18) % 540 - 135   # faixa de luz diagonal lenta
    od.polygon([(off, 0), (off + 60, 0), (off + 60 - 200, 480), (off - 200, 480)], fill=mix(M.BG1, (255, 255, 255), 0.35) + (38,))
    ov = ov.filter(ImageFilter.GaussianBlur(10))
    return Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB').resize((W, H), Image.BILINEAR)


def bg_split(tg):
    im = Image.new('RGB', (270, 480)); d = ImageDraw.Draw(im)
    sy = int(SPLIT_Y / 4)
    for y in range(480):
        if y < sy: c = mix(M.BG0, M.BG1, y / sy * 0.6)
        else: c = mix(CREAM, (238, 226, 206), (y - sy) / (480 - sy))
        d.line([(0, y), (270, y)], fill=c)
    im = im.resize((W, H), Image.BILINEAR)
    ImageDraw.Draw(im).rectangle([0, SPLIT_Y - 5, W, SPLIT_Y + 5], fill=M.GOLD)
    return im


def bg_listras(tg):
    im = Image.new('RGB', (270, 480), M.BG0); d = ImageDraw.Draw(im)
    step = 46; off = (tg * 10) % step
    c2 = mix(M.BG0, M.BG1, 0.55)
    x = -480 - step + off
    while x < 270 + 480:
        d.polygon([(x, 480), (x + step / 2, 480), (x + step / 2 + 480, 0), (x + 480, 0)], fill=c2)
        x += step
    return im.resize((W, H), Image.BILINEAR)


BGS = {'liso': bg_liso, 'split': bg_split, 'listras': bg_listras, 'bokeh': _bokeh}


def wrap(txt, font, size, maxw):
    f = F(font, size); out = []; cur = ''
    for w in txt.split():
        t2 = (cur + ' ' + w).strip()
        if f.getlength(t2) <= maxw or not cur: cur = t2
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out


def lines_block(img, lines, cx, y0, size, col, a, step=None, font='Poppins-Bold'):
    step = step or int(size * 1.25)
    for i, ln in enumerate(lines): T(img, ln, cx, y0 + i * step, size, col, a=a, font=font)
    return y0 + len(lines) * step


# ---------------- cenas ----------------
def kin(sp, d):
    L = sp['lines']; hl = set(sp.get('hl', []))
    n = len(L); size = sp.get('size', 128)
    gap = min(0.7, max(0.3, (d - 1.2) / max(n, 1)))
    def f(img, t):
        y0 = 870 - (n - 1) * size * 1.12 / 2
        for i, ln in enumerate(L):
            t0 = 0.15 + gap * i; p = eob(pr(t, t0, 0.45)); a = eo3(pr(t, t0, 0.25))
            sgn = -1 if i % 2 == 0 else 1
            col = M.GOLD if i in hl else M.WHITE
            T(img, ln, W / 2 + sgn * (1 - min(1, p)) * 420, y0 + i * size * 1.12, size, col, a=a, scale=max(0.3, 0.8 + 0.2 * p))
        if sp.get('sub'):
            T(img, sp['sub'], W / 2, 1230, 46, M.MUTED, a=eo3(pr(t, 0.15 + gap * n + 0.2, 0.5)), font='Poppins-Medium')
        if sp.get('ref'):
            RR(img, (300, 1330, 780, 1420), 45, M.GOLD + (255,), a=eo3(pr(t, 0.15 + gap * n + 0.6, 0.5)))
            T(img, sp['ref'], W / 2, 1375, 44, M.BG0, a=eo3(pr(t, 0.15 + gap * n + 0.6, 0.5)), shadow=False)
        if sp.get('logo'):
            la = eo3(pr(t, 0.2 + gap * n, 0.6)); MT.logo(img, W / 2, 1160 + (1 - la) * 30, 260, a=la, center=True)
        for k, ln in enumerate(sp.get('disc', [])):
            T(img, ln, W / 2, 1450 + 46 * k, 30, M.MUTED, a=eo3(pr(t, 1.5, 0.5)), font='Poppins-Medium')
    return f


def xmark(img, cx, cy, s, p, col, w=14):
    dd = ImageDraw.Draw(img); p = cl(p)
    if p > 0:
        e = (cx - s + 2 * s * p, cy - s + 2 * s * p); dd.line([(cx - s, cy - s), e], fill=col, width=w)
    q = cl((p - 0.5) / 0.5)
    if q > 0:
        e = (cx + s - 2 * s * q, cy - s + 2 * s * q); dd.line([(cx + s, cy - s), e], fill=col, width=w)


def mito(sp, d):
    RED = M.RED
    def f(img, t):
        # topo (fundo escuro): o que dizem. src y 235..1600 -> quadro 320 + (y-235)*.77; divisao em src y ~ 870
        T(img, 'O QUE DIZEM', W / 2, 420, 40, M.MUTED, a=eo3(pr(t, 0.1, 0.4)), font='Poppins-Medium')
        ml = wrap(sp['myth'], 'Poppins-Bold', 70, 820)
        a = eo3(pr(t, 0.3, 0.5)); yb = lines_block(img, ml, W / 2, 560, 76, M.WHITE, a)
        sp_ = pr(t, 1.6, 0.8)
        dd = ImageDraw.Draw(img)
        if sp_ > 0:
            ymid = 560 + (len(ml) - 1) * 48
            dd.line([(150, ymid), (150 + 780 * sp_, ymid)], fill=RED, width=10)
        xmark(img, W / 2, 770, 38, pr(t, 2.2, 0.6), RED)
        # base (fundo creme): o que esta escrito
        t3 = 3.0
        T(img, 'O QUE ESTÁ ESCRITO', W / 2, 1000, 40, M.BG1, a=eo3(pr(t, t3, 0.4)), font='Poppins-Medium', shadow=False)
        tl = wrap(sp['text'], 'Poppins-Bold', 76, 840)
        a = eo3(pr(t, t3 + 0.3, 0.5)); lines_block(img, tl, W / 2, 1130, 76, M.BG0, a)
        circle(img, W / 2, 1345, 46, M.TEAL, a=eo3(pr(t, t3 + 1.2, 0.4)))
        M.check(img, W / 2, 1347, 44, pr(t, t3 + 1.4, 0.6), color=M.BG0, w=10)
        RR(img, (270, 1425, 810, 1515), 45, M.BG0 + (255,), a=eo3(pr(t, t3 + 1.8, 0.5)))
        T(img, sp['ref'], W / 2, 1470, 42, M.GOLD, a=eo3(pr(t, t3 + 1.8, 0.5)), shadow=False)
        if sp.get('foot'):
            T(img, sp['foot'], W / 2, 1555, 30, M.BG1, a=eo3(pr(t, t3 + 2.2, 0.5)), font='Poppins-Medium', shadow=False)
    return f


LET = ['A', 'B', 'C']


def _opts(img, opts, t, t0, correct=None, show_ans=0.0):
    for i, o in enumerate(opts):
        a = eo3(pr(t, t0 + 0.5 * i, 0.4)); y = 830 + i * 165
        dim = 1.0
        fill = (255, 255, 255, 34); out = M.GOLD
        txtc = M.WHITE
        if correct is not None and show_ans > 0:
            if i == correct:
                fill = M.GOLD + (255,); txtc = M.BG0; out = M.WHITE
            else: dim = 1 - 0.65 * show_ans
        RR(img, (90 + (1 - min(1, a)) * 500, y - 70, 990 + (1 - min(1, a)) * 500, y + 70), 36, fill, a=a * dim, outline=out, width=4)
        xo = (1 - min(1, a)) * 500
        circle(img, 170 + xo, y, 44, M.GOLD if not (correct == i and show_ans > 0) else M.BG0, a=a * dim)
        T(img, LET[i], 170 + xo, y - 2, 46, M.BG0 if not (correct == i and show_ans > 0) else M.GOLD, a=a * dim, shadow=False)
        T(img, o, 250 + xo, y, 42, txtc, a=a * dim, anchor='lm', font='Poppins-Medium', shadow=correct is None or show_ans <= 0 or correct != i)


def quizq(sp, d):
    def f(img, t):
        T(img, 'QUIZ BÍBLICO', W / 2, 340, 44, M.GOLD, a=eo3(pr(t, 0.05, 0.3)))
        ql = wrap(sp['q'], 'Poppins-Bold', 66, 860)
        lines_block(img, ql, W / 2, 520, 66, M.WHITE, eo3(pr(t, 0.2, 0.5)))
        _opts(img, sp['opts'], t, 1.0)
        # contagem regressiva
        T0 = 2.8; T1 = d - 0.5
        k = 1 - pr(t, T0, T1 - T0)
        RR(img, (90, 1260, 990, 1286), 13, (255, 255, 255, 40), a=eo3(pr(t, 2.4, 0.3)))
        if k > 0.01: RR(img, (90, 1260, 90 + 900 * k, 1286), 13, M.GOLD + (255,), a=eo3(pr(t, 2.4, 0.3)))
        T(img, 'Pense rápido…', W / 2, 1340, 36, M.MUTED, a=eo3(pr(t, 2.4, 0.3)), font='Poppins-Medium')
    return f


def quizans(sp, d):
    def f(img, t):
        T(img, 'RESPOSTA', W / 2, 340, 44, M.GOLD, a=eo3(pr(t, 0.05, 0.3)))
        ql = wrap(sp['q'], 'Poppins-Bold', 60, 860)
        lines_block(img, ql, W / 2, 500, 60, M.WHITE, 1.0)
        _opts(img, sp['opts'], 99, 0, correct=sp['correct'], show_ans=eo3(pr(t, 0.6, 0.5)))
        a = eo3(pr(t, 1.6, 0.5))
        tl = wrap('“' + sp['text'] + '”', 'Poppins-Medium', 40, 840)
        lines_block(img, tl, W / 2, 1300, 40, M.WHITE, a, step=56, font='Poppins-Medium')
        T(img, sp['ref'], W / 2, 1300 + len(tl) * 56 + 20, 44, M.GOLD, a=eo3(pr(t, 2.4, 0.5)))
    return f


_imgc = {}
def bg_img(path, k, tint=0.55):
    """Fundo de FOTO/ILUSTRACAO (IA): cena com "img": caminho do arquivo (relativo ao repo ou absoluto). Zoom lento (k = 0..1 na cena),
    cobre 1080x1920 e escurece com degrade para o texto ler bem."""
    path = path if os.path.isabs(path) else os.path.join(HERE, '..', path)
    if path not in _imgc:
        im = Image.open(path).convert('RGB'); sc = max(W * 1.15 / im.width, H * 1.15 / im.height)
        _imgc[path] = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    im = _imgc[path]; z = 1.0 + 0.12 * k; cw, ch = int(W * 1.15 / z), int(H * 1.15 / z)
    x0, y0 = (im.width - cw) // 2, (im.height - ch) // 2
    out = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    g = Image.new('L', (1, H))
    for y in range(H): g.putpixel((0, y), int(255 * min(1, tint + 0.25 * abs(y / H - 0.5) * 2)))
    shade = Image.new('RGB', (W, H), M.BG0)
    return Image.composite(shade, out, g.resize((W, H)))


TYPES = {'kin': kin, 'mito': mito, 'quizq': quizq, 'quizans': quizans}


def build(spec_path, outdir):
    spec = json.load(open(spec_path)); os.makedirs(outdir, exist_ok=True)
    MT.apply_theme(spec)
    scenes = spec['scenes']; durs = spec['durs']
    M.DURS = durs; M.OLD_DURS = durs; M.SPEED = [1.0] * len(durs)
    M.STARTS = [sum(durs[:i]) for i in range(len(durs))]; M.TOTAL = sum(durs)
    M.SCENES = [TYPES[s['type']](s, durs[i]) for i, s in enumerate(scenes)]
    default_bg = {'cinetico': 'liso', 'mito': 'split', 'quiz': 'listras'}.get(spec.get('estilo'), 'liso')
    def bgsel(tg):
        i = 0
        for j, s0 in enumerate(M.STARTS):
            if s0 <= tg + 1e-6: i = j
        if scenes[i].get('img'): return bg_img(scenes[i]['img'], max(0, min(1, (tg - M.STARTS[i]) / durs[i])), scenes[i].get('tint', 0.5))
        return BGS[scenes[i].get('bg', default_bg)](tg)
    M.background = bgsel
    M.SRC_Y0 = 235
    def one(i): M.render(i, os.path.join(outdir, f's{i+1}.mp4'))
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, range(len(scenes))))
    lst = os.path.join(outdir, 'list.txt')
    open(lst, 'w').write(''.join(f"file 's{i+1}.mp4'\n" for i in range(len(scenes))))
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(outdir, 'silent.mp4')])
    print('ok', M.TOTAL)


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[1] == 'still':   # still spec.json cena t out.png
        spec = json.load(open(sys.argv[2])); MT.apply_theme(spec)
        durs = spec['durs']; M.DURS = durs; M.OLD_DURS = durs; M.SPEED = [1.0] * len(durs)
        M.STARTS = [sum(durs[:i]) for i in range(len(durs))]; M.TOTAL = sum(durs)
        sc = spec['scenes']; M.SCENES = [TYPES[s['type']](s, durs[i]) for i, s in enumerate(sc)]
        dbg = {'cinetico': 'liso', 'mito': 'split', 'quiz': 'listras'}.get(spec.get('estilo'), 'liso')
        M.background = lambda tg, sc=sc, dbg=dbg: bg_img(sc[max(j for j, s0 in enumerate(M.STARTS) if s0 <= tg + 1e-6)]['img'], 0.3) if sc[max(j for j, s0 in enumerate(M.STARTS) if s0 <= tg + 1e-6)].get('img') else BGS[sc[max(j for j, s0 in enumerate(M.STARTS) if s0 <= tg + 1e-6)].get('bg', dbg)](tg)
        M.frame(int(sys.argv[3]), float(sys.argv[4])).save(sys.argv[5])
    else:
        build(sys.argv[1], sys.argv[2])
