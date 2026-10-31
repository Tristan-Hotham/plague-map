"""r/dataisbeautiful collage for plague-map: 2400 x 3000 px on a light background. Numbers from data/results.json."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
from matplotlib.patches import Patch

R = jload(f"{DATA}/results.json")
C = jload(f"{WORK}/clean.json")
T, BY = C["towns"], {k: sorted(v) for k, v in C["by_town"].items()}
names = sorted(T)
X, Y = xy([T[n]["lon"] for n in names], [T[n]["lat"] for n in names])
LAST = np.array([BY[n][-1] for n in names])
BGc = "#F6F1E6"; LANDC = "#E4DBC7"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGc)
fig.text(.045, .968, "Five centuries of plague", fontproperties=DISP, fontsize=58, color=FG, va="top")
fig.text(.045, .9, f"{R['span']['n_town_years']:,} years with plague recorded in {R['span']['n_towns']:,} towns across Europe and the Mediterranean,\n1347 to 1900. Each town is coloured by the last year plague was recorded there.",
         fontproperties=SERP, fontsize=16, color=FG, va="top", linespacing=1.4)

# hero map: last recorded outbreak
ax = fig.add_axes([0, .445, 1, .4])
ext = (2.55e6, 6.65e6, 0.95e6, 4.45e6)
basemap(ax, ext=ext, lw=.35, ec=BGc, land=LANDC)
o = np.argsort(LAST)
ax.scatter(X[o], Y[o], s=13, c=[lastcol(v) for v in LAST[o]], ec="white", lw=.3, zorder=3)
CALL = [("London", "London 1665 to 1667:\nthe Great Plague", (3.2, 56.6), "left"),
        ("Marseille", "Marseille 1720 to 1722", (4.3, 40.9), "center"),
        ("Messina", "Messina 1743", (14.6, 34.7), "center"),
        ("Noja", "Noicattaro\n1815 to 1816", (15.9, 43.1), "center"),
        ("Izmir", "Izmir 1837", (22.2, 35.4), "center"),
        ("Kairo", "Cairo 1841", (30.2, 34.0), "center"),
        ("Porto", "Porto 1899 to 1900:\nthe third pandemic", (-17.2, 43.3), "left")]
for n, txt, (lx, ly), ha in CALL:
    x0, y0 = xy(T[n]["lon"], T[n]["lat"]); x1, y1 = xy(lx, ly)
    ax.annotate(txt, xy=(x0, y0), xytext=(x1, y1), fontsize=10.5, color=FG, ha=ha, va="center", family=MONO, zorder=6,
                arrowprops=dict(arrowstyle="-", color=FG, lw=.7, shrinkA=2, shrinkB=2),
                bbox=dict(boxstyle="round,pad=.25", fc=BGc, ec="none", alpha=.95))
    ax.scatter([x0], [y0], s=46, fc="none", ec=FG, lw=1.1, zorder=7)
leg = [Patch(fc=c, label=b[2]) for c, b in zip(LCOL, LBINS)]
fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(.035, .44), ncol=7, frameon=False, fontsize=10.6, handlelength=1.1,
           columnspacing=1.0, title="Last recorded outbreak in each town", title_fontsize=11.5, alignment="left")

# big numbers
w, rc, lm = R["wave"], R["recur"], R["landmarks"]
reg = {r["k"]: r for r in R["regions"]}
nums = [(f"{R['year_1348']}", "#A3241B", f"towns with plague in 1348,\nthe Black Death's first\nfull year"),
        (f"{rc['median']:.0f} yrs", "#B88400", f"median gap before plague\nreturned to the same town\n({rc['n_intervals']:,} gaps)"),
        (f"{lm['london_n']}", "#3E5FB8", f"years with plague in\nLondon, {lm['london_first']} to {lm['london_last']}:\nthe most of any town"),
        (f"{R['gap_otto_brit']} yrs", "#9B2D6F", f"after Britain ({reg['brit']['last_wide']}), plague\nwas still widespread in\nthe Ottoman east ({reg['otto']['last_wide']})")]
for i, (big, col, small) in enumerate(nums):
    x = .045 + i * .235
    fig.text(x, .375, big, fontproperties=DISP, fontsize=42, color=col, va="top")
    fig.text(x, .325, small, family=MONO, fontsize=11, color=FG, va="top", linespacing=1.45)

# small multiples by period
P = [(1347, 1353), (1354, 1399), (1400, 1449), (1450, 1499), (1500, 1549), (1550, 1599), (1600, 1649), (1650, 1699), (1700, 1749), (1750, 1799), (1800, 1849), (1850, 1900)]
sx = (2.6e6, 6.6e6, 0.95e6, 4.3e6)
for i, (a, b) in enumerate(P):
    r, c = divmod(i, 6)
    axp = fig.add_axes([.02 + c * .161, .168 - r * .074, .155, .066])
    basemap(axp, ext=sx, lw=.15, ec=BGc, land=LANDC)
    m = np.array([any(a <= y <= b for y in BY[n]) for n in names])
    axp.scatter(X[m], Y[m], s=1.6, c="#A3241B", lw=0, zorder=3)
    assert R["periods"][i]["a"] == a and R["periods"][i]["towns"] == int(m.sum())
    axp.text(0.03, 0.97, f"{a} to {b}", transform=axp.transAxes, family=MONO, fontsize=10.5, color=FG, va="top", zorder=8,
             bbox=dict(boxstyle="square,pad=.1", fc=BGc, ec="none", alpha=.85))
    axp.text(0.03, 0.03, f"{R['periods'][i]['towns']} towns", transform=axp.transAxes, fontsize=8.5, color=MUT, family=MONO)
fig.text(.045, .258, "Towns with plague recorded, by period", family=MONO, fontsize=12, color=FG, va="top")
fig.text(.045, .022, "Source: Büntgen, Ginzler, Esper, Tegel and McMichael (2012), Digitizing historical plague, EnviDat doi:10.16904/envidat.181 (ODbL),\n"
         "a digitisation of Biraben (1975 to 1976). Records are outbreak years, not deaths, and follow surviving documents: France holds\n"
         f"{R['cover']['top_pct']:.0f}% of them and Moscow, Constantinople and most of the Balkans are missing. Outlines: Natural Earth.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib  ·  maps.tristanhotham.com/plague-map", family=MONO, fontsize=9.1, color=MUT, linespacing=1.45, va="bottom")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "five_centuries_of_plague.png")
fig.savefig(out, facecolor=BGc, dpi=200)
print("ok", out)

# post text, numbers from results.json
rg = {r["k"]: r for r in R["regions"]}
post = f"""## Title

