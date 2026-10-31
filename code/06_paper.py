"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/Hotham_The_Plague_Years.tex and .pdf (figures f_*.png sit beside them)."""
import re, subprocess
from common import *

R = jload(f"{DATA}/results.json"); C = R["clean"]
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_The_Plague_Years"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def tfmt(v, f):
    if f == "pc": return f"{round(float(v))}\\%"
    return tex(fmt(v, f or "raw"))


TC = ("\\begin{table}[tbp]\\centering\\small\\caption{From the published file to the analysis table.}\\label{tab:clean}"
      "\\begin{tabular}{lr}\\toprule Step & Rows\\\\\\midrule\n"
      f"Rows in the published file & {C['n_raw']:,}\\\\\n"
      f"Dropped: year 9999 & $-${C['dropped_9999']}\\\\\n"
      f"Repaired: Eisleben rows broken by a comma (kept) & {C['eisleben_fixed']}\\\\\n"
      f"Merged: repeated town and year & $-${C['n_dupe']}\\\\\n"
      f"Town-years analysed & {C['n_town_years']:,}\\\\\n"
      f"Towns (after merging one duplicate spelling) & {C['n_towns']:,}\\\\\n"
      f"Towns moved to the correct place & {C['n_fixed']}\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")
assert C["n_raw"] - C["dropped_9999"] - C["n_dupe"] == C["n_town_years"]
rows = "".join(f"{tex(t['town'])}{(' (' + tex(t['en']) + ')') if t['en'] else ''} & {tex(t['country'])} & {t['n']} & {t['first']} & {t['last']}\\\\\n" for t in R["top_towns"])
TT = ("\\begin{table}[tbp]\\centering\\small\\caption{The twenty towns with most outbreak years (names as in the inventory).}\\label{tab:top}"
      "\\begin{tabular}{llrrr}\\toprule Town & Country & Years & First & Last\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(r['name'])} & {r['n']:,} & {r['towns']} & {r['first']} & {r['p95']} & {r['last_wide']} & {r['last']}\\\\\n" for r in R["regions"])
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Regions: town-years, towns, first record, the year by which 95\\% of records had occurred, the last year with plague in three or more towns, and the last record.}\\label{tab:regions}"
      "\\begin{tabular}{lrrrrrr}\\toprule Region & Town-years & Towns & First & 95\\% & Last 3+ & Last\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(c['name'])} & {c['n']:,} & {c['towns']} & {c['first']} & {c['last_wide'] or ''} & {c['last']} & {tex(', '.join(c['last_towns'][:3]))}{'...' if len(c['last_towns']) > 3 else ''}\\\\\n" for c in R["countries"][::-1])
TK = ("\\begin{table}[tbp]\\centering\\small\\caption{Modern countries, sorted by last record.}\\label{tab:countries}\\setlength{\\tabcolsep}{4pt}"
      "\\begin{tabular}{lrrrrrl}\\toprule Country & Town-years & Towns & First & Last 3+ & Last & Last record at\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\url{{{meta.page}}}", "\\url{%s}" % URL).replace("\\url{{{meta.repo}}}", "\\url{%s}" % REPO)
t = fill(t, R, tfmt)
t = t.replace("{{TABLE_CLEAN}}", TC).replace("{{TABLE_TOP}}", TT).replace("{{TABLE_REGIONS}}", TR).replace("{{TABLE_COUNTRIES}}", TK)
assert not re.search(r"\{\{(?!DOI\}\})", t), re.findall(r"\{\{[^}]*\}\}", t)[:5]
check_dashes(t, "paper")
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
# compile a copy with a visible placeholder DOI (the publisher refills {{DOI}} and recompiles)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l or l.startswith("!")][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
