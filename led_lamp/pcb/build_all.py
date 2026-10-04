"""Полная сборка: проверки -> Gerber -> zip для JLCPCB -> картинки -> BOM/координаты."""
import os, shutil, zipfile, csv
import led_board, driver_board, render, assembly

BOARDS = [(led_board, "LED_MCPCB_5xOSLON"), (driver_board, "LED_DRIVER_2xPT4115")]
shutil.rmtree("gerber", ignore_errors=True)
os.makedirs("out", exist_ok=True)
for mod, name in BOARDS:
    b = mod.build()
    errs, msgs, _ = b.check(verbose=True)
    assert errs == 0, f"{name}: {errs} ошибок проверки"
    d = f"gerber/{name}"
    b.export_gerber(d)
    for f in os.listdir(d):
        base, ext = os.path.splitext(f)
        if f.endswith(".nonplated.drl"):
            new = base.replace(".nonplated", "") + "_NPTH.DRL"
        elif f.endswith(".plated.drl"):
            new = base.replace(".plated", "") + "_PTH.DRL"
        else:
            new = base + ext.upper()
        os.rename(f"{d}/{f}", f"{d}/{new}")
    with zipfile.ZipFile(f"{name}_gerber.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(d)):
            z.write(f"{d}/{f}", f)
    print("zip:", f"{name}_gerber.zip", sorted(os.listdir(d)))

lb, db = led_board.build(), driver_board.build()
render.render(lb, "out/led_board_off.png", "top", False, "white_alu", title="LED-плата (алюминий) — выключена")
render.render(lb, "out/led_board_on.png", "top", True, "white_alu", title="LED-плата — включена, 700 мА")
render.render(db, "out/driver_top.png", "top", False, "green_fr4", ppm=20, title="Драйверная плата (FR4, 2 слоя) — верх")
render.render(db, "out/driver_bottom.png", "bot", False, "green_fr4", ppm=20, title="Драйверная плата — низ: сплошной полигон GND", flip=True)
assembly.make("out/assembly.png")
for f in ("out/_d.png", "out/_l.png"):
    if os.path.exists(f):
        os.remove(f)

# координаты центров деталей драйверной платы (Gerber: начало внизу слева, Y вверх)
H = driver_board.H
with open("driver_part_positions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Ref", "Mid X, мм", "Mid Y, мм", "Слой", "Поворот (не задан — сверить в предпросмотре фабрики)"])
    for bd in db.bodies:
        w.writerow([bd["label"], round(bd["cx"], 3), round(H - bd["cy"], 3), "Top", ""])
with open("BOM.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Плата", "Позиции", "Кол-во", "Номинал / тип", "Корпус", "Примечание"])
    rows = [
        ("LED", "LED1–LED5", 5, "OSRAM OSLON Square GW CSSRM1.PC (белый, цветовую температуру выбрать)", "3.0×3.0 мм, 3 площадки", "Площадки по даташиту GW CSSRM1.PC; для другой серии сверить"),
        ("Драйвер", "U1, U2", 2, "PT4115 (30 В, 1,2 А)", "SOT-89-5", "Вход 8–30 В по даташиту RYCHIP; сверить у выбранного производителя"),
        ("Драйвер", "R1, R2", 2, "0,15 Ом 1% ≥0,25 Вт", "1206", "Ток ≈667 мА (Rs = 0,1 В / I)"),
        ("Драйвер", "C1, C2", 2, "10 мкФ 50 В X7R", "1210", ""),
        ("Драйвер", "D1, D2", 2, "SS34 (Шоттки 3 А, 40 В)", "SMA (DO-214AC)", "Полоса катода — слева на шёлке"),
        ("Драйвер", "L1, L2", 2, "33 мкГн, Isat ≥1,5 А, низкое DCR", "≈6×6 мм, экранированная", "Посадочное место ориентировочное — под выбранную деталь сверить"),
        ("Оба", "Провода", 6, "0,5–0,75 мм², питание 12 В + 4 провода к LED-плате", "", "Пайка на площадки 5×4 мм / 5×5 мм"),
    ]
    w.writerows(rows)
print("готово")
