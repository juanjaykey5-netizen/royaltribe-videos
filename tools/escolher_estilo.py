"""Escolhe estilo, cor, fonte, voz e musica que NAO repetem nos ultimos N videos (financas + biblia juntos).
uso:
  python3 tools/escolher_estilo.py fin|bib            -> imprime a escolha (nao grava)
  python3 tools/escolher_estilo.py registrar SISTEMA ESTILO FORMATO ASSUNTO COR FONTE VOZ MUSICA   -> grava no estilos_usados.md
Regra (Juan): cor, fonte, voz e musica nao repetem por pelo menos 7 videos seguidos; estilo nao repete nos ultimos 3.
Cada video usa spec com "theme": COR e "font": FONTE (sobrescreve a fonte do tema), voz = voiceId no vidiq_voiceover_generate, musica = audio/music_<MUSICA>.mp3."""
import sys, os, random, datetime
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'estilos_usados.md')
JANELA = 7
ESTILOS = ['padrao', 'cinetico', 'mito', 'quiz']
CORES = {'fin': ['royal', 'esmeralda', 'ameixa', 'grafite', 'oceano', 'por-do-sol', 'rosa-fofo', 'lavanda', 'menta'],
         'bib': ['aljava', 'lavanda', 'rosa-fofo', 'menta', 'oceano', 'por-do-sol', 'ameixa', 'esmeralda', 'royal']}
FONTES = ['poppins', 'montserrat', 'nunito', 'oswald', 'merriweather', 'dmsans', 'fira', 'crimson', 'anton', 'archivo']
MUSICAS = ['lofi', 'bright', 'calm', 'groove', 'warm', 'jazz', 'drive', 'dream', 'pulse']
# vozes em PT primeiro; as demais leem portugues com sotaque (ElevenLabs multilingue). Confirmar com o Juan.
VOZES = {'Keren': '33B4UnXyTNbgLmdEDh5P', 'Roberta': 'RGymW84CSmfVugnA5tvA', 'Diego': 'rpNe0HOx7heUulPiOEaG',
         'Will-PT': 'CstacWqMhJQlnfLPxRG4', 'Sarah': 'EXAVITQu4vr4xnSDxMaL', 'Eric': 'cjVigY5qzO86Huf0OWal',
         'Brian': 'nPczCjzI2devNBz1zQrb', 'Matilda': 'XrExE9yKIg1WjnnlVkGX'}
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
    voz = livre(list(VOZES), rows, 'voz', JANELA)
    return dict(estilo=livre(ESTILOS, rows, 'estilo', 3), cor=livre(CORES[sis], rows, 'cor', JANELA),
                fonte=livre(FONTES, rows, 'fonte', JANELA), voz=voz, voiceId=VOZES[voz], musica=livre(MUSICAS, rows, 'musica', JANELA))
if __name__ == '__main__':
    if sys.argv[1] == 'registrar':
        a = sys.argv[2:]; assert len(a) == 8, 'faltam campos'
        open(LOG, 'a', encoding='utf-8').write(f"{datetime.date.today()} | {a[0]} | " + ' | '.join(a[1:]) + '\n'); print('registrado')
    else:
        for k, v in escolher(sys.argv[1]).items(): print(f'{k}: {v}')
