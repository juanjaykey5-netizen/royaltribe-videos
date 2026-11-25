"""Imprime tema visual e trilha do dia: python3 tools/variety.py -> 'tema musica'"""
import datetime, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes
print(*themes.pick(datetime.date.today().toordinal()))
