"""Read the raw file, fix its known faults, place every town in a modern country and region, and write
data/outbreaks.csv (one row per town and year) and data/towns.csv (one row per town).

Fixes, all checked by asserts:
  1. Lat_WGS84 and Lon_WGS84 are swapped in the file. Checked against the ETRS89 LAEA (EPSG:3035) coordinates, which
     are correct: projecting (Lat_WGS84 as longitude, Lon_WGS84 as latitude) reproduces X and Y to within 2 m.
  2. Two Eisleben rows have an unquoted comma in the name ("Eisleben, Lutherstadt"), so the line has one field too few:
     X is present, Y and the latitude are missing, and the year sits in the latitude column. The year is recovered and the
     latitude solved from X and the longitude.
  3. One Sevilla row has the year 9999 (a missing value code). It is dropped.
  4. A few place names were geocoded to the wrong place (Prag, Milan, Noja, Gratz) and are moved; PAISLEY is merged
     with Paisley and Besanèon renamed Besançon (see FIX, MERGE and RENAME in common.py).
  5. 80 rows repeat a town and year already listed (28 of them London). An outbreak here is a town-year, so they are merged.
"""
import csv
from collections import defaultdict
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from common import *

fwd = Transformer.from_crs(4326, 3035, always_xy=True)

rows, bad = [], []
with open(RAW, encoding="latin-1", newline="") as f:
    lines = f.read().splitlines()
assert lines[0] == "Location,X_Coord_ERTS89,Y_Coord_ERTS89,Year_of_Outbreak,Lat_WGS84,Lon_WGS84", lines[0]
n_raw = len(lines) - 1
assert n_raw == 6929
fixes = {"eisleben": 0, "year9999": 0}
for ln in lines[1:]:
    p = ln.split(",")
    if p[0] == "Eisleben" and p[1] == " Lutherstadt":
        # name, X, (Y lost), "2"?, year, lon : the file has Eisleben, Lutherstadt,4428620,2,<year>,11.550853
        x, year, lon = float(p[2]), int(p[4]), float(p[5])
        # solve latitude so that the projected X matches
        lo, hi = 45.0, 60.0
        for _ in range(60):
            mid = (lo + hi) / 2
            X = fwd.transform(lon, mid)[0]
            # in LAEA centred at 10E, 52N, X decreases northward for lon > 10E
            if X > x: lo = mid
            else: hi = mid
        lat = (lo + hi) / 2
        assert abs(fwd.transform(lon, lat)[0] - x) < 5 and 51.4 < lat < 51.6, lat
        rows.append({"loc": "Eisleben", "year": year, "lat": lat, "lon": lon, "x": x, "y": round(fwd.transform(lon, lat)[1])})
        fixes["eisleben"] += 1
        continue
    assert len(p) == 6, ln
    loc, x, y, year, a, b = p[0], float(p[1]), float(p[2]), int(p[3]), float(p[4]), float(p[5])
    if year == 9999:
        fixes["year9999"] += 1; bad.append(ln); continue
    lon, lat = a, b                       # the swap
    X, Y = fwd.transform(lon, lat)
    assert abs(X - x) < 3 and abs(Y - y) < 3, (ln, X, Y)
    loc = MERGE.get(loc, RENAME.get(loc, loc))
    rows.append({"loc": loc, "year": year, "lat": lat, "lon": lon, "x": x, "y": y})
assert fixes == {"eisleben": 2, "year9999": 1}, fixes
assert len(rows) == n_raw - 1
coruna = [r for r in rows if r["loc"] == "A Coruña"][0]
assert abs(coruna["lat"] - 43.3709) < .001 and abs(coruna["lon"] + 8.3958) < .001

# merge repeated town-years
seen = {}
for r in rows:
    k = (r["loc"], r["year"])
    seen.setdefault(k, r)
n_dupe = len(rows) - len(seen)
ty = list(seen.values())
years = [r["year"] for r in ty]
assert min(years) == 1347 and max(years) == 1900

# towns: name -> point (each name has exactly one point after the Eisleben fix)
pts = defaultdict(set)
for r in ty:
    pts[r["loc"]].add((round(r["lat"], 6), round(r["lon"], 6)))
