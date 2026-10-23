"""Собрать одного персонажа: голова от HEAD, тело от BODY, опционально перекраска одежды.
Запуск из Content/art:
  /usr/bin/python3 ../../tools/kitbash/make.py HEAD BODY OUT [HUE]
  HEAD/BODY — имена без префикса и расширения (lucullus, wellington)
  OUT       — имя нового спрайта без префикса (franklin) -> char_franklin.webp в текущей папке
  HUE       — сдвиг оттенка доминантного цвета одежды тела, 0..1 (0.55 ~ красный->синий); опционально
"""
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import compose as c
head,body,out=sys.argv[1:4]; hue=float(sys.argv[4]) if len(sys.argv)>4 else None
for n in (head,body):
    if f'char_{n}.webp' not in c.scan: sys.exit(f'{n}: нет в scan.json (шея не найдена или не базовый 512x768) — выбери другой спрайт')
dst=f'char_{out}.webp'
if os.path.exists(dst): sys.exit(f'{dst} уже существует — не перезаписываю')
c.compose(head,body,hue).save(dst,'WEBP',quality=92,method=6)
print('saved',dst)
