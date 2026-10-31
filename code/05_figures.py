"""Static figures: header.png (1200 x 630), paper figures (release/paper/f_*.png) and blog figures (release/blog/b_*.png).
All numbers from data/results.json and the cleaned town table."""
import shutil
from collections import Counter
from figstyle import *

R = jload(f"{DATA}/results.json")
C = jload(f"{WORK}/clean.json")
T, BY = C["towns"], {k: sorted(v) for k, v in C["by_town"].items()}
PAP = os.path.join(ROOT, "release", "paper"); BLG = os.path.join(ROOT, "release", "blog")
os.makedirs(PAP, exist_ok=True); os.makedirs(BLG, exist_ok=True)
names = sorted(T)
LON = np.array([T[n]["lon"] for n in names]); LAT = np.array([T[n]["lat"] for n in names])
X, Y = xy(LON, LAT)
NY = np.array([len(BY[n]) for n in names]); FIRST = np.array([BY[n][0] for n in names]); LAST = np.array([BY[n][-1] for n in names])
REGC = {k: c for k, _, _, c in REGIONS}
EN = lambda n: (T[n]["en"] or n).split(" (")[0]


def fig_wave_map(path):
    fig = plt.figure(figsize=(10, 8.4), facecolor=BG); ax = fig.add_axes([0, 0, 1, .93])
    basemap(ax)
    m = FIRST > 1353
    ax.scatter(X[m], Y[m], s=3, c="#B5AA98", lw=0, zorder=2)
    for y in sorted(WAVEC, reverse=True):
        k = FIRST == y
        if k.any():
            ax.scatter(X[k], Y[k], s=34, c=WAVEC[y], ec="white", lw=.6, zorder=3, label=f"{y}  ({k.sum()})")
    mx, my = xy(T["Messina"]["lon"], T["Messina"]["lat"])
    for r in (1000e3, 2000e3):
        ax.add_patch(plt.Circle((mx, my), r, fill=False, ec=MUT, lw=.7, ls=(0, (3, 3)), zorder=2))
    for r, t, a in ((1000e3, "1,000 km from Messina", -28), (2000e3, "2,000 km", 38)):
        ax.text(mx + r * np.cos(np.radians(a)) + 3e4, my + r * np.sin(np.radians(a)), t, fontsize=9, color=MUT, ha="left", va="center", zorder=5, bbox=dict(boxstyle="round,pad=.1", fc=BG, ec="none", alpha=.8))
    ax.legend(loc="upper left", frameon=False, title="First recorded", title_fontsize=11, fontsize=11, bbox_to_anchor=(.0, .97))
    fig.text(.03, .955, "The Black Death's first wave: each town coloured by its first recorded year", fontsize=12.5, color=FG)
    save(fig, path)


def fig_wave_distance(path):
    fig, ax = plt.subplots(figsize=(10, 5.4), facecolor=BG); ax.set_facecolor(BG)
    import csv
    rows = list(csv.reader(open(f"{DATA}/black_death_first_wave.csv", encoding="utf-8")))[1:]
    rng = np.random.default_rng(7)
    for r in rows:
        y, km = int(r[2]), float(r[5])
        ax.scatter(y + rng.uniform(-.3, .3), km, s=26, c=WAVEC[y], ec="white", lw=.5, zorder=3)
    ax.set_xticks(range(1347, 1353)); ax.set_ylabel("km from Messina (straight line)")
    ax.set_ylim(-60, 2600); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    w = R["wave"]
    ax.text(1351.6, 2350, f"Fitted slopes: {w['speed_lo']:.0f} to {w['speed_hi']:.0f} km a year", ha="right", fontsize=10.5, color=FG)
    fig.tight_layout(); save(fig, path)


