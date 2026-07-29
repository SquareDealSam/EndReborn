#!/usr/bin/env python3
"""Stage 3 - remaining mobs: seed 64x64 entity textures, lang, and build rigged +
animated Blockbench models (one tab each) matching the Java models.

Run:  python tools/stage3_mobs.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
ENT = os.path.join(RES, "assets", "endreborn", "textures", "entity")

# name -> (display, base, accent, groups[(name,origin,from,to)], animation)
MOBS = {
    "chorus_sprite": ("Chorus Sprite", "#8b3fa0", "#d9a6ff", [
        ("body", [0, 5, 0], [-1.5, 3.5, -1.5], [1.5, 6.5, 1.5]),
        ("left_wing", [1.5, 5, 0], [1.5, 4.5, -1.5], [5.5, 5.5, 1.5]),
        ("right_wing", [-1.5, 5, 0], [-5.5, 4.5, -1.5], [-1.5, 5.5, 1.5]),
    ], {"name": "flap", "loop": True, "animation_length": 0.6, "bones": {
        "left_wing": [{"time": 0, "rotation": [0, 0, -55]}, {"time": 0.3, "rotation": [0, 0, 55]}, {"time": 0.6, "rotation": [0, 0, -55]}],
        "right_wing": [{"time": 0, "rotation": [0, 0, 55]}, {"time": 0.3, "rotation": [0, 0, -55]}, {"time": 0.6, "rotation": [0, 0, 55]}]}}),

    "crystal_strider": ("Crystal Strider", "#6f7fb0", "#a6e8ff", [
        ("body", [0, 8, 0], [-3, 6, -5], [3, 12, 5]),
        ("leg0", [2, 6, -3], [1, 0, -4], [3, 6, -2]),
        ("leg1", [-2, 6, -3], [-3, 0, -4], [-1, 6, -2]),
        ("leg2", [2, 6, 3], [1, 0, 2], [3, 6, 4]),
        ("leg3", [-2, 6, 3], [-3, 0, 2], [-1, 6, 4]),
    ], {"name": "walk", "loop": True, "animation_length": 0.8, "bones": {
        "leg0": [{"time": 0, "rotation": [30, 0, 0]}, {"time": 0.4, "rotation": [-30, 0, 0]}, {"time": 0.8, "rotation": [30, 0, 0]}],
        "leg3": [{"time": 0, "rotation": [30, 0, 0]}, {"time": 0.4, "rotation": [-30, 0, 0]}, {"time": 0.8, "rotation": [30, 0, 0]}],
        "leg1": [{"time": 0, "rotation": [-30, 0, 0]}, {"time": 0.4, "rotation": [30, 0, 0]}, {"time": 0.8, "rotation": [-30, 0, 0]}],
        "leg2": [{"time": 0, "rotation": [-30, 0, 0]}, {"time": 0.4, "rotation": [30, 0, 0]}, {"time": 0.8, "rotation": [-30, 0, 0]}]}}),

    "void_wraith": ("Void Wraith", "#241a33", "#6a4f9e", [
        ("body", [0, 8, 0], [-3, 2, -2], [3, 14, 2]),
        ("head", [0, 15, 0], [-2.5, 14, -2.5], [2.5, 19, 2.5]),
        ("left_arm", [3, 12, 0], [3, 11, -1], [10, 13, 1]),
        ("right_arm", [-3, 12, 0], [-10, 11, -1], [-3, 13, 1]),
    ], {"name": "float", "loop": True, "animation_length": 1.4, "bones": {
        "left_arm": [{"time": 0, "rotation": [0, 0, -25]}, {"time": 0.7, "rotation": [0, 0, -5]}, {"time": 1.4, "rotation": [0, 0, -25]}],
        "right_arm": [{"time": 0, "rotation": [0, 0, 25]}, {"time": 0.7, "rotation": [0, 0, 5]}, {"time": 1.4, "rotation": [0, 0, 25]}]}}),

    "obsidian_golem": ("Obsidian Golem", "#141020", "#3a2f52", [
        ("body", [0, 12, 0], [-6, 8, -4], [6, 24, 4]),
        ("head", [0, 24, 0], [-3, 24, -3], [3, 28, 3]),
        ("left_arm", [6, 22, 0], [6, 8, -2], [10, 24, 2]),
        ("right_arm", [-6, 22, 0], [-10, 8, -2], [-6, 24, 2]),
        ("leg0", [3, 8, 0], [1, 0, -2], [5, 8, 2]),
        ("leg1", [-3, 8, 0], [-5, 0, -2], [-1, 8, 2]),
    ], {"name": "stomp", "loop": True, "animation_length": 1.0, "bones": {
        "leg0": [{"time": 0, "rotation": [25, 0, 0]}, {"time": 0.5, "rotation": [-25, 0, 0]}, {"time": 1.0, "rotation": [25, 0, 0]}],
        "leg1": [{"time": 0, "rotation": [-25, 0, 0]}, {"time": 0.5, "rotation": [25, 0, 0]}, {"time": 1.0, "rotation": [-25, 0, 0]}]}}),

    "abyss_stalker": ("Abyss Stalker", "#0d0a16", "#4a2f6a", [
        ("body", [0, 6, 0], [-3, 4, -6], [3, 8, 6]),
        ("leg0", [3, 6, -4], [3, 1, -5], [8, 6, -3]),
        ("leg1", [-3, 6, -4], [-8, 1, -5], [-3, 6, -3]),
        ("leg2", [3, 6, 4], [3, 1, 3], [8, 6, 5]),
        ("leg3", [-3, 6, 4], [-8, 1, 3], [-3, 6, 5]),
    ], {"name": "skitter", "loop": True, "animation_length": 0.5, "bones": {
        "leg0": [{"time": 0, "rotation": [0, 0, 30]}, {"time": 0.25, "rotation": [0, 0, 50]}, {"time": 0.5, "rotation": [0, 0, 30]}],
        "leg3": [{"time": 0, "rotation": [0, 0, 30]}, {"time": 0.25, "rotation": [0, 0, 50]}, {"time": 0.5, "rotation": [0, 0, 30]}],
        "leg1": [{"time": 0, "rotation": [0, 0, -30]}, {"time": 0.25, "rotation": [0, 0, -50]}, {"time": 0.5, "rotation": [0, 0, -30]}],
        "leg2": [{"time": 0, "rotation": [0, 0, -30]}, {"time": 0.25, "rotation": [0, 0, -50]}, {"time": 0.5, "rotation": [0, 0, -30]}]}}),

    "crystal_sentinel": ("Crystal Sentinel", "#4a6f96", "#8fe6ff", [
        ("core", [0, 10, 0], [-3, 7, -3], [3, 13, 3]),
        ("shards", [0, 10, 0], [-0.5, 8, 4], [0.5, 12, 5]),
    ], {"name": "hover", "loop": True, "animation_length": 2.0, "bones": {
        "shards": [{"time": 0, "rotation": [0, 0, 0]}, {"time": 1.0, "rotation": [0, 180, 0]}, {"time": 2.0, "rotation": [0, 360, 0]}]}}),
}


def main():
    lang_path = os.path.join(RES, "assets", "endreborn", "lang", "en_us.json")
    lang = json.load(open(lang_path))
    imgs = {}
    for name, (disp, base, accent, *_rest) in MOBS.items():
        img = T.entity_sheet(base, accent, name)
        imgs[name] = img
        T.save(img, os.path.join(ENT, name + ".png"))
        lang[f"entity.endreborn.{name}"] = disp
    json.dump(lang, open(lang_path, "w"), indent=2)
    print(f"seeded {len(MOBS)} entity textures + lang")

    bb = BB()
    for name, (disp, base, accent, groups, anim) in MOBS.items():
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