[OC] Five centuries of plague: {R['span']['n_town_years']:,} outbreak years in {R['span']['n_towns']:,} European and Mediterranean towns, 1347 to 1900. Plague returned to the same town every {R['recur']['median']:.0f} years (median), and left Britain {R['gap_otto_brit']} years before the Ottoman east

## Body

I mapped a digitised copy of Jean-Noël Biraben's inventory of plague outbreaks: every town and year with plague recorded, from Messina in 1347 to Porto in 1900. The Black Death was recorded in {R['year_1348']} towns in 1348 alone, but the busiest decade is actually the {R['decade_peak']['d']}s ({R['decade_peak']['n']} town-years). London has the most plague years ({R['landmarks']['london_n']}). Using the last year with plague in three or more towns, it left Italy in {rg['ita']['last_wide']}, Britain in {rg['brit']['last_wide']} and France in {rg['fra']['last_wide']}, but lasted to {rg['otto']['last_wide']} in Anatolia, the Levant and Egypt. Caveat: this is a map of surviving documents. France holds {R['cover']['top_pct']:.0f}% of the records, Moscow and Constantinople are missing, and it counts outbreak years, not deaths. Interactive version with a play button: https://maps.tristanhotham.com/plague-map/

## Source comment

Source: Büntgen U, Ginzler C, Esper J, Tegel W, McMichael AJ (2012) Digitizing historical plague, Clinical Infectious Diseases 55(11); dataset on EnviDat, doi:10.16904/envidat.181 (ODbL), a digitisation of Biraben J-N (1975 to 1976) Les hommes et la peste. I repaired the file (swapped latitude and longitude columns, a broken row, repeated rows, five mislocated towns). Outlines: Natural Earth.

Tools: Python (pandas, shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/plague-map/
Paper: {{https://doi.org/10.5281/zenodo.23844513}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/plague-map/}}
"""
check_dashes(post, "post")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.md"), "w", encoding="utf-8").write(post)
