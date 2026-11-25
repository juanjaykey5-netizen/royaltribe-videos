"""Escolhe estilo, cor, fonte, voz e musica que NAO repetem nos ultimos N videos (financas + biblia juntos).
uso:
  python3 tools/escolher_estilo.py fin|bib|car            -> imprime a escolha (nao grava)
  python3 tools/escolher_estilo.py registrar SISTEMA ESTILO FORMATO ASSUNTO COR FONTE VOZ MUSICA   -> grava no estilos_usados.md
CARROSSEL: registrar com estilo 'carrossel-<variante>' (ex.: carrossel-capa-foto), voz '-' e musica '-'; ele conta na janela de cor e fonte (videos e carrosseis juntos), mas nao na de voz, musica e estilo de video.
Regra (Juan): cor, fonte e musica nao repetem por 7 videos; voz (so 4 em PT) nao repete nos ultimos 3; estilo nos ultimos 3.
Cada video usa spec com "theme": COR e "font": FONTE (sobrescreve a fonte do tema), voz = voiceId no vidiq_voiceover_generate, musica = audio/music_<MUSICA>.mp3."""
import sys, os, random, datetime
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'estilos_usados.md')
JANELA = 7
ESTILOS = ['padrao', 'cinetico', 'mito', 'quiz']
CORES = {'car': ['royal', 'esmeralda', 'ameixa', 'grafite', 'oceano', 'por-do-sol', 'rosa-fofo', 'lavanda', 'menta'], 'fin': ['royal', 'esmeralda', 'ameixa', 'grafite', 'oceano', 'por-do-sol', 'rosa-fofo', 'lavanda', 'menta'],
         'bib': ['aljava', 'lavanda', 'rosa-fofo', 'menta', 'oceano', 'por-do-sol', 'ameixa', 'esmeralda', 'royal']}
FONTES = ['poppins', 'montserrat', 'nunito', 'oswald', 'merriweather', 'dmsans', 'fira', 'crimson', 'anton', 'archivo']
MUSICAS = ['lofi', 'bright', 'calm', 'groove', 'warm', 'jazz', 'drive', 'dream', 'pulse']
# Vozes: SOMENTE as 4 em portugues nativo (decisao do Juan). Com 4 vozes a janela de voz e 3 (nao repete nos ultimos 3 videos).
VOZES = {'Keren': '33B4UnXyTNbgLmdEDh5P', 'Roberta': 'RGymW84CSmfVugnA5tvA', 'Diego': 'rpNe0HOx7heUulPiOEaG',
         'Will-PT': 'CstacWqMhJQlnfLPxRG4'}
JANELA_VOZ = 3
ESTILOS_CAR = ['padrao', 'jornal', 'poster', 'quiz']  # carrosseis: padrao=make_carousel_fin.py; os outros=make_carrossel_estilos.py
COLS = ['data', 'sistema', 'estilo', 'formato', 'assunto', 'cor', 'fonte', 'voz', 'musica']
def ler():
    rows = []
    for ln in open(LOG, encoding='utf-8'):
        if ln.startswith('#') or not ln.strip(): continue
        p = [x.strip() for x in ln.split('|')]
        p += ['?'] * (len(COLS) - len(p)); rows.append(dict(zip(COLS, p)))
    return rows
def livre(pool, rows, col, n):
    usados = [r[col] for r in rows[-n:]]
    cand = [x for x in pool if x not in usados]
    if not cand: raise SystemExit(f'sem opcao livre em {col}: amplie o pool (janela {n}, pool {len(pool)})')
    # prefere o que ficou mais tempo sem uso
    ult = {x: max([i for i, r in enumerate(rows) if r[col] == x] or [-1]) for x in cand}
    m = min(ult.values()); return random.choice([x for x in cand if ult[x] == m])
def escolher(sis):
    rows = ler(); random.seed(datetime.datetime.now().timestamp())
    car = [r for r in rows if r['sistema'] == 'car' or r['estilo'].startswith('carrossel')]
    vid = [r for r in rows if r not in car]   # carrosseis nao tem voz/musica/estilo de video, mas contam em cor e fonte
    if sis == 'car':   # carrossel: estilo nao repete nos ultimos 3 CARROSSEIS; cor e fonte nao repetem por 7 (todos os sistemas)
        return dict(estilo=livre(ESTILOS_CAR, car, 'estilo', 3), cor=livre(CORES['car'], rows, 'cor', JANELA), fonte=livre(FONTES, rows, 'fonte', JANELA))
    voz = livre(list(VOZES), vid, 'voz', JANELA_VOZ)
    return dict(estilo=livre(ESTILOS, vid, 'estilo', 3), cor=livre(CORES[sis], rows, 'cor', JANELA),
                fonte=livre(FONTES, rows, 'fonte', JANELA), voz=voz, voiceId=VOZES[voz], musica=livre(MUSICAS, vid, 'musica', JANELA))
if __name__ == '__main__':
    if sys.argv[1] == 'registrar':
        a = sys.argv[2:]; assert len(a) == 8, 'faltam campos'
        open(LOG, 'a', encoding='utf-8').write(f"{datetime.date.today()} | {a[0]} | " + ' | '.join(a[1:]) + '\n'); print('registrado')
    else:
        for k, v in escolher(sys.argv[1]).items(): print(f'{k}: {v}')
