#!/usr/bin/env python3
"""Песочница «слепого» прохождения: отдаёт ровно то, что видит игрок, и принимает попытки.

Зачем: оценки «понятно / интересно» на глаз ничего не стоят. Здесь понятность становится
числом — сколько попыток нужно, чтобы решить уровень, зная только тексты и ростер.
Правила (`rules.json`) и эталон (`solution`) наружу не отдаются вообще: тестировщик их не
видит физически, а не по договорённости.

Отвечает теми же четырьмя вердиктами, что рисует игра на панелях (ui.wrong_* в каталоге),
и так же — только когда доска заполнена целиком. Порядок персонажей внутри панели
подбирается за игрока, как в приложении (LevelBoardModel.autoAssignSlots).

    python3 tools/blind_play.py brief <level_id> [--hint]   без --hint подсказка скрыта
    python3 tools/blind_play.py try <level_id> "сцена: перс, перс | сцена: перс"
    python3 tools/blind_play.py score [--reset]      сводка попыток по всем уровням

Журнал попыток: dist/blind_play.json (метрика для таблицы «попытки × order»).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulate import goal_met, initial_world, load_content, simulate

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "Content"
# Журнал попыток. Отдельный на тестировщика (переменная BLIND_LOG) — иначе двое, играющие
# параллельно, затирают счётчики друг друга.
LOG = Path(__import__("os").environ.get("BLIND_LOG", str(ROOT / "dist" / "blind_play.json")))

# Флаги, которые игра рисует бейджем на портрете (StateBadges.emojis). Остальные состояния
# игроку не видны вообще — и песочница не должна их показывать, иначе замер завышен:
# у Сифакса метка `punic_ally` подсказывала выбор, которого в игре не подсказано ничем.
BADGES = {"dead": "☠️", "plotting": "🗡", "traitor": "🎭", "crowned": "👑", "backed": "🛡",
          "conqueror": "⚔️", "locked_out": "🔒", "inside": "🚪", "in_rome": "🏛", "has_heir": "👶"}

VERDICT = {
    "ok": "панель верна",
    "wrong_chars": "Место то — да не те лица",
    "wrong_scene": "Верные герои — да не то место",
    "inert": "Совсем не то — ни место, ни лица",
    "wrong_order": "Всё то — да не в том порядке",
    "wrong_slots": "Люди те — да не по ролям: поменяй их местами в кадре",
}


def catalog() -> dict:
    return json.loads((CONTENT / "i18n" / "ru.json").read_text(encoding="utf-8"))


def find_level(level_id: str) -> dict:
    for p in CONTENT.glob("*/levels/*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d["id"] == level_id:
            return d
    sys.exit(f"нет такого уровня: {level_id}")


def db():
    return load_content(CONTENT / "rome")


def brief(level_id: str, show_hint: bool = False) -> None:
    """Всё, что видно игроку на экране уровня, и ничего сверх того."""
    lv = find_level(level_id)
    cat = catalog()
    chars, scenes, _rules = db()

    def t(key, default=""):
        return cat.get(f"level.{level_id}.{key}", default)

    print(f"УРОВЕНЬ: {t('title', level_id)}   (эпоха {lv['epoch']}, позиция {lv['order']})")
    if t("intro"):
        print(f"ЗАВЯЗКА: {t('intro')}")
    print(f"ЦЕЛЬ: {t('goal')}")
    # Подсказка в этой игре почти равна решению, поэтому «слепой» прогон должен идти без неё:
    # иначе замеряется качество подсказки, а не сложность уровня. Показываем только по флагу.
    if show_hint:
        print(f"ПОДСКАЗКА: {t('hint', '— подсказки нет —')}")
    print(f"ПАНЕЛЕЙ: {lv['panels']}")
    print("\nСЦЕНЫ (их больше, чем панелей — лишние ставить некуда):")
    for sid in lv["scenes"]:
        sc = scenes[sid]
        name = cat.get(f"scene.{sid}", sid)
        action = cat.get(f"scene.{sid}.action", "")
        roles = sc.get("roles")
        print(f"  {name} — «{action}», мест: {sc.get('slots', 2)}"
              + (f", роли: {', '.join(roles)}" if roles else ", роли не указаны"))
    print("\nПЕРСОНАЖИ:")
    for cid in lv["characters"]:
        st = lv.get("initialState", {}).get("flags", {}).get(cid) or []
        shown = [BADGES[f] for f in st if f in BADGES]
        print(f"  {cat.get(f'char.{cid}', cid)}" + (f"   {' '.join(shown)}" if shown else ""))
    print("\nПопытка:  python3 tools/blind_play.py try %s \"<сцена>: <перс>, <перс> | ...\"" % level_id)


def _resolve(name: str, mapping: dict[str, str], kind: str) -> str:
    key = name.strip().lower()
    for ident, human in mapping.items():
        if key in (ident.lower(), human.lower()):
            return ident
    hits = [i for i, h in mapping.items() if key in h.lower()]
    if len(hits) == 1:
        return hits[0]
    sys.exit(f"не понял {kind} «{name}». Доступно: {', '.join(mapping.values())}")


def _auto_slots(panels, lv, scenes, rules, chars):
    """Подбор порядка внутри кадров — как в приложении: совместный перебор по всем кадрам,
    максимум сработавших правил, при равенстве — порядок игрока (первый вариант = исходный)."""
    panels = [(s, list(c)) for s, c in panels]
    idxs = [i for i, (_, cs) in enumerate(panels) if len(cs) > 1]
    if not idxs:
        return panels
    def perms(cs):
        first = list(cs)
        return [first] + [list(p) for p in itertools.permutations(cs) if list(p) != first]
    options = [perms(panels[i][1]) for i in idxs]
    best, best_score = panels, -1
    for combo in itertools.product(*options):
        trial = list(panels)
        for k, i in enumerate(idxs):
            trial[i] = (panels[i][0], combo[k])
        log: list[str] = []
        simulate([(s, list(c)) for s, c in trial if s], initial_world(lv), scenes, rules, chars, log)
        if len(log) > best_score:
            best_score, best = len(log), trial
    return best


def _try_resolve(text: str, names: dict) -> str | None:
    """Тот же поиск, что и _resolve, но без выхода: нужен, чтобы разобрать двоеточия в именах."""
    t = text.strip().lower()
    if not t:
        return None
    for k, v in names.items():
        if t == v.lower() or t == k:
            return k
    hits = [k for k, v in names.items() if t in v.lower()]
    return hits[0] if len(hits) == 1 else None


def attempt(level_id: str, spec: str) -> None:
    lv = find_level(level_id)
    cat = catalog()
    chars, scenes, rules = db()
    scene_names = {s: cat.get(f"scene.{s}", s) for s in lv["scenes"]}
    char_names = {c: cat.get(f"char.{c}", c) for c in lv["characters"]}

    panels = []
    for chunk in spec.split("|"):
        chunk = chunk.strip()
        if not chunk:
            panels.append((None, []))
            continue
        # Двоеточие есть и в названиях сцен («Обет: никого не казнить»), поэтому режем по
        # ПОСЛЕДНЕМУ — оно отделяет список персонажей. Если справа от него не персонажи,
        # значит двоеточий в имени больше, чем разделителей: пробуем всю строку как имя сцены.
        sname, _, rest = chunk.rpartition(":")
        if not sname:
            sname, rest = chunk, ""
        elif not _try_resolve(sname, scene_names) and _try_resolve(chunk, scene_names):
            sname, rest = chunk, ""
        sid = _resolve(sname, scene_names, "сцену")
        cs = [_resolve(x, char_names, "персонажа") for x in rest.split(",") if x.strip()]
        panels.append((sid, cs))
    if len(panels) != lv["panels"]:
        sys.exit(f"панелей должно быть {lv['panels']}, а в попытке {len(panels)}")

    filled = [(sid, cs) for sid, cs in panels if sid]
    complete = len(filled) == lv["panels"] and all(
        len(cs) == scenes[sid].get("slots", 2) for sid, cs in filled)

    play = _auto_slots([(s or "", c) for s, c in panels], lv, scenes, rules, chars)
    world = simulate([(s, list(c)) for s, c in play if s], initial_world(lv), scenes, rules, chars, [])
    solved = goal_met(lv["goal"], world)

    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    rec = log.setdefault(level_id, {"attempts": 0, "solved_at": None})
    rec["attempts"] += 1
    if solved and rec["solved_at"] is None:
        rec["solved_at"] = rec["attempts"]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1))

    print(f"попытка №{rec['attempts']}")
    if solved:
        print("РЕШЕНО ✔")
        print(f"ФАКТ: {cat.get(f'level.{level_id}.fact', '')[:400]}")
        return
    print("не решено")
    if not complete:
        print("(доска заполнена не до конца — игра в таком виде подсказок не даёт)")
        return
    for i, v in enumerate(_diagnose(panels, lv, scenes), 1):
        print(f"  панель {i}: {VERDICT[v]}")


def _diagnose(panels, lv, scenes) -> list[str]:
    """Порт LevelBoardModel.computeDiagnoses: панели сверяются с эталоном как мультимножество."""
    sol = lv.get("solution")
    if not sol:
        return ["ok"] * len(panels)
    remaining = [(p["scene"], frozenset(p["characters"])) for p in sol]

    def filled(i):
        sid, cs = panels[i]
        if not sid or len(cs) != scenes[sid].get("slots", 2):
            return None
        return (sid, frozenset(cs))

    diag = ["ok"] * len(panels)
    pending = []
    for i in range(len(panels)):
        f = filled(i)
        if not f:
            continue
        if f in remaining:
            remaining.remove(f)
        else:
            pending.append(i)
    if not pending:
        ref = [(p["scene"], list(p["characters"])) for p in lv["solution"]]
        out = []
        for i, (sid, cs) in enumerate(panels):
            if not filled(i): out.append("ok"); continue
            exact = any(r[0] == sid and r[1] == list(cs) for r in ref)
            out.append("wrong_order" if exact else "wrong_slots")
        return out
    for i in pending:
        sid, cs = filled(i)
        m = next((r for r in remaining if r[0] == sid), None)
        if m:
            diag[i] = "wrong_chars"; remaining.remove(m); continue
        m = next((r for r in remaining if r[1] == cs), None)
        if m:
            diag[i] = "wrong_scene"; remaining.remove(m); continue
        diag[i] = "inert"
    return diag


def score(reset: bool) -> None:
    if reset:
        LOG.unlink(missing_ok=True)
        print("журнал очищен")
        return
    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    cat = catalog()
    rows = []
    for p in CONTENT.glob("*/levels/*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d["id"] in log:
            r = log[d["id"]]
            rows.append((d["order"], d["id"], cat.get(f"level.{d['id']}.title", ""),
                         r["attempts"], r["solved_at"]))
    print(f"{'order':>6} {'уровень':22} {'попыток':>8} {'решён с':>8}")
    for o, i, t, a, s in sorted(rows):
        print(f"{o:6} {t[:22]:22} {a:8} {str(s or '—'):>8}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "brief":
        brief(sys.argv[2], "--hint" in sys.argv)
    elif cmd == "try":
        attempt(sys.argv[2], sys.argv[3])
    elif cmd == "score":
        score("--reset" in sys.argv)
    else:
        sys.exit(__doc__)
