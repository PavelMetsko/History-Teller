#!/usr/bin/env python3
"""Пачка 6 главы «Польша»: Вавельский дракон (легенда) — первое существо фабрики.

    python3 tools/batches/poland_6.py [repo_root]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poland_1 as P
from poland_1 import char, scene, actor, setf, rule, flag, nflag, level, texts, ACT1

NEW_CHARS = [
    char("wawel_dragon", "Вавельский дракон", ["dragon_pl"], "🐉"),
    char("krak", "Князь Крак", ["krak_pl"], "👑"),
    char("skuba", "Сапожник Скуба", ["shoemaker_pl"], "👞"),
    char("wawel_knight", "Рыцарь в латах", ["knight_wawel_pl"], "🛡️"),
]
NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS = [], [], [], {}

NEW_SCENES += [
    scene("dragon_cave_pl", "Драконья пещера", ["sig_dragon_cave_pl"], 2, "⚔️", "идти на дракона", "icon_dead",
          ["рыцарь", "дракон"], "cellar_search"),
    scene("sulfur_ram_pl", "Баран, набитый серой", ["sig_sulfur_ram_pl"], 1, "🐏", "начинить барана", "icon_plot",
          ["сапожник"], "butcher_stall_v"),
    scene("vistula_drink_pl", "Дракон пьёт Вислу", ["sig_vistula_drink_pl"], 2, "💧", "подбросить приманку", "icon_dead",
          ["сапожник", "дракон"], "black_river"),
    scene("krak_reward_pl", "Награда князя", ["sig_krak_reward_pl"], 2, "👑", "наградить героя", "icon_crown",
          ["князь", "герой"], "throne"),
]
NEW_RULES += [
    rule("dragon_cave_pl_sig", "Рыцарь в латах идёт в пещеру под Вавелем — и дракон его сжирает",
         "sig_dragon_cave_pl",
         [actor("A", 0, tags=["knight_wawel_pl"]), actor("B", 1, tags=["dragon_pl"])],
         [setf("A", "dead")]),
    rule("sulfur_ram_pl_sig", "Сапожник набивает баранью шкуру серой и смолой",
         "sig_sulfur_ram_pl",
         [actor("A", 0, tags=["shoemaker_pl"])],
         [setf("A", "bait_ready_pl")]),
    rule("vistula_drink_pl_sig", "Дракон глотает барана, в брюхе загорается сера — он пьёт Вислу, пока не лопается",
         "sig_vistula_drink_pl",
         [actor("A", 0, tags=["shoemaker_pl"], flags=["bait_ready_pl"]), actor("B", 1, tags=["dragon_pl"])],
         [setf("B", "dead"), setf("A", "hero_dragon_pl")]),
    rule("krak_reward_pl_sig", "Князь отдаёт сапожнику обещанную награду",
         "sig_krak_reward_pl",
         [actor("A", 0, tags=["krak_pl"]), actor("B", 1, tags=["shoemaker_pl"], flags=["hero_dragon_pl"])],
         [setf("B", "rewarded_pl")]),
]
NEW_LEVELS.append(level(
    "wawel_dragon", 11, ACT1, "poland_tension", "vistula_drink_pl", 3,
    ["dragon_cave_pl", "sulfur_ram_pl", "vistula_drink_pl", "krak_reward_pl"],
    ["krak", "skuba", "wawel_knight", "wawel_dragon"],
    {"krak": ["reigns", "standing"], "wawel_dragon": ["strong"], "wawel_knight": ["standing", "strong"]}, [],
    [flag("wawel_dragon", "dead"), flag("skuba", "rewarded_pl"), nflag("wawel_knight", "dead")],
    [("sulfur_ram_pl", ["skuba"]), ("vistula_drink_pl", ["skuba", "wawel_dragon"]), ("krak_reward_pl", ["krak", "skuba"])],
    "legend"))
TEXTS.update(texts("wawel_dragon",
    "Вавельский дракон",
    "Рыцари гибнут в пещере дракона, а простой сапожник подбрасывает ему барана с серой — и дракон пьёт Вислу, пока не лопается",
    "Силой дракона не взять — рыцарей он ест. Нужна хитрость, а хитрость надо сначала приготовить. Награду дают тому, кто победил.",
    "Под Вавельским холмом поселился дракон. Он пожирает скот, а потом и людей, и князь Крак обещает щедрую награду тому, кто избавит город от чудовища. Рыцари в латах идут к пещере один за другим.",
    "В пещере под Вавельским холмом поселился дракон. Сначала он пожирал скот, потом стал требовать людей, и Краков жил в страхе. Князь Крак пообещал руку дочери тому, кто избавит город от чудовища, — и рыцари в сверкающих латах шли к пещере один за другим, но никто не вернулся. Тогда бедный сапожник Скуба взял барана, набил его шкуру серой и смолой, зашил и подбросил к пещере. Дракон проглотил его целиком — и в брюхе у него загорелся огонь. Чудовище бросилось к Висле и пило, пило, пило, пока не лопнуло. Скуба получил в жёны княжну, а пещеру — Смочу Яму — показывают под Вавелем до сих пор; у входа в неё стоит дракон, который выдыхает настоящий огонь.",
    "Винцентий Кадлубек, «Хроника», I, 5; Мартин Бельский, «Хроника польская» (XVI в.)"))

if __name__ == "__main__":
    P.NEW_CHARS, P.NEW_SCENES, P.NEW_RULES, P.NEW_LEVELS, P.TEXTS = NEW_CHARS, NEW_SCENES, NEW_RULES, NEW_LEVELS, TEXTS
    P.CHAPTER_TEXTS = {}
    P.main()
