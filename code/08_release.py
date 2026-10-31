"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
{{DOI}}, {{DOI_URL}} and https://blog.tristanhotham.com/2026/10/31/plague-map/ are left for the publisher to fill."""
import re, shutil, zipfile, json as _json
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release")
NAME = "Hotham_The_Plague_Years"

# numbers written out in the blog's alt text, checked against results
tt = [(t["town"], t["n"]) for t in R["top_towns"][:5]]
assert tt == [("London", 132), ("Alger", 112), ("Paris", 89), ("Toulouse", 88), ("Izmir", 86)], tt
assert [t["town"] for t in R["top_towns"][5:10]] == ["Bourg-en-Bresse", "Amiens", "Nantes", "Bordeaux", "Venezia"]
assert sum(1 for t in R["top_towns"] if t["country"] == "France") > 10
assert R["decade_peak"]["n"] == 570 and R["recur"]["median"] == 13
assert [r["last_wide"] for r in R["regions"]] == [1657, 1667, 1681, 1712, 1713, 1722, 1821, 1834]
assert 1900 <= R["wave"]["p90_1348"] <= 2100 and 0.4 <= R["wave"]["day_lo"] and R["wave"]["day_hi"] <= 0.65   # "about 2,000 km", "roughly half a kilometre a day"
assert max(R["recur"]["hist"], key=lambda k: R["recur"]["hist"][k]) == "2"

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
check_dashes(vis, "blog")
assert AI in post
for bad in ("DSIT", "DCMS", "civil serv"):
    assert bad not in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "The plague years: five centuries of plague, mapped year by year",
        "slug": "plague-map",
        "excerpt": f"{R['span']['n_town_years']:,} recorded outbreak years in {R['span']['n_towns']:,} towns, from the Black Death in 1347 to Porto in 1900: how plague spread, kept coming back about every {R['recur']['median']:.0f} years, and left Europe a century before the Ottoman Mediterranean.",
        "seo_description": "An animated map of five centuries of plague in Europe and the Mediterranean, 1347 to 1900: the Black Death, the returns, and when plague left.",
        "tags": ["plague", "Black Death", "history", "maps", "data visualisation", "epidemics", "Europe"],
        "header_alt": f"Title card reading 'The plague years' in black and red on cream, beside a map of Europe and the Mediterranean covered in red dots sized by the number of years plague was recorded in each town, largest in London, Paris, Algiers and Izmir. Text: {R['span']['n_town_years']:,} outbreak years in {R['span']['n_towns']:,} towns, 1347 to 1900."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/plague-map_code_and_data.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data", "data/page"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, fn)
            if os.path.isdir(p) or fn.endswith(".pyc"):
                continue
            z.write(p, f"plague-map/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"plague-map/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = re.sub(r"\\citet\{buntgen2012\}", "Büntgen et al. (2012)", ab)
ab = re.sub(r"\\citet\{biraben1975\}", "Biraben (1975 to 1976)", ab)
ab = ab.replace("\\%", "%").replace("\\&", "&")
assert "\\" not in ab, ab
zmeta = {"title": "The Plague Years: Five Centuries of Plague Outbreaks in Europe and the Mediterranean, 1347 to 1900, from a Digitised Copy of Biraben's Inventory",
         "upload_type": "publication", "publication_type": "workingpaper",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{URL}\">{URL}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p>"
                        "<p>Licences: the paper is CC BY 4.0. The derived data tables in the zip (data/) are a derived database of the EnviDat dataset doi:10.16904/envidat.181 and are released under the Open Database Licence 1.0. Code is MIT.</p>"
                        f"<p>{AI}</p>",
         "keywords": ["plague", "Black Death", "second pandemic", "historical epidemiology", "Biraben", "Europe", "Mediterranean", "maps", "open data"],
         "license": "cc-by-4.0",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": URL, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "10.16904/envidat.181", "relation": "isDerivedFrom", "resource_type": "dataset", "scheme": "doi"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
check_dashes(s, "metadata")
print("blog words", words, "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
