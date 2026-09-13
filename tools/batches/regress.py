# Регрессия общей БД: reference + count_fast2 для всех старых уровней на старой БД (git HEAD → old_db/) и новой.
# Запуск из корня: for f in characters scenes rules; do git show HEAD:Content/rome/$f.json > /tmp/old_db/$f.json; done; python3 tools/batches/regress.py /tmp/old_db
# NEW_IDS — id уровней текущей пачки (их сравнивать не с чем).
import json, glob, sys, subprocess, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, "tools"); import simulate as S
OLD = Path(sys.argv[1]); NEW = Path("Content/rome")
NEW_IDS = set("aspromonte bellarmine_1616 bordeaux_duel castel_escape cola_death francis_sultan imola_1502 lorenzo_deathbed michelangelo_flight senigallia bohemond_antioch heraclius_coup mehmed_ultimatum romanos_blinded secret_history theophano_widow zara".split())
old = S.load_content(OLD); new = S.load_content(NEW)
levels = sorted(p for p in glob.glob("Content/*/levels/*.json") if json.loads(Path(p).read_text())["id"] not in NEW_IDS)
def ref_ok(level, db):
    c, sc, r = db
    panels = [(p["scene"], p["characters"]) for p in level["solution"]]
    return S.goal_met(level["goal"], S.simulate(panels, S.initial_world(level), sc, r, c, []))
def count(db_dir, p):
    out = subprocess.run(["python3", "tools/count_fast2.py", str(db_dir), p], capture_output=True, text=True, timeout=900).stdout
    return out.strip().split("canonical_solutions=")[-1].split()[0] if "canonical_solutions=" in out else "ERR:" + out[-80:]
bad = []
for p in levels:
    L = json.loads(Path(p).read_text())
    if "solution" not in L: continue
    a, b = ref_ok(L, old), ref_ok(L, new)
    if a != b or not b: bad.append((L["id"], "reference", a, b))
print(f"reference check on {len(levels)} old levels: {'OK' if not bad else bad}", flush=True)
def job(p):
    return (p, count(OLD, p), count(NEW, p))
diff = []
with cf.ThreadPoolExecutor(8) as ex:
    for p, o, n in ex.map(job, levels):
        if o != n: diff.append((p, o, n)); print("DIFF", p, o, "->", n, flush=True)
print(f"canonical compare done: {len(levels)} levels, diffs: {len(diff)}")
for d in diff: print("  ", d)
