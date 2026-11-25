#!/usr/bin/env python3
"""Plano diario do Aljava GC (Biblia): qual peca e qual banco de imagens vale para a data.
  python3 tools/plano_biblia.py [AAAA-MM-DD]            -> imprime a peca do dia (id, tipo, tema, estilo da ilustracao, imagens)
  python3 tools/plano_biblia.py aplicar spec.json [AAAA-MM-DD]  -> grava as imagens do dia no spec:
        video (specs de make_estilos.py): "img" em cada cena kin/mito que ainda nao tem (3 imagens -> pares de cenas; 6 imagens -> uma por cena)
        carrossel (make_carousel.py): "imagens": [...] (capa, meio e ultimo slide)
Se nao houver peca para a data (acabou o banco), imprime SEM_IMAGENS e nao altera nada: a rotina segue com os estilos sem foto."""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); PLANO = os.path.join(HERE, '..', 'planejamento', 'biblia_plano_imagens.json')
def achar(data):
    for p in json.load(open(PLANO, encoding='utf-8')):
        if p['data'] == data and all(os.path.exists(os.path.join(HERE, '..', i)) for i in p['imagens']): return p
def main():
    a = sys.argv[1:]
    if a and a[0] == 'aplicar':
        spec_path = a[1]; data = a[2] if len(a) > 2 else datetime.date.today().isoformat()
        p = achar(data)
        if not p: print('SEM_IMAGENS'); return
        spec = json.load(open(spec_path, encoding='utf-8')); im = p['imagens']
        if 'slides' in spec: spec['imagens'] = im
        else:
            sc = [s for s in spec['scenes'] if s['type'] in ('kin', 'mito')]
            for k, s in enumerate(sc):
                if not s.get('img'): s['img'] = im[min(len(im) - 1, k * len(im) // len(sc))]
        json.dump(spec, open(spec_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('ok', p['id'], len(im), 'imagens'); return
    data = a[0] if a else datetime.date.today().isoformat(); p = achar(data)
    print(json.dumps(p, ensure_ascii=False, indent=1) if p else 'SEM_IMAGENS')
main()
