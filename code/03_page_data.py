"""Page data: data/page/towns.json (every town and its outbreak years), data/page/world.json (modern country outlines
for the map area, simplified), data/page/cities.json (modern city labels). Natural Earth, public domain."""
from shapely.geometry import shape, mapping, box
from common import *

C = jload(f"{WORK}/clean.json")
T, BY = C["towns"], C["by_town"]
RK = [r[0] for r in REGIONS]
towns = []
for name in sorted(T, key=lambda n: -len(BY[n])):
    t = T[name]
    towns.append([name, t["en"], round(t["lat"], 4), round(t["lon"], 4), t["iso"], RK.index(t["region"]), sorted(BY[name]), t["fix"]])
jsave(towns, f"{PAGE}/towns.json")

BB = box(-16, 24, 62, 66)
feats = []
for f in jload(NE50)["features"]:
    p = f["properties"]
    g = shape(f["geometry"])
    if not g.intersects(BB):
        continue
    g = g.intersection(BB).simplify(0.03, preserve_topology=True)
    if g.is_empty:
        continue
    iso = p["ADM0_A3"]
    gj = mapping(g)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 3), round(c[1], 3)]
    feats.append({"type": "Feature", "properties": {"iso": iso, "n": p.get("NAME_EN") or p["NAME"]}, "geometry": {"type": gj["type"], "coordinates": rnd(gj["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{PAGE}/world.json")

cities = []
for f in jload(PLACES)["features"]:
    p = f["properties"]
    lon, lat = f["geometry"]["coordinates"]
    if -14 <= lon <= 50 and 26 <= lat <= 64 and (p.get("pop_max") or 0) >= 150000:
        cities.append({"name": p["name"], "lat": round(lat, 3), "lon": round(lon, 3), "pop": int(p["pop_max"])})
cities.sort(key=lambda c: -c["pop"])
jsave(cities, f"{PAGE}/cities.json")
print(len(towns), "towns;", len(feats), "countries;", len(cities), "cities;",
      {f: os.path.getsize(f"{PAGE}/{f}") // 1024 for f in os.listdir(PAGE)}, "KB")
