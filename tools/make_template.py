"""Gerador generico de videos Royal Signature a partir de um spec JSON.
uso: python3 make_template.py spec.json outdir   (renderiza cenas s1..s6.mp4 e junta em silent.mp4)
spec: {"theme":"royal|esmeralda|ameixa|grafite|oceano|por-do-sol", "durs":[6 duracoes em s], "scenes":[{type:hook|stat|calc|cards|rule|cta, ...}]}
"""
import sys, os, json, math, subprocess
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make as M
from make import *
import themes
DESIGN = {'verse': 8.0, 'hook': 5.0, 'stat': 8.0, 'calc': 8.0, 'cards': 10.0, 'rule': 8.0, 'cta': 6.0}

def pop(img, txt, y, size, col, t, t0, font='Poppins-Bold'):
    T(img, txt, W / 2, y, size, col, a=cl(pr(t, t0, 0.2)), scale=max(0.01, eob(pr(t, t0, 0.5))), font=font)

def hook(sp):
    def f(img, t):
        la = eo3(pr(t, 0, 0.4))
        if BRAND_NAME:
            tw = F('Poppins-Bold', 32).getlength(BRAND_NAME); lw0 = M._logo(92).width
            x0 = (W - (lw0 + 20 + tw)) / 2
            lw = logo(img, x0, 245, 92, a=la)
            T(img, BRAND_NAME, x0 + lw + 20, 291, 32, M.LIGHT, a=0.95 * la, anchor='lm')
        else:  # logo ja traz o nome da marca: centralizado no topo
            logo(img, W / 2, 232, 160, a=la, center=True)
        T(img, sp['l1'], W / 2, 440, 86, WHITE, a=eo3(pr(t, 0.1, 0.4)))
        T(img, sp['l2'], W / 2, 550, 86, WHITE, a=eo3(pr(t, 0.4, 0.4)))
        pop(img, sp['big'], 730, 190, GOLD, t, 0.9)
        # anel animado
        a = eo3(pr(t, 1.4, 0.5)); cx, cy, r = W / 2, 1160, 190
        layer = Image.new('RGBA', (W, 500), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        box = [cx - r, 250 - r, cx + r, 250 + r]
        d.ellipse(box, outline=(255, 255, 255, int(60 * a * M.G)), width=30)
        sweep = 40 + 30 * math.sin(t * 2.0)
        d.arc(box, -90, -90 + sweep, fill=GOLD + (int(255 * a * M.G),), width=30)
        M._over(img, layer, (0, cy - 250))
        T(img, sp.get('ring', '$0'), cx, cy - 15, 110, WHITE, a=a)
        T(img, sp.get('ringlabel', 'reserva'), cx, cy + 75, 36, MUTED, a=a, font='Poppins-Medium')
        T(img, sp['sub1'], W / 2, 1520, 42, MUTED, a=eo3(pr(t, 2.8, 0.5)), font='Poppins-Medium')
        T(img, sp['sub2'], W / 2, 1572, 42, MUTED, a=eo3(pr(t, 3.0, 0.5)), font='Poppins-Medium')
    return f

def stat(sp):
    def f(img, t):
        T(img, sp['title'], W / 2, 300, 76, WHITE, a=eo3(pr(t, 0.1, 0.4)))
        pop(img, sp['big'], 560, 230, GOLD, t, 0.5)
        T(img, sp['unit'], W / 2, 735, 90, WHITE, a=eo3(pr(t, 1.2, 0.4)))
        T(img, sp['line'], W / 2, 850, 46, MUTED, a=eo3(pr(t, 1.6, 0.4)), font='Poppins-Medium')
        chips = sp['chips']
        for i, c in enumerate(chips):
            t0 = 2.6 + 0.8 * i; a = eo3(pr(t, t0, 0.4)); s = eob(pr(t, t0, 0.5))
            x0 = 100 + (i % 2) * 450; y0 = 1010 + (i // 2) * 170
            RR(img, (x0, y0, x0 + 430, y0 + 130), 65, (255, 255, 255, 30), a=a, outline=TEAL, width=4)
            T(img, c, x0 + 215, y0 + 65, 46, WHITE, a=a * min(1, s))
        T(img, sp['foot'], W / 2, 1450, 36, MUTED, a=eo3(pr(t, 6.0, 0.5)), font='Poppins-Medium')
    return f

def calc(sp):
    def f(img, t):
        T(img, sp['title'], W / 2, 300, 76, WHITE, a=eo3(pr(t, 0.1, 0.4)))
        rows = sp['rows']  # [[label, value], ...] 2 linhas + resultado em sp['result']
        for i, (lab, val) in enumerate(rows):
            t0 = 0.9 + 1.3 * i; a = eo3(pr(t, t0, 0.4)); y = 560 + i * 230
            RR(img, (100, y - 80, 980, y + 80), 40, (255, 255, 255, 30), a=a)
            T(img, lab, 140, y, 42, WHITE, a=a, anchor='lm', font='Poppins-Medium')
            T(img, val, 940, y, 64, TEAL, a=a, anchor='rm')
        a = eo3(pr(t, 3.6, 0.4)); d = ImageDraw.Draw(img)
        if a * M.G > 0.3: d.line([(100, 960), (980, 960)], fill=GOLD, width=6)
        rl, rv = sp['result']
        T(img, rl, W / 2, 1030, 48, WHITE, a=a)
        pop(img, rv, 1180, 190, GOLD, t, 4.2)
        T(img, sp['foot'], W / 2, 1400, 36, MUTED, a=eo3(pr(t, 5.6, 0.5)), font='Poppins-Medium')
    return f

def cards(sp):
    def f(img, t):
        T(img, sp['t1'], W / 2, 270, 70, WHITE, a=eo3(pr(t, 0.1, 0.4)))
        T(img, sp['t2'], W / 2, 360, 100, GOLD, a=eo3(pr(t, 0.3, 0.4)))
        tops = [500, 790, 1080]
        for i, (n, ti, l1, l2) in enumerate(sp['cards']):
            t0 = 0.8 + 2.7 * i; s = eob(pr(t, t0, 0.6)); a = cl(pr(t, t0, 0.25))
            x0, y0 = 60 + (1 - s) * 900, tops[i]
            RR(img, (x0, y0, x0 + 960, y0 + 250), 34, (255, 255, 255, 30), a=a)
            RR(img, (x0, y0, x0 + 14, y0 + 250), 7, GOLD + (255,), a=a)
            circle(img, x0 + 100, y0 + 125, 52, GOLD, a=a)
            T(img, n, x0 + 100, y0 + 122, 60, M.BG0, a=a, shadow=False)
            T(img, ti, x0 + 185, y0 + 62, 46, WHITE, a=a, anchor='lm')
            T(img, l1, x0 + 185, y0 + 140, 34, MUTED, a=a, anchor='lm', font='Poppins-Medium')
            T(img, l2, x0 + 185, y0 + 190, 34, MUTED, a=a, anchor='lm', font='Poppins-Medium')
        nb = eo3(pr(t, 8.4, 0.5))
        RR(img, (90, 1400, 990, 1500), 50, None, a=nb, outline=TEAL, width=4)
        T(img, sp['note'], W / 2, 1450, 36, TEAL, a=nb)
    return f

def rule(sp):
    def f(img, t):
        T(img, 'REGRA DE OURO', W / 2, 430, 54, GOLD, a=eo3(pr(t, 0.1, 0.4)))
        pop(img, sp['a'], 620, 104, WHITE, t, 0.5)
        pop(img, sp['b'], 800, 90, WHITE, t, 1.5)
        pop(img, sp['c'], 920, 104, GOLD, t, 2.2)
        w = eo3(pr(t, 3.2, 0.5))
        RR(img, (80, 1130, 1000, 1360), 36, (255, 110, 110, 40), a=w, outline=RED, width=4)
        T(img, sp['w1'], W / 2, 1210, 40, RED, a=w)
        T(img, sp['w2'], W / 2, 1290, 36, WHITE, a=w, font='Poppins-Medium')
    return f

def cta(sp):
    def f(img, t):
        pop(img, sp['a'], 440, 98, GOLD, t, 0.2)
        T(img, sp['b'], W / 2, 600, 60, WHITE, a=eo3(pr(t, 0.9, 0.4)))
        T(img, sp['c'], W / 2, 680, 60, WHITE, a=eo3(pr(t, 1.1, 0.4)))
        la = eo3(pr(t, 1.6, 0.6)); logo(img, W / 2, 800 + (1 - la) * 40, 400, a=la, center=True)
        if BRAND_NAME: T(img, BRAND_NAME, W / 2, 1250, 46, M.LIGHT, a=eo3(pr(t, 2.0, 0.5)))
        da = eo3(pr(t, 2.8, 0.5))
        for i, ln in enumerate(sp['disc']):
            T(img, ln, W / 2, 1350 + 50 * i, 32, MUTED, a=da, font='Poppins-Medium')
    return f

def verse(sp):
    """title, lines (versiculo quebrado em linhas de ~24 caracteres, max 7), ref (ex.: Salmos 23:1), foot (versao/traducao)"""
    def f(img, t):
        T(img, sp['title'], W / 2, 300, 70, WHITE, a=eo3(pr(t, 0.1, 0.4)))
        T(img, '\u201c', W / 2, 470, 200, GOLD, a=eo3(pr(t, 0.3, 0.4)))
        n = len(sp['lines']); y0 = 640; step = 96
        for i, ln in enumerate(sp['lines']):
            T(img, ln, W / 2, y0 + i * step, 58, WHITE, a=eo3(pr(t, 0.8 + 0.6 * i, 0.45)), font='Poppins-Medium')
        ya = y0 + n * step + 40
        pop(img, sp['ref'], ya, 70, GOLD, t, 0.8 + 0.6 * n + 0.3)
        T(img, sp['foot'], W / 2, ya + 100, 34, MUTED, a=eo3(pr(t, 0.8 + 0.6 * n + 1.0, 0.5)), font='Poppins-Medium')
    return f

TYPES = {'verse': verse, 'hook': hook, 'stat': stat, 'calc': calc, 'cards': cards, 'rule': rule, 'cta': cta}

BRAND_NAME = 'ROYAL SIGNATURE'

def apply_theme(spec):
    global BRAND_NAME
    br = spec.get('brand')  # {"logo": "brand/x.png", "name": ""} - sem 'brand' = Royal Signature
    if br:
        M.LOGO_PATH = os.path.join(M.HERE, '..', br['logo']); M._logo.cache_clear(); BRAND_NAME = br.get('name', '')

    th = themes.THEMES[spec.get('theme', 'royal')]
    fb, fm = themes.FONTS[th['font']]
    M.FONTMAP.update({'Poppins-Bold': fb, 'Poppins-Medium': fm})
    M.BG0, M.BG1 = th['bg0'], th['bg1']
    M.BLOBS = [tuple(min(255, c + 60) for c in th['bg1']) + (90,), th['a2'] + (38,), th['a1'] + (30,), tuple(min(255, c + 40) for c in th['bg1']) + (70,)]
    g = globals(); g['GOLD'] = th['a1']; g['TEAL'] = th['a2']; g['DARK'] = th['bg0']; M.GOLD = th['a1']; M.TEAL = th['a2']

def build(spec_path, outdir):
    spec = json.load(open(spec_path)); os.makedirs(outdir, exist_ok=True)
    apply_theme(spec)
    scenes = spec['scenes']; durs = spec['durs']
    old = [DESIGN[s['type']] for s in scenes]
    M.OLD_DURS = old; M.DURS = durs
    M.SPEED = [o / d for o, d in zip(old, durs)]
    M.STARTS = [sum(durs[:i]) for i in range(len(durs))]; M.TOTAL = sum(durs)
    M.SCENES = [TYPES[s['type']](s) for s in scenes]
    M.SRC_Y0 = 235
    def one(i):
        M.render(i, os.path.join(outdir, f's{i+1}.mp4'))
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, range(len(scenes))))
    lst = os.path.join(outdir, 'list.txt')
    open(lst, 'w').write(''.join(f"file 's{i+1}.mp4'\n" for i in range(len(scenes))))
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(outdir, 'silent.mp4')])
    print('ok', M.TOTAL)

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
