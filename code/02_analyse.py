"""All analysis: results.json (every number quoted anywhere) and the derived tables in data/.
An outbreak is a town-year: a town with plague recorded in a year. Consecutive outbreak years in one town are joined
into an episode for the recurrence analysis."""
import csv, math, random
from collections import Counter, defaultdict
import numpy as np
from common import *

C = jload(f"{WORK}/clean.json")
T, BY, CN = C["towns"], {k: sorted(v) for k, v in C["by_town"].items()}, C["cname"]
TY = [(t, y) for t, ys in BY.items() for y in ys]
N = len(TY)
assert N == C["clean"]["n_town_years"]
R = {"meta": {"page": URL, "repo": REPO, "slug": SLUG}, "clean": C["clean"]}
years = [y for _, y in TY]
R["span"] = {"first": min(years), "last": max(years), "n_years_with": len(set(years)), "n_town_years": N, "n_towns": len(T),
             "n_countries": len({T[t]["iso"] for t in T})}
EN = lambda t: T[t]["en"] or t


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


# ---- regions and countries: shares, first, last
reg_n = Counter(T[t]["region"] for t, _ in TY)
R["regions"] = []
for k, name, isos, col in REGIONS:
    ty = sorted([(y, t) for t, ys in BY.items() if T[t]["region"] == k for y in ys])
    if not ty:
        continue
    yc = Counter(y for y, _ in ty)
    wide = [y for y, n in yc.items() if n >= 3]
    last_y = ty[-1][0]
    last_towns = sorted({EN(t) for y, t in ty if y == last_y})
    R["regions"].append({"k": k, "name": name, "col": col, "n": len(ty), "pct": 100 * len(ty) / N,
                         "towns": len({t for _, t in ty}), "first": ty[0][0], "last": last_y, "last_towns": last_towns,
                         "last_wide": max(wide), "last_wide_n": yc[max(wide)],
                         "p95": int(np.percentile([y for y, _ in ty], 95)), "median": int(np.median([y for y, _ in ty]))})
R["regions"].sort(key=lambda r: r["last_wide"])
RG = {r["k"]: r for r in R["regions"]}
R["countries"] = []
for iso in sorted({T[t]["iso"] for t in T}):
    ty = sorted([(y, t) for t, ys in BY.items() if T[t]["iso"] == iso for y in ys])
    yc = Counter(y for y, _ in ty)
    wide = [y for y, n in yc.items() if n >= 3]
    last_y = ty[-1][0]
    R["countries"].append({"iso": iso, "name": CN[iso], "region": T[[t for t in T if T[t]["iso"] == iso][0]]["region"], "n": len(ty),
                           "pct": 100 * len(ty) / N, "towns": len({t for _, t in ty}), "first": ty[0][0], "last": last_y,
                           "last_towns": sorted({EN(t) for y, t in ty if y == last_y}), "last_wide": max(wide) if wide else None})
R["countries"].sort(key=lambda c: c["last"])
CC = {c["iso"]: c for c in R["countries"]}
R["n_countries"] = len(R["countries"])
top4 = sorted(R["countries"], key=lambda c: -c["n"])[:4]
R["cover"] = {"top_country": top4[0]["name"], "top_pct": top4[0]["pct"], "top4_names": [c["name"] for c in top4],
              "top4_pct": sum(c["pct"] for c in top4), "fra_gbr_pct": CC["FRA"]["pct"] + CC["GBR"]["pct"],
              "fra_n": CC["FRA"]["n"], "gbr_n": CC["GBR"]["n"]}

# ---- landmark epidemics (checked against the data)
def has(town, y):
    return y in BY.get(town, [])
for town, y in (("London", 1665), ("London", 1666), ("Marseille", 1720), ("Marseille", 1721), ("Messina", 1743), ("Wien", 1679),
                ("Prag", 1713), ("Porto", 1899), ("Messina", 1347), ("Noja", 1815), ("Manacor", 1819), ("Kairo", 1841), ("Beyrouth", 1859)):
    assert has(town, y), (town, y)
assert not any(norm(t).startswith(("moskva", "moscow", "istanbul", "constantinople", "konstantinopel")) for t in T)
R["landmarks"] = {"london_last": max(BY["London"]), "london_n": len(BY["London"]), "london_first": min(BY["London"]),
                  "marseille_n": len(BY["Marseille"]), "marseille_1720s": [y for y in BY["Marseille"] if 1720 <= y <= 1722],
                  "marseille_last": max(BY["Marseille"]), "messina_last": max(BY["Messina"]),
                  "eyam": "Eyam" in BY, "eyam_years": BY.get("Eyam", []), "podolsk": BY.get("Podol'sk", []),
                  "n_russia": CC["RUS"]["n"], "porto": [y for y in BY["Porto"] if y >= 1800]}
