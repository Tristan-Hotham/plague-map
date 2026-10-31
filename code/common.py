"""Shared paths and helpers for the plague-map project.

Raw inputs (read in place, never copied into the repo):
  PLAGUE  /home/claude/newdata/raw2/plague/Historical_plague_outbreaks.txt
          Buntgen U, Ginzler C, Esper J, Tegel W, McMichael AJ (2012) Digitizing historical plague. Clinical Infectious
          Diseases 55(11):1586-1588. Dataset on EnviDat, doi:10.16904/envidat.181, ODbL 1.0 with DbCL 1.0.
          A digitisation of Biraben J-N (1975-76) Les hommes et la peste en France et dans les pays europeens et
          mediterraneens. CSV, ISO-8859-1. Columns: Location, X_Coord_ERTS89, Y_Coord_ERTS89 (ETRS89 LAEA, EPSG:3035),
          Year_of_Outbreak, Lat_WGS84, Lon_WGS84. The last two columns are swapped in the file (Lat holds longitude).
  GEO     /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson, ne_50m_admin_0_countries.geojson,
          ne_10m_populated_places_simple.geojson (Natural Earth, public domain).
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "/home/claude/newdata/raw2/plague/Historical_plague_outbreaks.txt"
GEO = "/home/claude/newdata/raw/geo"
NE10 = f"{GEO}/ne_10m_admin_0_countries.geojson"
NE50 = f"{GEO}/ne_50m_admin_0_countries.geojson"
PLACES = f"{GEO}/ne_10m_populated_places_simple.geojson"
DATA = os.path.join(ROOT, "data")
PAGE = os.path.join(DATA, "page")
WORK = os.environ.get("PLAGUETMP", "/dev/shm/plague")   # intermediates live in memory, not in the repo
for d in (DATA, PAGE, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "plague-map"
URL = "https://maps.tristanhotham.com/plague-map/"
REPO = "https://github.com/Tristan-Hotham/plague-map"
DOI = "{{DOI}}"
DOI_URL = "{{DOI_URL}}"
BLOG = "https://blog.tristanhotham.com/2026/10/31/plague-map/"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# Macro regions, built from modern countries (ISO A3). Order is roughly north-west to south-east.
REGIONS = [
    ("brit", "Britain and Ireland", ["GBR", "IRL", "IMN", "GGY", "JEY"], "#3E5FB8"),
    ("fra", "France", ["FRA", "MCO", "AND"], "#2F6B4F"),
    ("ibe", "Iberia", ["ESP", "PRT", "GIB"], "#C08A00"),
    ("ita", "Italy", ["ITA", "MLT", "SMR", "VAT"], "#B8452A"),
    ("cen", "Central Europe", ["DEU", "AUT", "CHE", "LIE", "CZE", "SVN", "NLD", "BEL", "LUX", "DNK", "HUN", "SVK"], "#8C4A2F"),
    ("east", "Poland, the Baltic and Russia", ["POL", "LTU", "LVA", "EST", "RUS", "BLR", "UKR", "FIN", "SWE", "NOR"], "#6E5A7E"),
    ("magh", "North Africa", ["MAR", "DZA", "TUN", "LBY"], "#1E8C88"),
    ("otto", "Anatolia, the Levant and Egypt", ["TUR", "EGY", "LBN", "SYR", "ISR", "PSE", "JOR", "CYP", "GRC"], "#9B2D6F"),
]
REGION_OF = {iso: k for k, _, isos, _ in REGIONS for iso in isos}
REGION_NAME = {k: n for k, n, _, _ in REGIONS}
REGION_COL = {k: c for k, _, _, c in REGIONS}

# Geocoding corrections. The digitisation geocoded Biraben's place names automatically; these few are clearly wrong
# and are moved (the source point is kept in the data as source_lat, source_lon). Merges join a duplicate spelling.
FIX = {
    "Prag": (50.0755, 14.4378, "Prague: the source point is a village called Prag in Bavaria"),
    "Milan": (45.4642, 9.1900, "Milan: the source point is near Treviso, not Milan"),
    "Noja": (41.0330, 16.9900, "Noja, now Noicattaro near Bari (the plague of 1815 to 1816): the source point is Noja in Cantabria, Spain"),
    "Siacco": (37.5086, 13.0886, "Siacco, read here as Sciacca, a Sicilian port struck in 1347 with the other Sicilian ports: the source point is in Friuli"),
    "Gratz": (47.0707, 15.4395, "Gratz, the old spelling of Graz: the source point is a hamlet in Upper Austria"),
}
MERGE = {"PAISLEY": "Paisley"}
RENAME = {"Besanèon": "Besançon"}   # a character-set error in the source

# English names for some places the inventory gives in another language (display and search only; source names kept).
ALIAS = {
    "Kairo": "Cairo", "Alexandrie": "Alexandria", "Beyrouth": "Beirut", "Alger": "Algiers", "Bone": "Annaba (Bône)",
    "Venezia": "Venice", "Wien": "Vienna", "Prag": "Prague", "Warszawa": "Warsaw", "Sevilla": "Seville", "Firenze": "Florence",
    "Napoli": "Naples", "Genova": "Genoa", "Roma": "Rome", "Torino": "Turin", "Milano": "Milan", "Padova": "Padua",
    "Mantova": "Mantua", "Siracusa": "Syracuse", "Lisboa": "Lisbon", "Köln": "Cologne", "München": "Munich",
    "Nürnberg": "Nuremberg", "Braunschweig": "Brunswick", "Gdansk": "Danzig (Gdańsk)", "Kraków": "Cracow (Kraków)",
    "Tanger": "Tangier", "Tripoli": "Tripoli (Libya)", "Bruxelles": "Brussels", "Antwerpen": "Antwerp", "Gent": "Ghent",
    "Brugge": "Bruges", "Den Haag": "The Hague", "Dublin Industrial Estate": "Dublin", "Binn Éadair": "Howth",
    "København": "Copenhagen", "Göteborg": "Gothenburg", "Zürich": "Zurich", "Genève": "Geneva", "Luzern": "Lucerne",
    "Athina": "Athens", "Thessaloniki": "Salonica (Thessaloniki)", "Bucuresti": "Bucharest", "Beograd": "Belgrade",
    "Zagreb": "Zagreb", "Dubrovnik": "Ragusa (Dubrovnik)", "Split": "Split", "Djidjelli": "Jijel (Djidjelli)", "Prag": "Prague", "Gratz": "Graz", "Siacco": "Sciacca", "Noja": "Noicattaro", "Corcaigh": "Cork",
    "Loch Garman": "Wexford", "An Nás": "Naas", "Iruña": "Pamplona", "Sagunt": "Sagunto", "Geneve": "Geneva", "Izmir": "Izmir (Smyrna)",
    "Oran": "Oran", "Wrecsam": "Wrexham",
}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def jsave(obj, path, indent=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "yr": return str(int(v))
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    raise ValueError(f)


def fill(text, R, f=fmt):
    out = re.sub(r"\{\{(?!IMG|DOI|BLOG_URL|DOI_URL|TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: f(get(R, m.group(1)), m.group(3)), text)
    return out


def check_dashes(text, where):
    for bad in ("—", "–", "--"):
        assert bad not in text, (where, bad, text[max(0, text.find(bad) - 80):text.find(bad) + 80])
