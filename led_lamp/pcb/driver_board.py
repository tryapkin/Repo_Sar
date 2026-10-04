"""Драйверная плата: FR4, 2 слоя. Верх: детали и сигнальные дорожки. Низ: сплошной полигон GND.

Два канала PT4115 (SOT89-5), высокая сторона датчика тока, ток = 0.1 В / Rs.
Распиновка по даташиту: 1 SW, 2 GND, 3 EN/DIM, 4 RS (CSN), 5 IN; открытая площадка = GND.
Вид сверху после поворота рисунка из даташита на 90° против часовой:
  север: IN(5) слева, RS(4) справа, площадка GND в центре
  юг:    SW(1) слева, GND(2) в центре, DIM(3) справа
"""
from pcb_lib import Board

W, H = 70.0, 36.0
CY = 19.0
RAIL_Y = CY - 11.0
CX = (27.0, 51.0)


def chip(b, ref, cx, cy, n1, n2, size="1206", vertical=False):
    h = 1.8 if size == "1206" else 2.7
    if vertical:
        b.pad(ref, "1", cx, cy - 1.5, h, 1.2, n1)
        b.pad(ref, "2", cx, cy + 1.5, h, 1.2, n2)
    else:
        b.pad(ref, "1", cx - 1.5, cy, 1.2, h, n1)
        b.pad(ref, "2", cx + 1.5, cy, 1.2, h, n2)
    b.body("c" + size, cx, cy, 90 if vertical else 0, ref)