y1665 = sorted(EN(t) for t, ys in BY.items() if 1665 in ys and T[t]["iso"] == "GBR")
R["landmarks"]["gbr_1665_n"] = len(y1665)
R["landmarks"]["gbr_1665_6_n"] = len({t for t, ys in BY.items() if (1665 in ys or 1666 in ys) and T[t]["iso"] == "GBR"})
R["landmarks"]["prov_1720_2_n"] = len({t for t, ys in BY.items() if any(1720 <= y <= 1722 for y in ys) and T[t]["iso"] == "FRA"})
R["landmarks"]["prov_1720_2"] = sorted({EN(t) for t, ys in BY.items() if any(1720 <= y <= 1722 for y in ys) and T[t]["iso"] == "FRA"})

# ---- towns with most outbreak years
top = sorted(T, key=lambda t: (-len(BY[t]), t))
R["top_towns"] = [{"town": t, "en": T[t]["en"], "n": len(BY[t]), "first": BY[t][0], "last": BY[t][-1], "country": CN[T[t]["iso"]]} for t in top[:20]]
R["towns_n1"] = sum(1 for t in T if len(BY[t]) == 1)
R["towns_n1_pct"] = 100 * R["towns_n1"] / len(T)
R["towns_ge20"] = sum(1 for t in T if len(BY[t]) >= 20)
R["top20_share"] = 100 * sum(len(BY[t]) for t in top[:20]) / N

