"""Светодиодная плата: алюминиевая (MCPCB), 1 слой меди. 5x OSRAM OSLON Square (GW CSSRM1.xx).

Контактные площадки LED — по даташиту GW CSSRM1.PC (Recommended Solder Pad): три площадки
(анод 0.55 мм, тепловая 1.0 мм, катод 0.55 мм), длина 2.8 мм, зазор 0.35 мм.
"""
from shapely.geometry import box
from shapely.ops import unary_union
from pcb_lib import Board

W, H = 76.0, 40.0


def oslon(b, ref, cx, cy, anode, cathode, therm):
    # планки вертикальные: анод слева, катод справа (цепочка идёт слева направо)
    b.pad(ref, "A", cx - 1.125, cy, 0.55, 2.8, anode)
    b.pad(ref, "T", cx, cy, 1.0, 2.8, therm)
    b.pad(ref, "K", cx + 1.125, cy, 0.55, 2.8, cathode)
    # контур корпуса 3.0x3.0 и метка катода на шёлке
    s = 1.75
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.silk_line(cx + sx * s, cy + sy * s, cx + sx * (s - 0.5), cy + sy * s)
            b.silk_line(cx + sx * s, cy + sy * s, cx + sx * s, cy + sy * (s - 0.5))
    b.silk_line(cx + 2.35, cy - 1.3, cx + 2.35, cy + 1.3, 0.3)  # катод
    b.body("oslon", cx, cy, 0, ref)


def heat_island(cx, cy):
    """Медный остров для отвода тепла вокруг тепловой площадки: шея 1.0 мм между
    планками + блоки сверху и снизу."""
    neck = box(cx - 0.5, cy - 4.0, cx + 0.5, cy + 4.0)
    top = box(cx - 4.0, cy - 6.5, cx + 4.0, cy - 1.8)
    bot = box(cx - 4.0, cy + 1.8, cx + 4.0, cy + 6.5)
    return unary_union([neck, top, bot])


def build():
    b = Board("LED_MCPCB_5xOSLON", W, H, corner=3.0, layers=1)
    row1, row2 = 12.0, 28.0
    leds = [("LED1", 23.0, row1, "A_P", "N1"), ("LED2", 38.0, row1, "N1", "N2"), ("LED3", 53.0, row1, "N2", "A_N"),
            ("LED4", 30.5, row2, "B_P", "N3"), ("LED5", 45.5, row2, "N3", "B_N")]
    for i, (ref, x, y, a, k) in enumerate(leds, 1):
        oslon(b, ref, x, y, a, k, f"TH{i}")
        b.island(heat_island(x, y), f"TH{i}")
    # выводные площадки для проводов 5x4 мм
    px_l, px_r = 9.0, 67.0
    for ref, x, y, net in [("A+", px_l, row1, "A_P"), ("A-", px_r, row1, "A_N"),
                           ("B+", px_l, row2, "B_P"), ("B-", px_r, row2, "B_N")]:
        b.pad(ref, "1", x, y, 5.0, 4.0, net)
        b.silk_text(ref, x, y - 4.2, 1.5)
    # дорожки цепочек (2.0 мм, ток 0.7 А). Концы круглые (апертура Gerber), поэтому центр конца
    # отодвинут от тепловой площадки на половину ширины: колпачок доходит ровно до края планки.
    w = 2.0
    e = 0.85 + w / 2  # от центра LED до центра конца дорожки
    xs = {"LED1": 23.0, "LED2": 38.0, "LED3": 53.0, "LED4": 30.5, "LED5": 45.5}
    b.track("A_P", [(px_l, row1), (xs["LED1"] - e, row1)], w)
    b.track("N1", [(xs["LED1"] + e, row1), (xs["LED2"] - e, row1)], w)
    b.track("N2", [(xs["LED2"] + e, row1), (xs["LED3"] - e, row1)], w)
    b.track("A_N", [(xs["LED3"] + e, row1), (px_r, row1)], w)
    b.track("B_P", [(px_l, row2), (xs["LED4"] - e, row2)], w)
    b.track("N3", [(xs["LED4"] + e, row2), (xs["LED5"] - e, row2)], w)
    b.track("B_N", [(xs["LED5"] + e, row2), (px_r, row2)], w)
    # монтажные отверстия M3
    for x, y in [(3.8, 3.8), (W - 3.8, 3.8), (3.8, H - 3.8), (W - 3.8, H - 3.8)]:
        b.hole(x, y, 3.2)
    # подписи
    for ref, x, y, *_ in leds[:3]:
        b.silk_text(ref, x, 20.2, 1.4)
    for ref, x, y, *_ in leds[3:]:
        b.silk_text(ref, x, 36.6, 1.4)
    b.silk_text("5x OSLON  700mA", 38.0, 2.6, 1.6)
    return b


if __name__ == "__main__":
    b = build()
    b.check()
