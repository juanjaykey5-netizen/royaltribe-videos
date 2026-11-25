"""Imprime tema visual e trilha do dia.
python3 tools/variety.py            -> 'tema musica' (videos de financas, dias pares: usa ordinal//2 para passar pelos 6 temas)
python3 tools/variety.py carrossel  -> 'tema' do carrossel (dias impares; deslocado para nao coincidir com o video)
"""
import datetime, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes
o = datetime.date.today().toordinal() // 2
if len(sys.argv) > 1 and sys.argv[1].startswith('carrossel'):
    print(themes.pick(o + 3)[0])
else:
    print(*themes.pick(o))
