"""Минимальная библиотека для проектирования простых плат: модель, проверки, Gerber, рендер.

Координаты в мм, ось Y вниз (как на экране). При экспорте в Gerber Y переворачивается
(начало координат — левый нижний угол платы).
"""
import math
import os
import itertools
from collections import defaultdict

from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from HersheyFonts import HersheyFonts

_hf = HersheyFonts()
_hf.load_default_font()


# ---------------------------------------------------------------- текст (штриховой шрифт)
def stroke_text(s, x, y, h, anchor="c", rot=0):
    sc = h / 21.0
    lines = list(_hf.lines_for_text(s))
    xs = [p[0] for l in lines for p in l]
    if not xs:
        return []
    minx, maxx = min(xs), max(xs)
    w = (maxx - minx) * sc
    ox = {"c": -minx * sc - w / 2, "l": -minx * sc, "r": -minx * sc - w}[anchor]
    oy = 1.5 * sc
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for a, b in lines:
        pts = []
        for px, py in (a, b):
            qx, qy = ox + px * sc, oy + py * sc
            pts.append((x + qx * ca - qy * sa, y + qx * sa + qy * ca))
        out.append(tuple(pts))
    return out


def rot_xy(x, y, rot):
    k = (rot // 90) % 4
    for _ in range(k):
        x, y = -y, x
    return x, y


# ---------------------------------------------------------------- модель платы
class Board:
    def __init__(self, name, W, H, corner=2.0, layers=1, mask_exp=0.05):
        self.name, self.W, self.H, self.corner = name, W, H, corner
        self.layers = layers
        self.mask_exp = mask_exp
        self.pads, self.tracks, self.vias, self.holes = [], [], [], []
        self.islands, self.silk, self.bodies, self.labels = [], [], [], []
        self.pour = None  # (layer, net, edge_inset)
        self._nc = 0

    # ---- построение
    def pad(self, ref, pin, cx, cy, w, h, net=None, layer="top", shape="rect", mask=True):
        if net is None:
            self._nc += 1
            net = f"NC_{ref}_{pin}"
        self.pads.append(dict(ref=ref, pin=pin, cx=cx, cy=cy, w=w, h=h, net=net, layer=layer,
                              shape=shape, mask=mask))

    def track(self, net, pts, w, layer="top"):
        self.tracks.append(dict(net=net, pts=list(pts), w=w, layer=layer))

    def via(self, cx, cy, net, d=0.6, drill=0.3):
        self.vias.append(dict(cx=cx, cy=cy, net=net, d=d, drill=drill))

    def hole(self, cx, cy, d):
        self.holes.append(dict(cx=cx, cy=cy, d=d))

    def island(self, poly, net, layer="top"):
        self.islands.append(dict(poly=poly, net=net, layer=layer))

    def silk_line(self, x1, y1, x2, y2, w=0.15):
        self.silk.append(dict(pts=[(x1, y1), (x2, y2)], w=w))

    def silk_poly(self, pts, w=0.15, closed=True):
        pts = list(pts) + ([pts[0]] if closed else [])
        for a, b in zip(pts[:-1], pts[1:]):
            self.silk_line(a[0], a[1], b[0], b[1], w)

    def silk_text(self, s, x, y, h=1.4, anchor="c", rot=0, w=0.15):
        for (a, b) in stroke_text(s, x, y, h, anchor, rot):
            self.silk_line(a[0], a[1], b[0], b[1], w)

    def body(self, kind, cx, cy, rot=0, label=""):
        self.bodies.append(dict(kind=kind, cx=cx, cy=cy, rot=rot, label=label))

    def pour_zone(self, net, layer="bot", inset=0.3):
        self.pour = dict(net=net, layer=layer, inset=inset)

    # ---- геометрия
    def outline_poly(self):
        c = self.corner
        return box(0, 0, self.W, self.H).buffer(-c).buffer(c, resolution=24)

    @staticmethod
    def pad_geom(p, exp=0.0):
        w, h = p["w"] + 2 * exp, p["h"] + 2 * exp
        if p["shape"] == "round":
            return Point(p["cx"], p["cy"]).buffer(w / 2, resolution=24)
        return box(p["cx"] - w / 2, p["cy"] - h / 2, p["cx"] + w / 2, p["cy"] + h / 2)

    @staticmethod
    def track_geom(t):
        return LineString(t["pts"]).buffer(t["w"] / 2, cap_style=1, join_style=1, resolution=12)

    def via_geom(self, v):
        return Point(v["cx"], v["cy"]).buffer(v["d"] / 2, resolution=16)

    def hole_geom(self, h):
        return Point(h["cx"], h["cy"]).buffer(h["d"] / 2, resolution=24)

    def pour_geom(self):
        if not self.pour:
            return None
        g = self.outline_poly().buffer(-self.pour["inset"])
        for h in self.holes:
            g = g.difference(self.hole_geom(h).buffer(0.5))
        # зазор до чужой меди на том же слое
        for v in self.vias:
            if v["net"] != self.pour["net"]:
                g = g.difference(self.via_geom(v).buffer(0.3))
        return g

    def layer_items(self, layer):
        """[(net, geom, kind, ref)] — вся медь слоя."""
        it = []
        for p in self.pads:
            if p["layer"] == layer:
                it.append((p["net"], self.pad_geom(p), "pad", f"{p['ref']}.{p['pin']}"))
        for t in self.tracks:
            if t["layer"] == layer:
                it.append((t["net"], self.track_geom(t), "track", t["net"]))
        for v in self.vias:
            it.append((v["net"], self.via_geom(v), "via", f"via@{v['cx']:.1f},{v['cy']:.1f}"))
        for i in self.islands:
            if i["layer"] == layer:
                it.append((i["net"], i["poly"], "island", i["net"]))
        if self.pour and self.pour["layer"] == layer:
            it.append((self.pour["net"], self.pour_geom(), "pour", self.pour["net"]))
        return it

    def layer_names(self):
        return ["top"] if self.layers == 1 else ["top", "bot"]

    # ---- проверки
    def check(self, min_clear=0.2, edge=0.3, mask_web=0.1, ring=0.13, verbose=True):
        msgs, errs = [], 0

        def err(m):
            nonlocal errs
            errs += 1
            msgs.append("ОШИБКА: " + m)

        def warn(m):
            msgs.append("ПРЕДУПРЕЖДЕНИЕ: " + m)

        outline = self.outline_poly()
        inner = outline.buffer(-edge)
        stats = {}
        for layer in self.layer_names():
            items = self.layer_items(layer)
            per_net = defaultdict(list)
            for net, g, kind, ref in items:
                per_net[net].append(g)
                if kind != "pour" and not inner.contains(g):
                    err(f"[{layer}] {kind} {ref} ближе {edge} мм к краю платы или вылезает за него")
            merged = {n: unary_union(gs) for n, gs in per_net.items()}
            names = sorted(merged)
            min_seen = 9e9
            for a, b in itertools.combinations(names, 2):
                d = merged[a].distance(merged[b])
                min_seen = min(min_seen, d)
                if d < min_clear - 1e-9:
                    kind = "КОРОТКОЕ ЗАМЫКАНИЕ" if d == 0 else f"зазор {d:.3f} мм < {min_clear}"
                    err(f"[{layer}] {kind} между цепями {a} и {b}")
            stats[layer] = dict(nets=len(names), min_clearance=None if min_seen > 1e8 else round(min_seen, 3))

        # связность цепей
        parent = {}

        def find(x):
            while parent.setdefault(x, x) != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            parent[find(a)] = find(b)

        comp = {}
        for layer in self.layer_names():
            per_net = defaultdict(list)
            for net, g, kind, ref in self.layer_items(layer):
                per_net[net].append((g, kind, ref))
            for net, lst in per_net.items():
                u = unary_union([g for g, _, _ in lst])
                parts = list(u.geoms) if hasattr(u, "geoms") else [u]
                for g, kind, ref in lst:
                    for i, part in enumerate(parts):
                        if part.buffer(1e-6).intersects(g):
                            comp[(layer, net, kind, ref, g.wkb_hex[:24])] = (layer, net, i)
                            union((layer, net, i), (layer, net, i))
                            break
        for v in self.vias:
            nodes = []
            for layer in self.layer_names():
                u = unary_union([g for n, g, k, r in self.layer_items(layer) if n == v["net"]])
                parts = list(u.geoms) if hasattr(u, "geoms") else [u]
                for i, part in enumerate(parts):
                    if part.buffer(1e-6).intersects(self.via_geom(v)):
                        nodes.append((layer, v["net"], i))
                        break
            for a, b in zip(nodes[:-1], nodes[1:]):
                union(a, b)
        pad_nodes = defaultdict(set)
        for p in self.pads:
            u = unary_union([g for n, g, k, r in self.layer_items(p["layer"]) if n == p["net"]])
            parts = list(u.geoms) if hasattr(u, "geoms") else [u]
            for i, part in enumerate(parts):
                if part.buffer(1e-6).intersects(self.pad_geom(p)):
                    pad_nodes[p["net"]].add((find((p["layer"], p["net"], i)), f"{p['ref']}.{p['pin']}"))
                    break
        connected = {}
        for net, s in pad_nodes.items():
            if net.startswith("NC_"):
                continue
            groups = defaultdict(list)
            for root, name in s:
                groups[root].append(name)
            connected[net] = len(groups) == 1
            if len(groups) > 1:
                err(f"цепь {net} разорвана: " + " | ".join(",".join(sorted(v)) for v in groups.values()))

        # переходные отверстия
        for v in self.vias:
            if (v["d"] - v["drill"]) / 2 < ring - 1e-9:
                err(f"кольцо перехода {(v['d'] - v['drill']) / 2:.2f} мм < {ring}")
        # отверстия: расстояние до чужой меди
        for h in self.holes:
            hg = self.hole_geom(h)
            for layer in self.layer_names():
                for net, g, kind, ref in self.layer_items(layer):
                    if kind != "pour" and hg.distance(g) < 0.3:
                        err(f"монтажное отверстие ({h['cx']},{h['cy']}) ближе 0.3 мм к {kind} {ref}")
        # маска
        opens = [(f"{p['ref']}.{p['pin']}", self.pad_geom(p, self.mask_exp)) for p in self.pads if p["mask"]]
        for (n1, g1), (n2, g2) in itertools.combinations(opens, 2):
            if g1.distance(g2) < mask_web - 1e-9 and not g1.intersects(g2):
                warn(f"перемычка маски {g1.distance(g2):.3f} мм между {n1} и {n2}")
        # шёлк на открытых площадках
        silk_g = [LineString(s["pts"]).buffer(s["w"] / 2) for s in self.silk]
        bad = 0
        for sg in silk_g:
            for n, og in opens:
                if sg.intersects(og):
                    bad += 1
                    break
        if bad:
            warn(f"{bad} штрихов шёлкографии пересекают открытые площадки (фабрика их обрежет)")
        for sg in silk_g:
            if not outline.buffer(-0.1).contains(sg):
                warn("шёлкография у самого края платы"); break
        if verbose:
            print(f"== {self.name}: слои {self.layer_names()} ==")
            for m in msgs:
                print(m)
            print("зазоры/цепи:", stats)
            print("цепи соединены:", {k: v for k, v in connected.items()})
            print("ИТОГ:", "ошибок нет" if errs == 0 else f"{errs} ошибок")
        return errs, msgs, stats

    # ---- Gerber
    def export_gerber(self, outdir, jlc_name=None):
        from gerbonara import graphic_objects as go, apertures as ap, rs274x, excellon, layers
        from gerbonara.utils import MM

        name = jlc_name or self.name
        H = self.H

        def fy(y):
            return H - y

        def poly_pts(poly):
            return [(x, fy(y)) for x, y in list(poly.exterior.coords)[:-1]]

        def circ(d):
            return ap.CircleAperture(d, unit=MM)

        def rect(w, h):
            return ap.RectangleAperture(w, h, unit=MM)

        def add_geom(objs, g, polarity_dark=True):
            for part in (g.geoms if hasattr(g, "geoms") else [g]):
                if part.is_empty or part.geom_type != "Polygon":
                    continue
                objs.append(go.Region(poly_pts(part), polarity_dark=polarity_dark, unit=MM))
                for hole in part.interiors:
                    pts = [(x, fy(y)) for x, y in list(hole.coords)[:-1]]
                    objs.append(go.Region(pts, polarity_dark=False, unit=MM))

        gl = {}
        for layer in self.layer_names():
            objs = []
            pour_g = None
            for net, g, kind, ref in self.layer_items(layer):
                if kind == "pour":
                    pour_g = g
            if pour_g is not None:
                add_geom(objs, pour_g)
                for h in self.holes:  # зазор вокруг монтажных отверстий уже вычтен из пролива
                    pass
            for p in self.pads:
                if p["layer"] == layer:
                    ap_ = circ(p["w"]) if p["shape"] == "round" else rect(p["w"], p["h"])
                    objs.append(go.Flash(p["cx"], fy(p["cy"]), ap_, unit=MM))
            for t in self.tracks:
                if t["layer"] == layer:
                    a = circ(t["w"])
                    for (x1, y1), (x2, y2) in zip(t["pts"][:-1], t["pts"][1:]):
                        objs.append(go.Line(x1, fy(y1), x2, fy(y2), a, unit=MM))
            for i in self.islands:
                if i["layer"] == layer:
                    add_geom(objs, i["poly"])
            for v in self.vias:
                objs.append(go.Flash(v["cx"], fy(v["cy"]), circ(v["d"]), unit=MM))
            side = "top" if layer == "top" else "bottom"
            gl[(side, "copper")] = rs274x.GerberFile(objects=objs)
            # маска: открытия только площадок этого слоя
            mobjs = []
            for p in self.pads:
                if p["layer"] == layer and p["mask"]:
                    w, h = p["w"] + 2 * self.mask_exp, p["h"] + 2 * self.mask_exp
                    ap_ = circ(w) if p["shape"] == "round" else rect(w, h)
                    mobjs.append(go.Flash(p["cx"], fy(p["cy"]), ap_, unit=MM))
            gl[(side, "mask")] = rs274x.GerberFile(objects=mobjs)
        # шёлк (верх)
        sobjs = []
        for s in self.silk:
            a = circ(s["w"])
            (x1, y1), (x2, y2) = s["pts"]
            sobjs.append(go.Line(x1, fy(y1), x2, fy(y2), a, unit=MM))
        gl[("top", "silk")] = rs274x.GerberFile(objects=sobjs)
        # контур
        oo = []
        a = circ(0.1)
        pts = list(self.outline_poly().exterior.coords)
        for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
            oo.append(go.Line(x1, fy(y1), x2, fy(y2), a, unit=MM))
        gl[("mechanical", "outline")] = rs274x.GerberFile(objects=oo)
        # сверловка
        pth = None
        if self.vias:
            tools = {}
            ex = []
            for v in self.vias:
                t = tools.setdefault(v["drill"], ap.ExcellonTool(v["drill"], plated=True, unit=MM))
                ex.append(go.Flash(v["cx"], fy(v["cy"]), t, unit=MM))
            pth = excellon.ExcellonFile(objects=ex)
        npth = None
        if self.holes:
            tools = {}
            ex = []
            for h in self.holes:
                t = tools.setdefault(h["d"], ap.ExcellonTool(h["d"], plated=False, unit=MM))
                ex.append(go.Flash(h["cx"], fy(h["cy"]), t, unit=MM))
            npth = excellon.ExcellonFile(objects=ex)
        st = layers.LayerStack(graphic_layers=gl, drill_pth=pth, drill_npth=npth, board_name=name)
        os.makedirs(outdir, exist_ok=True)
        st.save_to_directory(outdir, naming_scheme=layers.NamingScheme.altium, overwrite_existing=True)
        return sorted(os.listdir(outdir))
