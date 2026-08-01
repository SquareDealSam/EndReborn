#!/usr/bin/env python3
"""Stage 3 - Void Moth: seed entity texture, add lang, and build a rigged +
animated model in Blockbench (matching the Java model) for live refinement.

Run:  python tools/stage3_voidmoth.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")


def main():
    img = T.entity_moth("#3a2d5c", "#7a4fb0", "void_moth")
    T.save(img, os.path.join(RES, "assets", "voidweaver", "textures", "entity", "void_moth.png"))

    lang_path = os.path.join(RES, "assets", "voidweaver", "lang", "en_us.json")
    lang = json.load(open(lang_path))
    lang["entity.voidweaver.void_moth"] = "Void Moth"
    json.dump(lang, open(lang_path, "w"), indent=2)
    print("seeded void_moth texture + lang")

    bb = BB()
    bb.call("create_project", {"name": "void_moth", "format": "modded_entity"})
    bb.call("create_texture", {"name": "void_moth", "data": T.to_data_url(img)})
    bb.call("add_group", {"name": "body", "origin": [0, 5, 0], "rotation": [0, 0, 0]})
    bb.call("add_group", {"name": "left_wing", "origin": [2, 5, 0], "rotation": [0, 0, 0]})
    bb.call("add_group", {"name": "right_wing", "origin": [-2, 5, 0], "rotation": [0, 0, 0]})
    bb.call("place_cube", {"elements": [{"name": "body", "from": [-2, 3, -3], "to": [2, 7, 3],
             "origin": [0, 5, 0]}], "group": "body", "texture": "void_moth", "faces": True})
    bb.call("place_cube", {"elements": [{"name": "left_wing", "from": [2, 4.5, -3], "to": [8, 5.5, 3],
             "origin": [2, 5, 0]}], "group": "left_wing", "texture": "void_moth", "faces": True})
    bb.call("place_cube", {"elements": [{"name": "right_wing", "from": [-8, 4.5, -3], "to": [-2, 5.5, 3],
             "origin": [-2, 5, 0]}], "group": "right_wing", "texture": "void_moth", "faces": True})
    print("built rigged void_moth model in Blockbench")

    try:
        bb.call("create_animation", {
            "name": "flap", "loop": True, "animation_length": 0.75,
            "bones": {
                "left_wing": [{"time": 0, "rotation": [0, 0, -50]},
                              {"time": 0.375, "rotation": [0, 0, 55]},
                              {"time": 0.75, "rotation": [0, 0, -50]}],
                "right_wing": [{"time": 0, "rotation": [0, 0, 50]},
                               {"time": 0.375, "rotation": [0, 0, -55]},
                               {"time": 0.75, "rotation": [0, 0, 50]}],
            }})
        print("created 'flap' animation in Blockbench")
    except Exception as e:
        print("animation skipped:", e)


if __name__ == "__main__":
    main()