def fig_decades(path):
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=BG); ax.set_facecolor(BG)
    D = R["decades"]; bottom = np.zeros(len(D)); xs = np.array([d["d"] for d in D])
    for k, name, _, col in REGIONS:
        v = np.array([d["reg"].get(k, 0) for d in D])
        if v.sum():
            ax.bar(xs + 5, v, width=8.6, bottom=bottom, color=col, label=name, lw=0); bottom += v
    ax.set_xlim(1338, 1905); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True); ax.set_ylabel("town-years per decade")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, ncol=1, loc="upper right", bbox_to_anchor=(1, .97))
    fig.tight_layout(); save(fig, path)


def fig_top(path):
    fig, ax = plt.subplots(figsize=(9, 6.6), facecolor=BG); ax.set_facecolor(BG)
    tt = R["top_towns"][::-1]
    ax.barh(range(len(tt)), [t["n"] for t in tt], color=[REGC[T[t["town"]]["region"]] for t in tt], height=.72)
    ax.set_yticks(range(len(tt))); ax.set_yticklabels([f"{(t['en'] or t['town']).split(' (')[0]}, {t['country'].replace('United Kingdom', 'UK')}" for t in tt], fontsize=10.5)
    for i, t in enumerate(tt):
        ax.text(t["n"] + 1.2, i, f"{t['n']}  ({t['first']} to {t['last']})", va="center", fontsize=9.5, color=FG)
    ax.set_xlim(0, 175); ax.set_xlabel("years with plague recorded")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); save(fig, path)


def fig_intervals(path):
    fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=BG); ax.set_facecolor(BG)
    H = R["recur"]["hist"]; ks = sorted(int(k) for k in H)
    ax.bar([k + 1 for k in ks], [H[str(k)] for k in ks], width=1.75, color=["#9C8F80" if k >= 60 else "#C9784F" for k in ks], lw=0)
    ax.axvline(R["recur"]["median"], color=HOT, lw=1.6)
    ax.text(R["recur"]["median"] + .8, max(H.values()) * .93, f"median {R['recur']['median']:.0f} years", color=HOT, fontsize=10.5)
    ax.set_xticks([0, 10, 20, 30, 40, 50, 61]); ax.set_xticklabels(["0", "10", "20", "30", "40", "50", "60+"])
    ax.set_xlabel("years from the start of one episode to the start of the next, same town"); ax.set_ylabel("gaps")
    ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); save(fig, path)


def fig_end(path):
    rows = R["regions"]
    fig, ax = plt.subplots(figsize=(10, 4.8), facecolor=BG); ax.set_facecolor(BG)
    for i, r in enumerate(rows[::-1]):
        ax.plot([r["first"], r["last"]], [i, i], color=r["col"], lw=2.4, alpha=.5, solid_capstyle="butt")
        ax.scatter([r["p95"]], [i], marker="D", s=40, fc=BG, ec=r["col"], lw=1.5, zorder=3)
        ax.scatter([r["last"]], [i], s=46, fc=BG, ec=r["col"], lw=1.8, zorder=3)
        ax.scatter([r["last_wide"]], [i], s=120, c=r["col"], zorder=4)
        ax.text(r["last_wide"] + (-9 if r["last_wide"] > 1800 else 9), i + .3, str(r["last_wide"]), fontsize=10, ha="right" if r["last_wide"] > 1800 else "left", color=FG, fontweight="medium")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r["name"] for r in rows[::-1]], fontsize=10.5)
    ax.set_xlim(1340, 1910); ax.grid(axis="x", color=RULE); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout(); save(fig, path)


def fig_last_map(path, title=True):
    fig = plt.figure(figsize=(10, 8.4), facecolor=BG); ax = fig.add_axes([0, 0, 1, .93])
    basemap(ax)
    o = np.argsort(LAST)
    ax.scatter(X[o], Y[o], s=16, c=[lastcol(v) for v in LAST[o]], ec="white", lw=.35, zorder=3)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=c, label=b[2]) for c, b in zip(LCOL, LBINS)], loc="upper left", bbox_to_anchor=(0, .97), frameon=False, fontsize=10.5, title="Last recorded outbreak", title_fontsize=11)
    if title:
        fig.text(.03, .955, "When each town last recorded plague", fontsize=12.5, color=FG)
    save(fig, path)


