"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (towns, world, cities) is embedded. Facts stated in words are checked here against the
data. The full-screen map snippet (copied from the drinks-map reference, code/fullscreen_snippet.html) goes before </body>.
{{DOI}} and https://blog.tristanhotham.com/2026/10/31/plague-map/ are left for the publisher to fill."""
import re
from common import *

R = jload(f"{DATA}/results.json")
C = jload(f"{WORK}/clean.json")
BY = C["by_town"]
inyear = lambda town, y: y in BY[town]

# facts stated in words (page, and reused by the blog and paper)
for t in ("Messina", "Catania", "Siracusa", "Reggio di Calabria", "Napoli", "Genova", "Cagliari", "Trapani", "Agrigento"):
    assert BY[t][0] == 1347, t
for t in ("Alexandrie", "Kairo", "Tunis", "Sevilla", "Bordeaux", "London", "Bristol"):
    assert inyear(t, 1348), t
assert BY["Paris"][0] == 1349 and R["wave"]["first_deu"] == 1349
for t in ("Gdansk", "Stralsund"):
    assert BY[t][0] == 1350, t
assert R["wave"]["first_baltic"] == 1350 and R["wave"]["by_year"]["1347"] == R["wave"]["n_seeds"] == 10
assert 1900 <= R["wave"]["p90_1348"] <= 2100   # "already 2,000 km from Messina, in England" uses the rounded figure
assert R["wave"]["far_1350"][0][0] == "Aluksne"
assert any(T == "London" for T in BY if 1348 in BY[T])
assert R["decade_peak"]["d"] == 1630 and R["year_peak"]["y"] == 1630
d1630 = [d for d in R["decades"] if d["d"] == 1630][0]["reg"]
assert d1630["fra"] == max(d1630.values())
assert [t["town"] for t in R["top_towns"][:4]] == ["London", "Alger", "Paris", "Toulouse"]
assert [r["k"] for r in R["regions"]] == ["ita", "brit", "ibe", "east", "cen", "fra", "magh", "otto"], [r["k"] for r in R["regions"]]
for t, y in (("Napoli", 1656), ("Roma", 1656), ("Genova", 1656), ("Wien", 1679), ("Prag", 1713), ("Hamburg", 1713), ("Bremen", 1713),
             ("Marseille", 1720), ("Marseille", 1721), ("Marseille", 1722), ("Messina", 1743), ("Noja", 1815), ("Noja", 1816),
             ("Manacor", 1819), ("Palma", 1819), ("Porto", 1899), ("Porto", 1900), ("Eyam", 1666), ("London", 1665)):
    assert inyear(t, y), (t, y)
assert R["landmarks"]["n_russia"] == 2 and R["recur"]["by_century"]["1300"]["median"] > R["recur"]["by_century"]["1600"]["median"]
present = {c["iso"] for c in R["countries"]}
assert not present & {"NLD", "BEL", "SWE", "NOR", "DNK", "FIN", "HUN", "GRC", "BGR", "SRB", "ROU", "HRV", "BIH", "ALB"}
assert "CZE" in present and [c["n"] for c in R["countries"] if c["iso"] == "CZE"][0] == len(BY["Prag"])
assert R["after_1670_south_pct"] > 80 and len(FIX) == 5 and R["landmarks"]["gbr_1665_n"] > 50


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl, R)
    assert not re.search(r"\{\{(?!DOI\}\}|BLOG_URL\}\})", html), re.findall(r"\{\{[^}]*\}\}", html)[:5]
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*TOWNS*/", open(f"{PAGE}/towns.json", encoding="utf-8").read())
    html = html.replace("/*WORLD*/", open(f"{PAGE}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", open(f"{PAGE}/cities.json", encoding="utf-8").read())
    html = html.replace("/*REGIONS*/", J([[k, n, c] for k, n, _, c in REGIONS]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    check_dashes(vis, "page text")
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    for bad in ("DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in html, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
