#!/usr/bin/env python3
"""Stage 3 - bosses: seed textures + lang + loot tables, and build rigged, animated
Blockbench models (one tab each).

Run:  python tools/stage3_bosses.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
ENT = os.path.join(RES, "assets", "voidweaver", "textures", "entity")


def writej(rel, obj):
    p = os.path.join(RES, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)


def uniform(lo, hi):
    return {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}


def item(name, funcs=None):
    e = {"type": "minecraft:item", "name": f"voidweaver:{name}"}
    if funcs:
        e["functions"] = funcs
    return e


BOSSES = {
    "chorus_guardian": ("Chorus Guardian", "#7a4fb0", "#b9e8ff", [
        ("core", [0, 10, 0], [-4, 2, -4], [4, 16, 4]),
        ("arm0", [4, 8, 0], [4, 7, -1], [13, 9, 1]),
        ("arm1", [-4, 8, 0], [-13, 7, -1], [-4, 9, 1]),
        ("arm2", [0, 8, 4], [-1, 7, 4], [1, 9, 13]),
        ("arm3", [0, 8, -4], [-1, 7, -13], [1, 9, -4]),
    ], {"name": "spin", "loop": True, "animation_length": 3.0, "bones": {
        "core": [{"time": 0, "rotation": [0, 0, 0]}, {"time": 1.5, "rotation": [0, 180, 0]}, {"time": 3.0, "rotation": [0, 360, 0]}],
        "arm0": [{"time": 0, "rotation": [0, 0, -10]}, {"time": 1.5, "rotation": [0, 0, -35]}, {"time": 3.0, "rotation": [0, 0, -10]}],
        "arm1": [{"time": 0, "rotation": [0, 0, 10]}, {"time": 1.5, "rotation": [0, 0, 35]}, {"time": 3.0, "rotation": [0, 0, 10]}]}}),

    "voidbringer": ("The Voidbringer", "#1a1030", "#7a3fd0", [
        ("body", [0, 14, 0], [-5, 2, -3], [5, 20, 3]),
        ("head", [0, 20, 0], [-3, 20, -3], [3, 25, 3]),
        ("left_arm", [5, 18, 0], [5, 4, -2], [9, 20, 2]),
        ("right_arm", [-5, 18, 0], [-9, 4, -2], [-5, 20, 2]),
    ], {"name": "menace", "loop": True, "animation_length": 2.4, "bones": {
        "left_arm": [{"time": 0, "rotation": [-15, 0, -10]}, {"time": 1.2, "rotation": [-60, 0, -25]}, {"time": 2.4, "rotation": [-15, 0, -10]}],
        "right_arm": [{"time": 0, "rotation": [-15, 0, 10]}, {"time": 1.2, "rotation": [-60, 0, 25]}, {"time": 2.4, "rotation": [-15, 0, 10]}],
        "body": [{"time": 0, "rotation": [0, 0, -3]}, {"time": 1.2, "rotation": [0, 0, 3]}, {"time": 2.4, "rotation": [0, 0, -3]}]}}),
}

LOOT = {
    "chorus_guardian": {"type": "minecraft:entity", "pools": [
        {"rolls": 1, "entries": [item("crystal_shard", [uniform(4, 8)])]},
        {"rolls": 1, "entries": [item("void_crystal", [uniform(1, 2)])]},
        {"rolls": 1, "entries": [item("crystal_stone", [{"function": "minecraft:set_count", "count": 8}])]},
    ]},
    "voidbringer": {"type": "minecraft:entity", "pools": [
        {"rolls": 1, "entries": [item("void_crystal", [uniform(4, 8)])]},
        {"rolls": 1, "entries": [item("chorus_alloy_ingot", [uniform(3, 6)])]},
        {"rolls": 1, "entries": [item("void_crystal_sword")]},
        {"rolls": 1, "entries": [item("void_crystal_block", [uniform(1, 2)])]},
    ]},
}


def main():
    lang_path = os.path.join(RES, "assets", "voidweaver", "lang", "en_us.json")
    lang = json.load(open(lang_path))
    imgs = {}
    for name, (disp, base, accent, *_r) in BOSSES.items():
        img = T.entity_sheet(base, accent, name)
        imgs[name] = img
        T.save(img, os.path.join(ENT, name + ".png"))
        lang[f"entity.voidweaver.{name}"] = disp
        writej(f"data/voidweaver/loot_table/entities/{name}.json", LOOT[name])
    json.dump(lang, open(lang_path, "w"), indent=2)
    print("seeded 2 boss textures + lang + loot tables")

    bb = BB()
    for name, (disp, base, accent, groups, anim) in BOSSES.items():
        bb.call("create_project", {"name": name, "format": "modded_entity"})
        bb.call("create_texture", {"name": name, "data": T.to_data_url(imgs[name])})
        for gname, origin, frm, to in groups:
            bb.call("add_group", {"name": gname, "origin": origin, "rotation": [0, 0, 0]})
            bb.call("place_cube", {"elements": [{"name": gname, "from": frm, "to": to, "origin": origin}],
                                   "group": gname, "texture": name, "faces": True})
        try:
            bb.call("create_animation", anim)
            print(f"  built + animated -> {name}")
        except Exception as e:
            print(f"  built (anim skipped: {e}) -> {name}")


if __name__ == "__main__":
    main()