def fig_often_map(path):
    fig = plt.figure(figsize=(10, 8.4), facecolor=BG); ax = fig.add_axes([0, 0, 1, .93])
    basemap(ax)
    o = np.argsort(-NY)
    ax.scatter(X[o], Y[o], s=NY[o] * 2.2 + 3, c=[REGC[T[names[i]]["region"]] for i in o], ec="white", lw=.4, alpha=.85, zorder=3)
    for n in ("London", "Alger", "Paris", "Toulouse", "Izmir", "Venezia", "Kairo", "Barcelona", "Gdansk"):
        x, y = xy(T[n]["lon"], T[n]["lat"])
        ax.text(x + 4e4, y + 4e4, f"{EN(n)} {len(BY[n])}", fontsize=9.5, color=FG, zorder=5,
                bbox=dict(boxstyle="round,pad=.15", fc=BG, ec="none", alpha=.8))
    fig.text(.03, .955, "Years with plague recorded in each town, 1347 to 1900 (dot area)", fontsize=12.5, color=FG)
    save(fig, path)


def fig_coverage(path):
    cs = sorted(R["countries"], key=lambda c: -c["n"])[:14][::-1]
    fig, ax = plt.subplots(figsize=(9, 5.6), facecolor=BG); ax.set_facecolor(BG)
    ax.barh(range(len(cs)), [c["n"] for c in cs], color=[REGC[c["region"]] for c in cs], height=.7)
    ax.set_yticks(range(len(cs))); ax.set_yticklabels([c["name"] for c in cs], fontsize=10.5)
    for i, c in enumerate(cs):
        ax.text(c["n"] + 25, i, f"{c['n']:,} ({c['pct']:.1f}%)", va="center", fontsize=9.5)
    ax.set_xlim(0, 3300); ax.set_xlabel("town-years in the inventory")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); save(fig, path)


def header():
    fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
    ax = fig.add_axes([.38, 0, .62, 1])
    ext = (2.55e6, 6.6e6, 1.05e6, 4.6e6)
    basemap(ax, ext=ext, lw=.3, ec=BG)
    o = np.argsort(-NY)
    ax.scatter(X[o], Y[o], s=NY[o] * 1.7 + 3, c=HOT, ec="white", lw=.35, alpha=.78, zorder=3)
    fig.text(.045, .79, "The", fontproperties=DISP, fontsize=60, color=FG, va="baseline")
    fig.text(.045, .645, "plague", fontproperties=DISP, fontsize=60, color=HOT, va="baseline")
    fig.text(.045, .50, "years", fontproperties=DISP, fontsize=60, color=FG, va="baseline")
    fig.text(.047, .40, f"{R['span']['n_town_years']:,} outbreak years in\n{R['span']['n_towns']:,} towns, 1347 to 1900.\nWhen plague came, came back\nand finally left.", fontproperties=SERP, fontsize=17, color=FG, va="top", linespacing=1.45)
    fig.text(.047, .06, "maps.tristanhotham.com/plague-map", family=MONO, fontsize=12, color=MUT)
    fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG)
    plt.close(fig)


FIGS = [("wave_map", fig_wave_map), ("wave_distance", fig_wave_distance), ("decades", fig_decades), ("top_towns", fig_top),
        ("intervals", fig_intervals), ("end_regions", fig_end), ("last_map", fig_last_map), ("often_map", fig_often_map), ("coverage", fig_coverage)]
for name, fn in FIGS:
    fn(os.path.join(PAP, f"f_{name}.png"))
    shutil.copy(os.path.join(PAP, f"f_{name}.png"), os.path.join(BLG, f"b_{name}.png"))
header()
from PIL import Image
assert Image.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
print("figures", sorted(os.listdir(PAP)))
