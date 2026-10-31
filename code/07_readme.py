"""README.md, LICENSE and data/LICENSE. Numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
s, w, rc, cl, rg = R["span"], R["wave"], R["recur"], R["clean"], R["regions"]
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e3:,.0f} KB"
readme = f"""# The plague years

Five centuries of plague in Europe and the Mediterranean, mapped year by year: {s['n_town_years']:,} town-years with plague recorded in {s['n_towns']:,} towns, {s['first']} to {s['last']}. Built from the digitisation by Büntgen and others (2012) of Jean-Noël Biraben's inventory of plague outbreaks (1975 to 1976). An animated map shows the Black Death spreading from the Mediterranean ports, the outbreaks that followed it for three centuries, and when plague last appeared in each town, region and country.

Interactive page: {URL}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- The first wave: {w['n']} towns have their first recorded outbreak in 1347 to 1353, starting with {w['n_seeds']} Mediterranean ports in 1347; plague is recorded in {R['year_1348']} towns in 1348 and reaches the Baltic in 1350. Fitted through distance and year, the recorded frontier moved {w['speed_lo']:.0f} to {w['speed_hi']:.0f} km a year as the crow flies ({w['day_lo']:.1f} to {w['day_hi']:.1f} km a day), an average over sea leaps and slower overland spread.
- Five centuries: outbreaks are recorded in almost every decade to the 1660s; the busiest decade is the {R['decade_peak']['d']}s ({R['decade_peak']['n']} town-years) and the busiest year {R['year_peak']['y']} ({R['year_peak']['n']} towns). Only {R['after_1667_pct']:.1f}% of records come after 1667.
- The towns: London has the most outbreak years ({R['top_towns'][0]['n']}, {R['top_towns'][0]['first']} to {R['top_towns'][0]['last']}), then Algiers ({R['top_towns'][1]['n']}), Paris ({R['top_towns'][2]['n']}) and Toulouse ({R['top_towns'][3]['n']}).
- Recurrence: the median gap between successive plague episodes in a town is {rc['median']:.0f} years (interquartile range {rc['q25']:.0f} to {rc['q75']:.0f}), shortening from {rc['by_century']['1300']['median']:.1f} years in the fourteenth century to {rc['by_century']['1600']['median']:.0f} in the seventeenth.
- When plague left (last year with plague in three or more towns): {', '.join(f"{r['name']} {r['last_wide']}" for r in rg)}. London's last recorded year is {R['landmarks']['london_last']}; Marseille's great plague is recorded in 1720 to 1722.
- The record: France holds {R['cover']['top_pct']:.1f}% of all town-years. Moscow (1771) and Constantinople are absent and Russia appears only {R['landmarks']['n_russia']} times. This is a map of surviving documents, and it records outbreak years, not deaths.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; page data embedded). |
| `header.png` | Social card, 1200 x 630. |
| `data/outbreaks.csv` | {s['n_town_years']:,} town-years: town as in the inventory, English name where useful, year, modern country and region, corrected WGS84 point, source ETRS89 LAEA coordinates ({size('outbreaks.csv')}). |
| `data/towns.csv` | {s['n_towns']:,} towns with point, source point, any correction, number of outbreak years, first and last year and the full list of years. |
| `data/black_death_first_wave.csv` | The {w['n']} towns first recorded in 1347 to 1353, with distance from Messina and from the nearest 1347 town. |
| `data/outbreaks_by_decade.csv` | Town-years and towns per decade. |
| `data/recurrence_intervals.csv` | {rc['n_intervals']:,} intervals between successive episodes in the same town. |
| `data/last_outbreak_by_country.csv`, `data/last_outbreak_by_region.csv` | First and last records, last widespread year and 95% year by country and region. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/page/` | Page data: towns, modern country outlines and city labels (Natural Earth). |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures, blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots from the Playwright check at 1280 px and 390 px. |

## Method in brief

- Repairs to the published file ({cl['n_raw']:,} rows): latitude and longitude columns swapped back (checked against the file's ETRS89 LAEA coordinates); two Eisleben rows broken by an unquoted comma repaired; one row with year 9999 dropped; {cl['n_dupe']} repeated town-years merged; five clearly mislocated towns moved (Prag to Prague, Milan, Noja to Noicattaro near Bari, Gratz to Graz, Siacco to Sciacca), one duplicate spelling merged and one character-set error fixed.
- An outbreak is a town-year. Consecutive outbreak years in a town form an episode; recurrence is the gap between episode starts.
- First wave: towns first recorded in 1347 to 1353; great-circle distance from Messina and from the nearest 1347 town; slopes by Theil-Sen and least squares, bootstrap over towns.
- Ends: per region and country, the last record, the last year with three or more towns, and the year by which 95% of records had occurred.
- Countries are modern (Natural Earth), grouped into eight regions.
- Caveats: records follow surviving documents and Biraben's sources (France {R['cover']['top_pct']:.0f}% of records; eastern Europe thin); presence not mortality; some years approximate; automatic geocoding, of which only clear errors were corrected; modern borders.

## How to rerun

Needs Python 3 with numpy, pandas, shapely, pyproj, matplotlib, fontTools and Pillow, xelatex and pdftotext, and Node with Playwright for the QA script. Raw inputs are read in place (paths in `code/common.py`): `/home/claude/newdata/raw2/plague/Historical_plague_outbreaks.txt` (the EnviDat file, ISO-8859-1) and Natural Earth files in `/home/claude/newdata/raw/geo/`. Intermediates go to `/dev/shm/plague` (set `PLAGUETMP` to change).

```
python3 code/01_clean.py        # repair, deduplicate, place towns
python3 code/02_analyse.py      # results.json and derived tables
python3 code/03_page_data.py    # page data
python3 code/04_build_site.py   # index.html
python3 code/05_figures.py      # header, paper and blog figures
python3 code/06_paper.py        # paper PDF
python3 code/07_readme.py       # README and licences
python3 code/08_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
node code/12_qa.js              # screenshots and console check
```

## Sources and licences

- Büntgen U, Ginzler C, Esper J, Tegel W, McMichael AJ (2012) Digitizing historical plague. Clinical Infectious Diseases 55(11), 1586 to 1588. Dataset: EnviDat, doi:10.16904/envidat.181, Open Database Licence (ODbL) 1.0 with Database Contents Licence (DbCL) 1.0.
- Biraben J-N (1975 to 1976) Les hommes et la peste en France et dans les pays européens et méditerranéens. Paris and The Hague: Mouton.
- Natural Earth countries and populated places (public domain).
- Base map tiles on the page: © Esri.

The tables in `data/` are a derived database of the EnviDat dataset and are made available under the ODbL 1.0 (see `data/LICENSE`). Text and figures are CC BY 4.0; code is MIT (see `LICENSE`).

## Citation

Hotham, T. (2026) The plague years: five centuries of plague outbreaks in Europe and the Mediterranean, 1347 to 1900, from a digitised copy of Biraben's inventory. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
check_dashes("\n".join(l for l in readme.splitlines() if not l.startswith("|---")), "README")
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, paper and blog post and the figures are released under
CC BY 4.0. The data files in data/ are a derived database of "Historical plague
outbreaks" (Buntgen, Ginzler, Esper, Tegel and McMichael, EnviDat,
doi:10.16904/envidat.181), which is licensed under the Open Database Licence
1.0, and are made available under the ODbL 1.0 (see data/LICENSE). Country
outlines and places are Natural Earth (public domain).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
dlic = """The files in this folder are a derived database of:

  Buntgen U, Ginzler C, Esper J, Tegel W, McMichael AJ. Historical plague outbreaks.
  EnviDat. doi:10.16904/envidat.181. Described in: Buntgen U et al. (2012) Digitizing
  historical plague. Clinical Infectious Diseases 55(11), 1586 to 1588.
  A digitisation of Biraben J-N (1975 to 1976) Les hommes et la peste en France et
  dans les pays europeens et mediterraneens.

The original database is licensed under the Open Database Licence (ODbL) 1.0, and its
contents under the Database Contents Licence (DbCL) 1.0. This derived database (the CSV
and JSON files here: repaired, deduplicated and corrected outbreak records, with
countries, regions and summary tables added by Tristan Hotham, 2026) is made available
under the Open Database Licence 1.0: https://opendatacommons.org/licenses/odbl/1-0/
Individual contents remain under the Database Contents Licence 1.0:
https://opendatacommons.org/licenses/dbcl/1-0/

Country outlines and city names in data/page/ are from Natural Earth (public domain).
The changes made to the original are described in code/01_clean.py and README.md.
"""
open(os.path.join(DATA, "LICENSE"), "w", encoding="utf-8").write(dlic)
print("README", len(readme.split()), "words")
