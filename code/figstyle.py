"""House style for static figures: fonts (a static Fraunces Black cut from the variable font, written to memory),
colours, and Natural Earth outlines in the ETRS89 Lambert azimuthal equal-area projection (EPSG:3035)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape, box
from common import *

FONTS = "/home/claude/ref/fonts"
FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": 900, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-Black.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Regular.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Medium.ttf")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#6B6158", "axes.labelcolor": "#231D19",
                     "xtick.color": "#6B6158", "ytick.color": "#6B6158"})
BG, FG, MUT, LAND, RULE, HOT, COOL = "#F7F2E7", "#231D19", "#6B6158", "#E6DDC9", "#E2D8C4", "#A3241B", "#3E5FB8"
SEA = "#F7F2E7"
WAVEC = {1347: "#5A0A0E", 1348: "#A3241B", 1349: "#E0682F", 1350: "#EBA542", 1351: "#C8B65A", 1352: "#8FA88A", 1353: "#5F8A9A"}
LBINS = [(1347, 1499, "before 1500"), (1500, 1599, "1500s"), (1600, 1649, "1600 to 1649"), (1650, 1699, "1650 to 1699"),
         (1700, 1749, "1700 to 1749"), (1750, 1799, "1750 to 1799"), (1800, 1900, "1800 or later")]
LCOL = ["#2F4B7C", "#4D78A8", "#88A9C9", "#E6C36A", "#E58E3A", "#C4421F", "#7A0F12"]
lastcol = lambda y: LCOL[[i for i, b in enumerate(LBINS) if b[0] <= y <= b[1]][0]]
tr = Transformer.from_crs(4326, 3035, always_xy=True)
EXT = (2.45e6, 6.75e6, 0.85e6, 4.75e6)        # x0, x1, y0, y1 in EPSG:3035: Ireland to the Levant, Cairo to the Baltic

_SH = []
for f in jload(NE50)["features"]:
    g = shape(f["geometry"]).intersection(box(-30, 18, 70, 75))
    if g.is_empty:
        continue
    polys = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
    rings = []
    for p in polys:
        if p.geom_type != "Polygon":
            continue
        a = np.array(p.exterior.coords)
        x, y = tr.transform(a[:, 0], a[:, 1])
        rings.append(np.column_stack([x, y]))
    _SH.append((f["properties"]["ADM0_A3"], rings))


def basemap(ax, colour_of=lambda iso: None, ext=EXT, lw=.35, ec="#FFFFFF", land=LAND):
    for iso, rings in _SH:
        c = colour_of(iso) or land
        for r in rings:
            ax.add_patch(MPoly(r, closed=True, fc=c, ec=ec, lw=lw, zorder=1))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")


def xy(lon, lat):
    return tr.transform(np.asarray(lon), np.asarray(lat))


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
