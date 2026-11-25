import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
GF = '/usr/share/fonts/truetype/google-fonts/'
FONTS = {
    'poppins':   (GF + 'Poppins-Bold.ttf', GF + 'Poppins-Medium.ttf'),
    'montserrat': (ROOT + '/fonts/montserrat-latin-700-normal.woff', ROOT + '/fonts/montserrat-latin-500-normal.woff'),
    'nunito':    (ROOT + '/fonts/nunito-latin-700-normal.woff', ROOT + '/fonts/nunito-latin-500-normal.woff'),
    'merriweather': (ROOT + '/fonts/merriweather-latin-700-normal.woff', ROOT + '/fonts/merriweather-latin-400-normal.woff'),
    'oswald':    (ROOT + '/fonts/oswald-latin-700-normal.woff', ROOT + '/fonts/oswald-latin-500-normal.woff'),
    'dmsans':    (ROOT + '/fonts/dm-sans-latin-700-normal.woff', ROOT + '/fonts/dm-sans-latin-500-normal.woff'),
}
# bg0 (topo), bg1 (base), a1 (destaque 1), a2 (destaque 2), blobs RGBA
THEMES = {
    'royal':    dict(font='poppins',    bg0=(8, 20, 48),  bg1=(20, 44, 98),  a1=(245, 183, 0),   a2=(24, 194, 156)),
    'esmeralda': dict(font='montserrat', bg0=(4, 28, 26),  bg1=(10, 72, 60),  a1=(255, 196, 64),  a2=(120, 232, 192)),
    'ameixa':   dict(font='nunito',     bg0=(28, 10, 48), bg1=(74, 30, 104), a1=(255, 128, 176), a2=(130, 222, 255)),
    'grafite':  dict(font='oswald',     bg0=(10, 12, 16), bg1=(40, 44, 56),  a1=(255, 98, 64),   a2=(255, 212, 0)),
    'oceano':   dict(font='merriweather',   bg0=(3, 26, 52),  bg1=(0, 92, 122),  a1=(255, 218, 160), a2=(92, 224, 232)),
    'por-do-sol': dict(font='dmsans',   bg0=(38, 12, 24), bg1=(112, 42, 52), a1=(255, 180, 70),  a2=(255, 124, 104)),
}
MUSICS = ['lofi', 'bright', 'calm', 'groove', 'warm']
def pick(ordinal):
    names = list(THEMES)
    return names[ordinal % len(names)], MUSICS[(ordinal * 2 + ordinal // 5) % len(MUSICS)]