multi = {k: v for k, v in pts.items() if len(v) > 1}
assert not multi, multi

# countries: Natural Earth 10m, point in polygon, else nearest within 25 km (coastal towns)
NE = jload(NE10)["features"]
geoms, isos, names = [], [], []
for f in NE:
    p = f["properties"]
    iso = p["ADM0_A3"]
    iso = {"SAH": "MAR", "KOS": "KOS", "SDS": "SSD", "PSX": "PSE", "CYN": "CYP", "SOL": "SOM"}.get(iso, iso)
    geoms.append(shape(f["geometry"])); isos.append(iso); names.append(p["NAME_EN"] if p.get("NAME_EN") else p["NAME"])
tree = STRtree(geoms)
CNAME = {}
for i, n in zip(isos, names):
    CNAME.setdefault(i, n)
CNAME.update({"GBR": "United Kingdom", "CZE": "Czech Republic", "PSE": "Palestine", "KOS": "Kosovo", "CYP": "Cyprus"})


def country(lat, lon):
    pt = Point(lon, lat)
    for j in tree.query(pt):
        if geoms[j].contains(pt):
            return isos[j], 0.0
    j = tree.nearest(pt)
    d = geoms[j].distance(pt) * 111.0
    return isos[j], d


T = {}
far = []
for name, s in pts.items():
    lat, lon = list(s)[0]
    src = (lat, lon)
    if name in FIX:
        lat, lon = FIX[name][0], FIX[name][1]
    iso, d = country(lat, lon)
    if d > 0:
        far.append((name, iso, round(d, 1)))
    assert d < 25, (name, iso, d)
    assert iso in REGION_OF, (name, iso)
    T[name] = {"name": name, "en": ALIAS.get(name, "") if ALIAS.get(name) != name else "", "lat": lat, "lon": lon, "src": src, "fix": FIX.get(name, (0, 0, ""))[2], "iso": iso, "country": CNAME[iso], "region": REGION_OF[iso]}
print("towns placed by nearest country (km):", far[:20], len(far))

ty.sort(key=lambda r: (r["loc"], r["year"]))
by_town = defaultdict(list)
for r in ty:
    by_town[r["loc"]].append(r["year"])
with open(f"{DATA}/outbreaks.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["town", "town_english", "year", "country_iso3", "country", "region", "lat", "lon", "etrs89_laea_x", "etrs89_laea_y"])
    for r in ty:
        t = T[r["loc"]]
        w.writerow([r["loc"], t["en"], r["year"], t["iso"], t["country"], REGION_NAME[t["region"]], f"{t['lat']:.6f}", f"{t['lon']:.6f}", int(r["x"]), int(r["y"])])
with open(f"{DATA}/towns.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["town", "town_english", "country_iso3", "country", "region", "lat", "lon", "source_lat", "source_lon", "correction", "n_outbreak_years", "first_year", "last_year", "years"])
    for name in sorted(T):
        t, ys = T[name], by_town[name]
        w.writerow([name, t["en"], t["iso"], t["country"], REGION_NAME[t["region"]], f"{t['lat']:.6f}", f"{t['lon']:.6f}", f"{t['src'][0]:.6f}", f"{t['src'][1]:.6f}", t["fix"], len(ys), min(ys), max(ys), " ".join(map(str, ys))])
jsave({"towns": T, "by_town": by_town, "cname": CNAME,
       "clean": {"n_raw": n_raw, "n_rows_kept": len(rows), "n_dupe": n_dupe, "n_town_years": len(ty), "n_towns": len(T),
                 "dropped_9999": fixes["year9999"], "eisleben_fixed": fixes["eisleben"], "n_nearest": len(far),
                 "n_fixed": len(FIX), "n_merged": len(MERGE), "n_renamed": len(RENAME), "london_dupes": sum(1 for r in rows if r["loc"] == "London") - len(by_town["London"])}},
      f"{WORK}/clean.json")
print("raw", n_raw, "kept", len(rows), "dupes merged", n_dupe, "town-years", len(ty), "towns", len(T))