# ---- decades and years
dec = Counter(y // 10 * 10 for y in years)
dtowns = defaultdict(set)
for t, y in TY:
    dtowns[y // 10 * 10].add(t)
dreg = defaultdict(Counter)
for t, y in TY:
    dreg[y // 10 * 10][T[t]["region"]] += 1
R["decades"] = [{"d": d, "n": dec.get(d, 0), "towns": len(dtowns.get(d, ())), "reg": dict(dreg[d])} for d in range(1340, 1901, 10)]
R["years"] = {str(y): yc_ for y, yc_ in sorted(Counter(years).items())}
pk = max(R["decades"], key=lambda r: r["n"])
R["decade_peak"] = pk
yc = Counter(years)
R["year_peak"] = {"y": max(yc, key=lambda y: (yc[y], -y)), "n": max(yc.values())}
R["year_1348"] = yc[1348]
by_cent = Counter((y - 1) // 100 + 1 for y in years)  # 14th century = 1301-1400
R["by_century"] = {str(k): by_cent[k] for k in sorted(by_cent)}
R["share_1500_1670"] = 100 * sum(1 for y in years if 1500 <= y <= 1669) / N
R["after_1670"] = sum(1 for y in years if y >= 1670)
R["after_1670_south_pct"] = 100 * sum(1 for t, y in TY if y >= 1720 and T[t]["region"] in ("magh", "otto")) / sum(1 for t, y in TY if y >= 1720)
R["after_1720_n"] = sum(1 for y in years if y >= 1720)
dec_mean_1600s = np.mean([dec[d] for d in range(1600, 1670, 10)])

# ---- the first wave, 1347 to 1353
W0, W1 = 1347, 1353
first = {t: BY[t][0] for t in T}
wave = {t: y for t, y in first.items() if W0 <= y <= W1}
MES = (T["Messina"]["lat"], T["Messina"]["lon"])
seeds = [t for t, y in wave.items() if y == 1347]
eur = {t: y for t, y in wave.items() if T[t]["region"] not in ("magh", "otto")}
rows = []
for t, y in sorted(wave.items(), key=lambda kv: (kv[1], kv[0])):
    p = (T[t]["lat"], T[t]["lon"])
    rows.append({"town": t, "en": T[t]["en"], "year": y, "region": T[t]["region"], "country": CN[T[t]["iso"]],
                 "km_messina": hav(MES, p), "km_seed": min(hav((T[s]["lat"], T[s]["lon"]), p) for s in seeds)})
wy = Counter(r["year"] for r in rows)
R["wave"] = {"n": len(rows), "n_eur": len(eur), "by_year": {str(y): wy.get(y, 0) for y in range(W0, W1 + 1)},
             "seeds": sorted(EN(s) for s in seeds), "n_seeds": len(seeds)}


def theil_sen(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    s = [(y[j] - y[i]) / (x[j] - x[i]) for i in range(len(x)) for j in range(i + 1, len(x)) if x[j] != x[i]]
    return float(np.median(s))


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    b = np.polyfit(x, y, 1)[0]
    return float(b)


E = [r for r in rows if r["region"] not in ("magh", "otto")]
xs, ym, ys = [r["year"] for r in E], [r["km_messina"] for r in E], [r["km_seed"] for r in E]
random.seed(1347)
boots = []
for _ in range(400):
    smp = [random.choice(E) for _ in E]
    boots.append(theil_sen([r["year"] for r in smp], [r["km_seed"] for r in smp]))
fronts = {}
for y in range(W0, W1 + 1):
    d = [r["km_messina"] for r in E if r["year"] <= y]
    fronts[str(y)] = {"p90": float(np.percentile(d, 90)), "max": float(max(d)), "median_new": float(np.median([r["km_messina"] for r in E if r["year"] == y])) if any(r["year"] == y for r in E) else None}
med = {y: np.median([r["km_messina"] for r in E if r["year"] == y]) for y in range(W0, 1351)}
R["wave"].update({
    "speed_ts_seed": theil_sen(xs, ys), "speed_ts_messina": theil_sen(xs, ym), "speed_ols_messina": ols(xs, ym),
    "speed_ci": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
    "front": fronts, "median_km": {str(k): float(v) for k, v in med.items()},
    "median_step_47_50": float((med[1350] - med[1347]) / 3),
    "front_p90_47_50": float((fronts["1350"]["p90"] - fronts["1347"]["p90"]) / 3),
    "far_1350": sorted([(EN(r["town"]), round(r["km_messina"])) for r in E if r["year"] == 1350], key=lambda x: -x[1])[:5],
    "first_gbr": min(r["year"] for r in E if r["country"] == "United Kingdom"),
    "first_deu": min(r["year"] for r in E if r["country"] == "Germany"),
    "first_pol": min(r["year"] for r in E if r["country"] == "Poland"),
    "first_baltic": min(r["year"] for r in E if r["region"] == "east"),
    "n_1348_south": sum(1 for r in rows if r["year"] == 1348 and r["region"] in ("magh", "otto")),
})
R["wave"]["speed_per_day_ts"] = R["wave"]["speed_ts_seed"] / 365.25
with open(f"{DATA}/black_death_first_wave.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["town", "town_english", "first_year", "country", "region", "km_from_messina", "km_from_nearest_1347_town"])
    for r in rows:
        w.writerow([r["town"], r["en"], r["year"], r["country"], REGION_NAME[r["region"]], round(r["km_messina"]), round(r["km_seed"])])

# ---- recurrence: episodes (runs of consecutive years) and intervals between episode starts
ep = {}
for t, ys in BY.items():
    e = []
    for y in ys:
        if e and y - e[-1][1] == 1:
            e[-1][1] = y
        else:
            e.append([y, y])
    ep[t] = e
iv = []      # (start of earlier episode, interval, town)
for t, e in ep.items():
    for a, b in zip(e, e[1:]):
        iv.append((a[0], b[0] - a[0], t))
ivs = [x[1] for x in iv]
ivc = lambda lo, hi: [i for s, i, _ in iv if lo <= s < hi]
R["recur"] = {"n_episodes": sum(len(e) for e in ep.values()), "n_intervals": len(iv), "median": float(np.median(ivs)),
              "q25": float(np.percentile(ivs, 25)), "q75": float(np.percentile(ivs, 75)),
              "le15_pct": 100 * sum(1 for i in ivs if i <= 15) / len(ivs),
              "mean_len": float(np.mean([b - a + 1 for e in ep.values() for a, b in e])),
              "multi_year_pct": 100 * sum(1 for e in ep.values() for a, b in e if b > a) / sum(len(e) for e in ep.values()),
              "by_century": {}, "hist": {}}
for c0 in (1300, 1400, 1500, 1600):
    x = ivc(c0, c0 + 100)
    R["recur"]["by_century"][str(c0)] = {"n": len(x), "median": float(np.median(x))}
h = Counter(min(i, 61) // 2 * 2 for i in ivs)
R["recur"]["hist"] = {str(k): h[k] for k in sorted(h)}
big = [t for t in T if len(ep[t]) >= 10]
R["recur"]["n_towns_10ep"] = len(big)
R["recur"]["median_town_10ep"] = float(np.median([np.median([b[0] - a[0] for a, b in zip(ep[t], ep[t][1:])]) for t in big]))
lon_iv = [b[0] - a[0] for a, b in zip(ep["London"], ep["London"][1:])]
R["recur"]["london_ep"] = len(ep["London"]); R["recur"]["london_median"] = float(np.median(lon_iv)); R["recur"]["london_max"] = max(lon_iv)
R["recur"]["london_longest_gap"] = [ep["London"][i][0] for i in range(len(lon_iv)) if lon_iv[i] == max(lon_iv)][0]
# Europe-wide plague years: years in which 20 or more towns record plague
wide = sorted(y for y, n in yc.items() if n >= 20)
R["recur"]["wide_years"] = wide
R["recur"]["n_wide_years"] = len(wide)
with open(f"{DATA}/recurrence_intervals.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["town", "episode_start", "next_episode_start", "interval_years"])
    for s, i, t in sorted(iv, key=lambda x: (x[2], x[0])):
        w.writerow([t, s, s + i, i])

# ---- tables
with open(f"{DATA}/outbreaks_by_decade.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["decade", "town_years", "towns"])
    for r in R["decades"]:
        w.writerow([r["d"], r["n"], r["towns"]])
with open(f"{DATA}/last_outbreak_by_country.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["country_iso3", "country", "region", "town_years", "towns", "first_year", "last_year", "last_towns", "last_year_with_3_or_more_towns"])
    for c in R["countries"]:
        w.writerow([c["iso"], c["name"], REGION_NAME[c["region"]], c["n"], c["towns"], c["first"], c["last"], "; ".join(c["last_towns"]), c["last_wide"] or ""])
with open(f"{DATA}/last_outbreak_by_region.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["region", "town_years", "towns", "first_year", "last_year", "last_towns", "last_year_with_3_or_more_towns", "towns_that_year", "year_by_which_95pct_recorded"])
    for r in R["regions"]:
        w.writerow([r["name"], r["n"], r["towns"], r["first"], r["last"], "; ".join(r["last_towns"]), r["last_wide"], r["last_wide_n"], r["p95"]])

# ---- periods for the collage small multiples, and the gap between the end in Britain and in the Ottoman east
PER = [(1347, 1353), (1354, 1399), (1400, 1449), (1450, 1499), (1500, 1549), (1550, 1599), (1600, 1649), (1650, 1699), (1700, 1749), (1750, 1799), (1800, 1849), (1850, 1900)]
R["periods"] = [{"a": a, "b": b, "towns": len({t for t, y in TY if a <= y <= b}), "n": sum(1 for _, y in TY if a <= y <= b)} for a, b in PER]
R["gap_otto_brit"] = RG["otto"]["last_wide"] - RG["brit"]["last_wide"]

# ---- facts checked here, used in the text
reg_order = [r["k"] for r in R["regions"]]
assert reg_order.index("brit") < reg_order.index("fra") and reg_order[-2:] in (["magh", "otto"], ["otto", "magh"]), reg_order
assert RG["brit"]["last"] == 1667 and RG["brit"]["last_wide"] in (1665, 1666, 1667)
assert R["landmarks"]["london_last"] == 1667
R["wave"]["speed_lo"] = min(R["wave"]["speed_ts_seed"], R["wave"]["speed_ols_messina"], R["wave"]["speed_ts_messina"])
R["wave"]["speed_hi"] = max(R["wave"]["speed_ts_seed"], R["wave"]["speed_ols_messina"], R["wave"]["speed_ts_messina"])
R["wave"]["day_lo"] = R["wave"]["speed_lo"] / 365.25
R["wave"]["day_hi"] = R["wave"]["speed_hi"] / 365.25
R["wave"]["max_1347"] = fronts["1347"]["max"]; R["wave"]["max_1348"] = fronts["1348"]["max"]
R["wave"]["far_1347"] = EN(max((r for r in E if r["year"] == 1347), key=lambda r: r["km_messina"])["town"])
R["wave"]["far_1348"] = EN(max((r for r in E if r["year"] == 1348), key=lambda r: r["km_messina"])["town"])
R["wave"]["p90_1347"] = fronts["1347"]["p90"]; R["wave"]["p90_1348"] = fronts["1348"]["p90"]
R["wave"]["share_by_1348"] = 100 * sum(1 for r in E if r["year"] <= 1348) / len(E)
R["wave"]["n_1351_on"] = sum(1 for r in rows if r["year"] >= 1351)
R["after_1667_pct"] = 100 * sum(1 for y in years if y > 1667) / N
R["peak_1620_1639"] = dec[1620] + dec[1630]
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("span", "cover", "decade_peak", "year_peak", "landmarks")}, indent=0, ensure_ascii=False)[:3000])
for r in R["regions"]:
    print(r["name"], r["n"], round(r["pct"], 1), r["first"], r["last"], r["last_towns"], "wide", r["last_wide"], r["last_wide_n"], "p95", r["p95"])
print({k: v for k, v in R["wave"].items() if k not in ("front",)})
print(R["wave"]["front"])
print({k: v for k, v in R["recur"].items() if k != "hist"})
print(R["top_towns"][:12])
