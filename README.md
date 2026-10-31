# The plague years

Five centuries of plague in Europe and the Mediterranean, mapped year by year: 6,848 town-years with plague recorded in 1,172 towns, 1347 to 1900. Built from the digitisation by Büntgen and others (2012) of Jean-Noël Biraben's inventory of plague outbreaks (1975 to 1976). An animated map shows the Black Death spreading from the Mediterranean ports, the outbreaks that followed it for three centuries, and when plague last appeared in each town, region and country.

Interactive page: https://maps.tristanhotham.com/plague-map/
Paper: https://doi.org/10.5281/zenodo.23844513
Blog post: https://blog.tristanhotham.com/2026/10/31/plague-map/

## Headline results

- The first wave: 195 towns have their first recorded outbreak in 1347 to 1353, starting with 10 Mediterranean ports in 1347; plague is recorded in 110 towns in 1348 and reaches the Baltic in 1350. Fitted through distance and year, the recorded frontier moved 176 to 214 km a year as the crow flies (0.5 to 0.6 km a day), an average over sea leaps and slower overland spread.
- Five centuries: outbreaks are recorded in almost every decade to the 1660s; the busiest decade is the 1630s (570 town-years) and the busiest year 1630 (119 towns). Only 7.6% of records come after 1667.
- The towns: London has the most outbreak years (132, 1348 to 1667), then Algiers (112), Paris (89) and Toulouse (88).
- Recurrence: the median gap between successive plague episodes in a town is 13 years (interquartile range 6 to 31), shortening from 18.5 years in the fourteenth century to 11 in the seventeenth.
- When plague left (last year with plague in three or more towns): Italy 1657, Britain and Ireland 1667, Iberia 1681, Poland, the Baltic and Russia 1712, Central Europe 1713, France 1722, North Africa 1821, Anatolia, the Levant and Egypt 1834. London's last recorded year is 1667; Marseille's great plague is recorded in 1720 to 1722.
- The record: France holds 40.4% of all town-years. Moscow (1771) and Constantinople are absent and Russia appears only 2 times. This is a map of surviving documents, and it records outbreak years, not deaths.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; page data embedded). |
| `header.png` | Social card, 1200 x 630. |
| `data/outbreaks.csv` | 6,848 town-years: town as in the inventory, English name where useful, year, modern country and region, corrected WGS84 point, source ETRS89 LAEA coordinates (527 KB). |
| `data/towns.csv` | 1,172 towns with point, source point, any correction, number of outbreak years, first and last year and the full list of years. |
| `data/black_death_first_wave.csv` | The 195 towns first recorded in 1347 to 1353, with distance from Messina and from the nearest 1347 town. |
| `data/outbreaks_by_decade.csv` | Town-years and towns per decade. |
| `data/recurrence_intervals.csv` | 3,203 intervals between successive episodes in the same town. |
| `data/last_outbreak_by_country.csv`, `data/last_outbreak_by_region.csv` | First and last records, last widespread year and 95% year by country and region. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/page/` | Page data: towns, modern country outlines and city labels (Natural Earth). |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures, blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots from the Playwright check at 1280 px and 390 px. |

## Method in brief

- Repairs to the published file (6,929 rows): latitude and longitude columns swapped back (checked against the file's ETRS89 LAEA coordinates); two Eisleben rows broken by an unquoted comma repaired; one row with year 9999 dropped; 80 repeated town-years merged; five clearly mislocated towns moved (Prag to Prague, Milan, Noja to Noicattaro near Bari, Gratz to Graz, Siacco to Sciacca), one duplicate spelling merged and one character-set error fixed.
- An outbreak is a town-year. Consecutive outbreak years in a town form an episode; recurrence is the gap between episode starts.
- First wave: towns first recorded in 1347 to 1353; great-circle distance from Messina and from the nearest 1347 town; slopes by Theil-Sen and least squares, bootstrap over towns.
- Ends: per region and country, the last record, the last year with three or more towns, and the year by which 95% of records had occurred.
- Countries are modern (Natural Earth), grouped into eight regions.
- Caveats: records follow surviving documents and Biraben's sources (France 40% of records; eastern Europe thin); presence not mortality; some years approximate; automatic geocoding, of which only clear errors were corrected; modern borders.

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

Hotham, T. (2026) The plague years: five centuries of plague outbreaks in Europe and the Mediterranean, 1347 to 1900, from a digitised copy of Biraben's inventory. Zenodo. https://doi.org/10.5281/zenodo.23844513

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
