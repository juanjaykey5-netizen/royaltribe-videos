"""Desenhos fofinhos (kawaii) para os videos biblicos. Uso: art.draw(kind, size) -> imagem RGBA (fundo transparente).
kinds: ovelha, pomba, estrela, sol, arca, biblia, coracao, nuvem. Todos com carinha (olhos pontinhos + bochechas)."""
import math
from PIL import Image, ImageDraw
S = 4  # supersampling

def _face(d, cx, cy, u, dark=(60, 40, 40)):
    for sx in (-1, 1):
        d.ellipse([cx + sx * 1.5 * u - 0.38 * u, cy - 0.38 * u, cx + sx * 1.5 * u + 0.38 * u, cy + 0.38 * u], fill=dark)
        d.ellipse([cx + sx * 2.6 * u - 0.7 * u, cy + 0.7 * u, cx + sx * 2.6 * u + 0.7 * u, cy + 1.5 * u], fill=(255, 150, 160, 190))
    d.arc([cx - 0.7 * u, cy - 0.1 * u, cx + 0.7 * u, cy + 1.0 * u], 20, 160, fill=dark, width=max(2, int(0.22 * u)))

def _canvas(n):
    return Image.new('RGBA', (n * S, n * S), (0, 0, 0, 0))

def ovelha(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    for x, y in [(6, 11), (9, 8.5), (12.5, 8.5), (15, 11), (13, 14), (8, 14), (10.5, 11.5)]:
        d.ellipse([(x - 3.4) * u, (y - 3.4) * u, (x + 3.4) * u, (y + 3.4) * u], fill=(255, 250, 242))
    for x in (7, 13):
        d.rounded_rectangle([(x - 0.8) * u, 15.5 * u, (x + 0.8) * u, 18.5 * u], 0.8 * u, fill=(120, 86, 70))
    d.ellipse([6.2 * u, 7.5 * u, 13.8 * u, 14.6 * u], fill=(236, 205, 170))
    for sx in (-1, 1):
        d.ellipse([10 * u + sx * 4.6 * u - 1.3 * u, 9.6 * u, 10 * u + sx * 4.6 * u + 1.3 * u, 11.8 * u], fill=(236, 205, 170))
    _face(d, 10 * u, 10.6 * u, u * 0.8)
    return im

def pomba(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    d.ellipse([4 * u, 7 * u, 16 * u, 17 * u], fill=(255, 255, 255))
    d.ellipse([11 * u, 3.5 * u, 17.5 * u, 10 * u], fill=(255, 255, 255))
    d.polygon([(17 * u, 6.2 * u), (19.5 * u, 7 * u), (17 * u, 8 * u)], fill=(255, 190, 90))
    d.ellipse([2 * u, 6 * u, 10 * u, 14 * u], fill=(226, 238, 252))
    d.polygon([(4.5 * u, 11 * u), (1 * u, 9 * u), (3 * u, 13.5 * u)], fill=(226, 238, 252))
    d.arc([14 * u, 12 * u, 19.5 * u, 18 * u], 200, 340, fill=(100, 170, 90), width=int(0.45 * u))
    for a, b in [(15.5, 16.4), (17, 16.6), (18.3, 15.6)]:
        d.ellipse([(a - 0.9) * u, (b - 0.5) * u, (a + 0.9) * u, (b + 0.5) * u], fill=(120, 190, 100))
    _face(d, 13.8 * u, 6.7 * u, u * 0.55)
    return im

def estrela(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    pts = []
    for i in range(10):
        r = 9 if i % 2 == 0 else 4.4
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((10 * u + r * u * math.cos(a), 10.6 * u + r * u * math.sin(a)))
    d.polygon(pts, fill=(255, 217, 90), outline=(255, 238, 170), width=int(0.5 * u))
    d.line(pts + [pts[0]], fill=(255, 238, 170), width=int(0.9 * u), joint='curve')
    _face(d, 10 * u, 10.8 * u, u * 0.9)
    return im

def sol(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    for i in range(12):
        a = i * math.pi / 6
        x, y = 10 * u + 8.6 * u * math.cos(a), 10 * u + 8.6 * u * math.sin(a)
        d.ellipse([x - 1.1 * u, y - 1.1 * u, x + 1.1 * u, y + 1.1 * u], fill=(255, 205, 80))
    d.ellipse([3.6 * u, 3.6 * u, 16.4 * u, 16.4 * u], fill=(255, 224, 110))
    _face(d, 10 * u, 10 * u, u * 0.95)
    return im

def arca(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    for i, c in enumerate([(255, 120, 120), (255, 190, 90), (255, 235, 120), (130, 210, 140), (110, 180, 255)]):
        d.arc([2 * u + i * 0.5 * u, 0.6 * u + i * 0.5 * u, 18 * u - i * 0.5 * u, 14 * u + i * 1.0 * u], 180, 360, fill=c, width=int(0.8 * u))
    d.rounded_rectangle([6.5 * u, 6.6 * u, 14 * u, 11.6 * u], 0.8 * u, fill=(214, 160, 108))
    d.polygon([(6 * u, 6.8 * u), (10.2 * u, 3.4 * u), (14.6 * u, 6.8 * u)], fill=(176, 108, 74))
    d.polygon([(1.6 * u, 11 * u), (18.4 * u, 11 * u), (15.6 * u, 16.6 * u), (4.4 * u, 16.6 * u)], fill=(150, 96, 66))
    d.rectangle([1.6 * u, 11 * u, 18.4 * u, 12 * u], fill=(190, 130, 90))
    _face(d, 10 * u, 9.1 * u, u * 0.62)
    return im

def biblia(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    d.rounded_rectangle([3.4 * u, 3 * u, 16.6 * u, 17.4 * u], 1.6 * u, fill=(120, 80, 150))
    d.rounded_rectangle([4.6 * u, 3.8 * u, 16.6 * u, 16.6 * u], 1.2 * u, fill=(250, 244, 230))
    d.rounded_rectangle([3.4 * u, 3 * u, 5.4 * u, 17.4 * u], 0.8 * u, fill=(96, 62, 128))
    d.rectangle([10.3 * u, 5.2 * u, 11.7 * u, 8.6 * u], fill=(255, 205, 90)); d.rectangle([9 * u, 6.2 * u, 13 * u, 7.4 * u], fill=(255, 205, 90))
    _face(d, 10.6 * u, 12.4 * u, u * 0.8)
    return im

def coracao(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    d.ellipse([2.4 * u, 3.4 * u, 10.6 * u, 11.6 * u], fill=(255, 120, 150)); d.ellipse([9.4 * u, 3.4 * u, 17.6 * u, 11.6 * u], fill=(255, 120, 150))
    d.polygon([(2.6 * u, 8.6 * u), (17.4 * u, 8.6 * u), (10 * u, 17.8 * u)], fill=(255, 120, 150))
    d.ellipse([4.4 * u, 4.8 * u, 7 * u, 7.2 * u], fill=(255, 190, 205))
    _face(d, 10 * u, 9.6 * u, u * 0.9)
    return im

def nuvem(n):
    im = _canvas(n); d = ImageDraw.Draw(im); u = n * S / 20
    for i, c in enumerate([(255, 120, 120), (255, 190, 90), (255, 235, 120), (130, 210, 140), (110, 180, 255)]):
        d.arc([2 * u + i * 0.6 * u, 1 * u + i * 0.6 * u, 18 * u - i * 0.6 * u, 15 * u + i * 0.6 * u], 180, 360, fill=c, width=int(0.8 * u))
    for x, y, r in [(6.5, 14, 3.2), (10, 12.4, 4), (13.6, 14, 3.2), (8.2, 15.4, 3), (12, 15.4, 3)]:
        d.ellipse([(x - r) * u, (y - r) * u, (x + r) * u, (y + r) * u], fill=(255, 255, 255))
    _face(d, 10 * u, 14 * u, u * 0.8)
    return im

KINDS = dict(ovelha=ovelha, pomba=pomba, estrela=estrela, sol=sol, arca=arca, biblia=biblia, coracao=coracao, nuvem=nuvem)

def draw(kind, size):
    return KINDS[kind](size).resize((size, size), Image.LANCZOS)
