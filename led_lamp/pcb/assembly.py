"""Схема соединения плат проводами (картинка)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import led_board, driver_board, render

PPM, MX = 16, 5


def px(board_origin, x, y):
    return board_origin[0] + (x + MX) * PPM, board_origin[1] + (y + MX) * PPM


def make(path):
    db, lb = driver_board.build(), led_board.build()
    render.render(db, "out/_d.png", "top", False, "green_fr4", ppm=PPM)
    render.render(lb, "out/_l.png", "top", True, "white_alu", ppm=PPM)
    di, li = plt.imread("out/_d.png"), plt.imread("out/_l.png")
    gap = 420
    Wc = di.shape[1] + li.shape[1] + gap + 280
    Hc = max(di.shape[0], li.shape[0]) + 330
    fig = plt.figure(figsize=(Wc / 100, Hc / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, Wc); ax.set_ylim(Hc, 0); ax.axis("off")
    fig.patch.set_facecolor("#20242b")
    do = (200, 200)
    lo = (do[0] + di.shape[1] + gap, 200 + 60)
    ax.imshow(di, extent=(do[0], do[0] + di.shape[1], do[1] + di.shape[0], do[1]), zorder=1)
    ax.imshow(li, extent=(lo[0], lo[0] + li.shape[1], lo[1] + li.shape[0], lo[1]), zorder=1)
    ax.text(do[0] + di.shape[1] / 2, do[1] - 28, "ПЛАТА ДРАЙВЕРА (FR4, 2 слоя)", color="#e9edf3", fontsize=15, ha="center", fontweight="bold")
    ax.text(lo[0] + li.shape[1] / 2, lo[1] - 28, "ПЛАТА СВЕТОДИОДОВ (алюминий)", color="#e9edf3", fontsize=15, ha="center", fontweight="bold")

    def wire(p0, p1, c0, c1, color, label=None, lw=5):
        v = [p0, c0, c1, p1]
        ax.add_patch(PathPatch(Path(v, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc="none", ec="#00000090", lw=lw + 3, zorder=9, capstyle="round"))
        ax.add_patch(PathPatch(Path(v, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc="none", ec=color, lw=lw, zorder=10, capstyle="round"))

    cx1, cx2, cy = driver_board.CX[0], driver_board.CX[1], driver_board.CY
    dpad = {"A+": (cx1 + 10, cy - 6), "A-": (cx1 + 10, cy + 9), "B+": (cx2 + 10, cy - 6), "B-": (cx2 + 10, cy + 9)}
    lpad = {"A+": (9, 12), "A-": (67, 12), "B+": (9, 28), "B-": (67, 28)}
    col = {"A+": "#ff4d4d", "A-": "#ffb020", "B+": "#4da3ff", "B-": "#35e0d0"}
    # маршруты: A+ и B+ — прямо к левым площадкам; A- — над платой; B- — под платой
    P = {k: px(do, *dpad[k]) for k in dpad}
    Q = {k: px(lo, *lpad[k]) for k in lpad}
    top_y, bot_y = lo[1] + 0, lo[1] + li.shape[0] + 20
    wire(P["A+"], Q["A+"], (P["A+"][0] + 160, P["A+"][1] - 60), (Q["A+"][0] - 180, Q["A+"][1] - 40), col["A+"])
    wire(P["B+"], Q["B+"], (P["B+"][0] + 200, P["B+"][1] + 160), (Q["B+"][0] - 220, Q["B+"][1] + 120), col["B+"])
    wire(P["A-"], Q["A-"], (P["A-"][0] + 120, top_y - 110), (Q["A-"][0] + 110, top_y - 130), col["A-"])
    wire(P["B-"], Q["B-"], (P["B-"][0] + 150, bot_y + 90), (Q["B-"][0] + 120, bot_y + 70), col["B-"])
    for k in P:
        ax.text(P[k][0] + 18, P[k][1] - 16, k.replace("-", "−"), color=col[k], fontsize=11, fontweight="bold", zorder=11)
        ax.text(Q[k][0] + (-60 if "+" in k else 22), Q[k][1] - 22, k.replace("-", "−"), color=col[k], fontsize=11, fontweight="bold", zorder=11)
    # питание
    psu = (30, do[1] + 90)
    ax.add_patch(FancyBboxPatch((20, do[1] + 110), 150, 190, boxstyle="round,pad=0,rounding_size=14", fc="#2f3540", ec="#8d96a5", lw=2, zorder=3))
    ax.text(95, do[1] + 190, "Блок\nпитания\n12 В", color="#e9edf3", fontsize=14, ha="center", va="center", fontweight="bold")
    Jp, Jg = px(do, 7.5, driver_board.RAIL_Y), px(do, 7.5, 24.0)
    wire((170, do[1] + 150), (Jp[0] - 22, Jp[1]), (210, do[1] + 150), (Jp[0] - 100, Jp[1]), "#ff4d4d", lw=6)
    wire((170, do[1] + 250), (Jg[0] - 22, Jg[1]), (210, do[1] + 250), (Jg[0] - 100, Jg[1]), "#c9ced6", lw=6)
    ax.text(178, do[1] + 128, "+12 В", color="#ff4d4d", fontsize=11, fontweight="bold")
    ax.text(178, do[1] + 278, "GND", color="#c9ced6", fontsize=11, fontweight="bold")
    ax.text(Wc / 2, Hc - 45, "4 провода к светодиодной плате: A+ → A+, A− → A−, B+ → B+, B− → B−. Сечение ≥ 0,5 мм², длина до ~1 м. Питание: ≥12 В, ≥1,5 А.",
            color="#aab2bd", fontsize=11, ha="center")
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    make("out/assembly.png")
