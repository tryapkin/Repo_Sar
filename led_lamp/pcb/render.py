"""Цветная визуализация плат (вид сверху/снизу, с установленными деталями, включённое состояние)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle, Rectangle, FancyBboxPatch
from shapely.geometry import Point
from shapely.ops import unary_union

THEMES = {
    "white_alu": dict(mask="#f3f3ee", under="#e4dbc9", finish="#c6cad1", silk="#1d1d1d", edge="#9aa0a8",
                      bg="#20242b", plane="#e4dbc9"),
    "green_fr4": dict(mask="#17683a", under="#26884f", finish="#c6cad1", silk="#f1f1f1", edge="#0d3f23",
                      bg="#20242b", plane="#2b9257"),
}


def _poly_patch(g, **kw):
    patches = []
    for part in (g.geoms if hasattr(g, "geoms") else [g]):
        if part.is_empty or part.geom_type != "Polygon":
            continue
        verts, codes = [], []
        for ring in [part.exterior] + list(part.interiors):
            pts = list(ring.coords)
            verts += pts
            codes += [Path.MOVETO] + [Path.LINETO] * (len(pts) - 2) + [Path.CLOSEPOLY]
        patches.append(PathPatch(Path(verts, codes), **kw))
    return patches


def _add(ax, g, **kw):
    for p in _poly_patch(g, **kw):
        ax.add_patch(p)


def _glow(ax, cx, cy, R, color=(1.0, 0.82, 0.35), z=5):
    n = 300
    yy, xx = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]
    r = np.sqrt(xx ** 2 + yy ** 2)
    a = np.clip(1 - r, 0, 1) ** 2.2 * 0.85
    img = np.zeros((n, n, 4))
    img[..., 0], img[..., 1], img[..., 2], img[..., 3] = color[0], color[1], color[2], a
    ax.imshow(img, extent=(cx - R, cx + R, cy + R, cy - R), zorder=z, interpolation="bilinear")


def _body(ax, bd, powered, th):
    k, cx, cy, rot = bd["kind"], bd["cx"], bd["cy"], bd["rot"]
    z = 8

    def rect(w, h, fc, ec="#111", lw=0.6, r=0.2, zz=z):
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                    fc=fc, ec=ec, lw=lw, zorder=zz))

    if k == "oslon":
        rect(3.0, 3.0, "#f7f7f1", ec="#b8b8ae", r=0.15)
        ax.add_patch(Circle((cx, cy), 1.2, fc="#fffbe2" if powered else "#e8b92e", ec="#c99a1a", lw=0.6, zorder=z + 1))
        ax.add_patch(Circle((cx - 0.35, cy - 0.4), 0.35, fc=(1, 1, 1, 0.55), ec="none", zorder=z + 2))
        if powered:
            _glow(ax, cx, cy, 2.6, (1.0, 0.95, 0.7), z=z + 3)
    elif k == "sot89":
        rect(4.5, 2.5, "#25282e", r=0.25)
        ax.text(cx, cy, "PT4115", color="#9aa1ad", fontsize=3.2, ha="center", va="center", zorder=z + 1)
    elif k in ("c1206", "c1210"):
        w, h = (3.2, 1.6) if k == "c1206" else (3.2, 2.5)
        if rot == 90:
            w, h = h, w
        body = "#171717" if bd["label"].startswith("R") else "#c9a56d"
        rect(w, h, body, ec="#444", r=0.15)
        capw = 0.6
        if rot == 90:
            for sy in (-1, 1):
                ax.add_patch(Rectangle((cx - w / 2, cy + sy * (h / 2 - capw / 2) - capw / 2), w, capw, fc="#cfd3d9", ec="none", zorder=z + 1))
        else:
            for sx in (-1, 1):
                ax.add_patch(Rectangle((cx + sx * (w / 2 - capw / 2) - capw / 2, cy - h / 2), capw, h, fc="#cfd3d9", ec="none", zorder=z + 1))
        if bd["label"].startswith("R"):
            ax.text(cx, cy, "R150", color="#ddd", fontsize=2.8, ha="center", va="center", zorder=z + 2)
    elif k == "sma":
        rect(4.3, 2.6, "#141416", r=0.2)
        ax.add_patch(Rectangle((cx - 2.15 + 0.15, cy - 1.3), 0.55, 2.6, fc="#d4d7dc", ec="none", zorder=z + 1))
    elif k == "ind":
        rect(6.0, 6.0, "#3a3e47", ec="#202228", r=0.5)
        ax.add_patch(Circle((cx, cy), 2.4, fc="#4a4f5a", ec="#2b2e35", lw=0.5, zorder=z + 1))
        ax.text(cx, cy, "330", color="#aab0bb", fontsize=4, ha="center", va="center", zorder=z + 2)


def render(b, path, side="top", powered=False, theme="white_alu", ppm=22, title=None, flip=False):
    th = THEMES[theme]
    W, H = b.W, b.H
    mx = 5
    fig = plt.figure(figsize=((W + 2 * mx) * ppm / 100, (H + 2 * mx + (4 if title else 0)) * ppm / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    fig.patch.set_facecolor(th["bg"])
    ax.set_facecolor(th["bg"])
    ax.set_xlim((W + mx) if flip else -mx, -mx if flip else (W + mx))
    ax.set_ylim(H + mx, -mx - (4 if title else 0))
    ax.set_aspect("equal")
    ax.axis("off")
    out = b.outline_poly()
    # тень
    from shapely import affinity
    _add(ax, affinity.translate(out, 0.6, 0.9), fc="#000000", ec="none", alpha=0.45, zorder=0)
    _add(ax, out, fc=th["mask"], ec=th["edge"], lw=1.2, zorder=1)
    layer = "top" if side == "top" else "bot"
    for net, g, kind, ref in b.layer_items(layer):
        if kind == "pour":
            _add(ax, g, fc=th["plane"], ec="none", zorder=2)
        elif kind in ("track", "island"):
            _add(ax, g, fc=th["under"], ec="none", zorder=2)
    # открытые площадки (покрытие)
    for p in b.pads:
        if p["layer"] == layer and p["mask"]:
            gm = b.pad_geom(p, 0.0)
            _add(ax, gm, fc=th["finish"], ec="#8d939b", lw=0.3, zorder=3)
        elif p["layer"] == layer:
            _add(ax, b.pad_geom(p), fc=th["under"], ec="none", zorder=2)
    # переходные отверстия (закрыты маской)
    for v in b.vias:
        ax.add_patch(Circle((v["cx"], v["cy"]), v["d"] / 2, fc=th["under"], ec="#00000030", lw=0.4, zorder=3))
        ax.add_patch(Circle((v["cx"], v["cy"]), v["drill"] / 2, fc="#0b0d10", ec="none", zorder=4))
    for h in b.holes:
        ax.add_patch(Circle((h["cx"], h["cy"]), h["d"] / 2 + 0.25, fc="#b8bcc3", ec="none", zorder=3))
        ax.add_patch(Circle((h["cx"], h["cy"]), h["d"] / 2, fc=th["bg"], ec="#00000060", lw=0.5, zorder=4))
    if side == "top":
        for s in b.silk:
            (x1, y1), (x2, y2) = s["pts"]
            ax.plot([x1, x2], [y1, y2], color=th["silk"], lw=max(s["w"] * ppm / 100 * 72 * 0.9, 0.6),
                    solid_capstyle="round", zorder=6)
        if powered:
            for bd in b.bodies:
                if bd["kind"] == "oslon":
                    _glow(ax, bd["cx"], bd["cy"], 13.0, z=5)
        for bd in b.bodies:
            _body(ax, bd, powered, th)
    if title:
        ax.text((W / 2), -mx - 1.2 + 0.8, title, color="#e9edf3", fontsize=ppm * 0.62, ha="center", va="center",
                fontweight="bold")
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
