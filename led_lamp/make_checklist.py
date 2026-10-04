rows=[
("1","Осмотр","Пайка, полярность LED/диодов/конденсаторов; прозвонка +12 В — GND без питания","Нет КЗ, сопротивление не ≈0"),
("2","Первое включение","12 В, ограничение 0,3 А, затем 1,5 А","Нет дыма, нет резкого роста тока"),
("3","Канал A (3 LED)","Напряжение на Rs, ток = U/0,15 Ом","667 мА ±10% (600–733)"),
("4","Канал B (2 LED)","То же","667 мА ±10% (600–733)"),
("5","Развертка напряжения","См. таблицу ниже, 9 → 14 В","Ток канала A ≥ 600 мА при 11–14 В"),
("6","Оба канала","12 В, общий ток блока питания","≈1,0–1,2 А"),
("7","Пульсации","Осциллограф: вход и цепь LED","Без резких выбросов (по даташиту)"),
("8","Тепло","30 мин на радиаторе, температуры ниже","Ниже допустимого по даташитам"),
("9","Диммирование DIM","ШИМ 1 кГц, 10–100%","Яркость меняется плавно"),
("10","Выдержка","4–8 ч при 12 В","Ток и температура не уходят"),
]
def tr(r): return f'<tr><td class="c">{r[0]}</td><td><b>{r[1]}</b><br><span>{r[2]}</span></td><td>{r[3]}</td><td class="m"></td><td class="c">☐ да<br>☐ нет</td></tr>'
sweep=''.join(f'<tr><td class="c">{v:.1f}</td><td class="m"></td><td class="m"></td><td class="m"></td></tr>' for v in [9,10,11,12,13,14])
therm=''.join(f'<tr><td>{n}</td><td class="m"></td><td class="m"></td><td>{lim}</td></tr>' for n,lim in [("Точка пайки LED (Ts)","≤ 85 °C (даташит OSLON)"),("PT4115 U1","≤ 85 °C (рабочий диапазон)"),("PT4115 U2","≤ 85 °C (рабочий диапазон)"),("Индуктивности L1/L2","по даташиту детали"),("Диоды D1/D2","по даташиту детали"),("Радиатор","—")])
css='''@page{size:A4;margin:14mm}*{box-sizing:border-box}body{font-family:"Liberation Sans",Arial,sans-serif;font-size:9.5pt;color:#111;line-height:1.35}
h1{font-size:17pt;margin-bottom:2mm}h2{font-size:11.5pt;margin:6mm 0 2mm}table{width:100%;border-collapse:collapse}
th{background:#1d2230;color:#fff;font-size:8.5pt;text-align:left;padding:1.6mm 2mm}td{border:.25mm solid #aab;padding:1.6mm 2mm;vertical-align:top}
td.c{text-align:center}td.m{min-width:26mm;height:11mm}span{color:#444;font-size:8.5pt}.meta td{height:8mm}.warn{border:.4mm solid #c33;background:#fff4f4;padding:2.5mm;margin-top:4mm;font-size:9pt}
.page{page-break-after:always}'''
meta=''.join(f'<td><span>{a}</span></td>' for a in ["Дата:","Плата / ревизия:","Исполнитель:","Блок питания, Vin:"])
html=f'''<!doctype html><html lang="ru"><meta charset="utf-8"><style>{css}</style><body>
<h1>Чек-лист испытаний: светильник 5× OSLON, 12 В, 700 мА</h1>
<table class="meta"><tr>{meta}</tr></table>
<h2>Основные проверки</h2>
<table><tr><th>№</th><th>Проверка и метод</th><th>Критерий</th><th>Результат</th><th>Годен</th></tr>{"".join(tr(r) for r in rows)}</table>
<div class="warn"><b>Безопасность.</b> Не отсоединять светодиоды при включённом питании. Без радиатора включать только на секунды. Не смотреть прямо на включённые светодиоды.</div>
<div class="page"></div>
<h2>Этап 5. Развертка напряжения (ток по Rs, мА)</h2>
<table><tr><th>Vin, В</th><th>Канал A, мА</th><th>Канал B, мА</th><th>Заметки</th></tr>{sweep}</table>
<p><span>Напряжение, при котором ток канала A упал ниже 600 мА: ________ В. Если оно выше 11 В — поднять питание до 13,8 В или перейти на каналы 2+2+1.</span></p>
<h2>Этап 8. Температуры через 30 мин (°C)</h2>
<table><tr><th>Точка</th><th>10 мин</th><th>30 мин</th><th>Предел по даташиту</th></tr>{therm}</table>
<h2>Итог</h2>
<table><tr><td style="height:24mm"><span>Вывод (годен / доработка), решение по компоновке и радиатору:</span></td></tr></table>
</body></html>'''
open('lamp_test_checklist.html','w',encoding='utf-8').write(html)