def channel(b, k, cx, cy=CY):
    CSN, LK, SW, DIM = f"CSN{k}", f"LK{k}", f"SW{k}", f"DIM{k}"
    U, R, C, D, L = f"U{k}", f"R{k}", f"C{k}", f"D{k}", f"L{k}"
    # --- PT4115
    b.pad(U, "5", cx - 1.5, cy - 1.95, 0.7, 1.5, "VIN")
    b.pad(U, "4", cx + 1.5, cy - 1.95, 0.7, 1.5, CSN)
    b.pad(U, "T", cx, cy - 1.65, 1.5, 2.1, "GND")
    b.pad(U, "1", cx - 1.5, cy + 1.95, 0.7, 1.5, SW)
    b.pad(U, "2", cx, cy + 1.95, 0.7, 1.5, "GND")
    b.pad(U, "3", cx + 1.5, cy + 1.95, 0.7, 1.5, DIM)
    b.body("sot89", cx, cy, 0, U)
    b.silk_poly([(cx - 3.0, cy + 2.5), (cx - 3.0, cy + 3.0)], closed=False)  # метка вывода 1
    # --- датчик тока Rs 1206
    chip(b, R, cx, cy - 6.0, "VIN", CSN)
    # --- входной конденсатор 1210 (лежит слева от IN; минус - в полигон через переход)
    chip(b, C, cx - 5.5, cy - 1.2, "GND", "VIN", size="1210")
    # --- диод SMA: K слева (к шине VIN), A справа (к узлу SW)
    b.pad(D, "K", cx - 8.5, cy + 4.5, 2.5, 1.7, "VIN")
    b.pad(D, "A", cx - 4.5, cy + 4.5, 2.5, 1.7, SW)
    b.body("sma", cx - 6.5, cy + 4.5, 0, D)
    b.silk_line(cx - 7.0, cy + 3.75, cx - 7.0, cy + 5.25, 0.2)  # полоса катода
    # --- дроссель 6x6 (посадочное место ориентировочное, сверить с выбранной деталью)
    b.pad(L, "1", cx + 2.15, cy + 9.0, 1.9, 5.0, LK)
    b.pad(L, "2", cx - 2.15, cy + 9.0, 1.9, 5.0, SW)
    b.body("ind", cx, cy + 9.0, 0, L)
    # --- выходные площадки для проводов к светодиодной плате и тестовая площадка DIM
    b.pad("AP" if k == 1 else "BP", "1", cx + 10, cy - 6.0, 4.0, 4.0, CSN)
    b.pad("AN" if k == 1 else "BN", "1", cx + 10, cy + 9.0, 4.0, 4.0, LK)
    b.pad(f"DIM{k}", "1", cx + 4.5, cy + 4.5, 2.0, 2.0, DIM)
    # --- дорожки (верх)
    b.track("VIN", [(cx - 1.5, RAIL_Y), (cx - 1.5, cy - 6.0)], 1.0)
    b.track("VIN", [(cx - 1.5, cy - 6.0), (cx - 1.5, cy - 1.95)], 0.7)
    b.track("VIN", [(cx - 4.0, cy - 1.95), (cx - 1.5, cy - 1.95)], 0.7)
    b.track("VIN", [(cx - 8.5, RAIL_Y), (cx - 8.5, cy + 4.5)], 1.0)
    # короткая локальная перемычка VIN: замыкает петлю обратного тока диода D -> Rs -> LED -> L
    # рядом с микросхемой, а не через верхнюю шину
    b.track("VIN", [(cx - 8.5, cy - 4.2), (cx - 1.5, cy - 4.2)], 0.8)
    b.track(CSN, [(cx + 1.5, cy - 1.95), (cx + 1.5, cy - 6.0)], 0.7)
    b.track(CSN, [(cx + 1.5, cy - 6.0), (cx + 10, cy - 6.0)], 1.0)
    b.track(SW, [(cx - 1.5, cy + 1.95), (cx - 1.5, cy + 7.0)], 0.8)
    b.track(SW, [(cx - 1.5, cy + 4.5), (cx - 4.5, cy + 4.5)], 1.0)
    b.track(LK, [(cx + 2.15, cy + 9.0), (cx + 10, cy + 9.0)], 1.0)
    b.track(DIM, [(cx + 1.5, cy + 1.95), (cx + 1.5, cy + 4.5), (cx + 4.5, cy + 4.5)], 0.5)
    # --- земля: переходы на нижний полигон
    b.via(cx, cy - 3.6, "GND")
    b.track("GND", [(cx, cy - 1.65), (cx, cy - 3.6)], 0.5)
    b.via(cx, cy + 3.6, "GND")
    b.track("GND", [(cx, cy + 1.95), (cx, cy + 3.6)], 0.5)
    b.via(cx - 7.0, cy + 1.4, "GND")
    b.track("GND", [(cx - 7.0, cy - 1.2), (cx - 7.0, cy + 1.4)], 0.6)
    # --- подписи
    b.silk_text(U, cx + 5.0, cy - 1.0, 1.2)
    b.silk_text(R, cx + 3.8, cy - 8.8, 1.2)
    b.silk_text(C, cx - 4.4, cy + 1.9, 1.2)
    b.silk_text(D, cx - 6.5, cy + 7.6, 1.2)
    b.silk_text(L, cx + 6.5, cy + 6.9, 1.2)
    b.silk_text("A+" if k == 1 else "B+", cx + 10, cy - 8.9, 1.3)
    b.silk_text("A-" if k == 1 else "B-", cx + 10, cy + 12.2, 1.3)
    b.silk_text(f"DIM{k}", cx + 6.3, cy + 4.5, 1.1, anchor="l")


def build():
    b = Board("LED_DRIVER_2xPT4115", W, H, corner=2.0, layers=2)
    for k, cx in enumerate(CX, 1):
        channel(b, k, cx)
    # --- входные площадки питания
    b.pad("J1", "+12V", 7.5, RAIL_Y, 5.0, 5.0, "VIN")
    b.pad("J1", "GND", 7.5, 24.0, 5.0, 5.0, "GND")
    b.track("VIN", [(7.5, RAIL_Y), (CX[1] - 1.5, RAIL_Y)], 1.2)
    for x in (5.5, 7.5, 9.5):
        b.via(x, 28.2, "GND")
        b.track("GND", [(x, 24.0), (x, 28.2)], 0.8)
    b.silk_text("+12V", 7.5, 12.4, 1.4)
    b.silk_text("GND", 7.5, 20.6, 1.4)
    for x, y in [(3.8, 3.8), (W - 3.8, 3.8), (3.8, H - 3.8), (W - 3.8, H - 3.8)]:
        b.hole(x, y, 3.2)
    b.pour_zone("GND", layer="bot", inset=0.3)
    b.silk_text("LED DRIVER 12V 2xPT4115 700mA", 38.0, 34.0, 1.3)
    return b


if __name__ == "__main__":
    b = build()
    b.check()
