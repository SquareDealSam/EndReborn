#!/usr/bin/env python3
"""Stage 2 - Chorus wood set (sign & boat deferred to the entity stage).

7 NEW textures, each in its own new Blockbench tab, + all wood JSON.
Run:  python tools/stage2_wood.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
import mcjson as J
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
TEX = os.path.join(RES, "assets", "endreborn", "textures")
PLANK = "chorus_planks"
WOOD = "#7a4a86"

NEW_TEX = [
    ("block", "stripped_chorus_log",     T.log_side("#6a4f78", "#7a5f88", "stripped_chorus_log")),
    ("block", "stripped_chorus_log_top", T.log_top("#8a6a98", "#6a4f78", "stripped_chorus_log_top")),
    ("block", "chorus_door_bottom",      T.door_panel(WOOD, "chorus_door_bottom", top=False)),
    ("block", "chorus_door_top",         T.door_panel(WOOD, "chorus_door_top", top=True)),
    ("item",  "chorus_door",             T.door_item(WOOD, "chorus_door")),
    ("block", "chorus_trapdoor",         T.trapdoor_tex(WOOD, "chorus_trapdoor")),
    ("block", "chorus_leaves",           T.leaves_tex("#8b3fa0", "chorus_leaves")),
]


def writej(rel, obj):
    p = os.path.join(RES, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)


def title(name):
    return " ".join(w.capitalize() for w in name.split("_"))


def loot_door(name):
    return (f"data/endreborn/loot_table/blocks/{name}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"endreborn:{name}"}],
                   "conditions": [{"condition": "minecraft:survives_explosion"},
                                  {"condition": "minecraft:block_state_property",
                                   "block": f"endreborn:{name}",
                                   "properties": {"half": "lower"}}]}]})


def main():
    for sub, name, img in NEW_TEX:
        T.save(img, os.path.join(TEX, sub, name + ".png"))
    bb = BB()
    for sub, name, img in NEW_TEX:
        bb.call("create_project", {"name": name, "format": "java_block"})  # new tab
        bb.call("create_texture", {"name": name, "data": T.to_data_url(img)})
        if sub == "block":
            bb.call("place_cube", {"elements": [{"name": name, "from": [0, 0, 0],
                     "to": [16, 16, 16], "origin": [8, 8, 8]}], "texture": name, "faces": True})
        print(f"  tab+texture -> {name}")

    lang_path = os.path.join(RES, "assets", "endreborn", "lang", "en_us.json")
    lang = json.load(open(lang_path))

    def emit(files, loot=None):
        for rel, obj in files:
            writej(rel, obj)
        if loot:
            writej(*loot)

    emit(J.cube_column("stripped_chorus_log", "stripped_chorus_log", "stripped_chorus_log_top"), J.loot_self("stripped_chorus_log"))
    emit(J.cube_column("chorus_wood", "chorus_log", "chorus_log"), J.loot_self("chorus_wood"))
    emit(J.cube_column("stripped_chorus_wood", "stripped_chorus_log", "stripped_chorus_log"), J.loot_self("stripped_chorus_wood"))
    emit(J.stairs("chorus_stairs", PLANK), J.loot_self("chorus_stairs"))
    emit(J.slab("chorus_slab", PLANK, "chorus_planks"), J.loot_slab("chorus_slab"))
    emit(J.fence("chorus_fence", PLANK), J.loot_self("chorus_fence"))
    emit(J.fence_gate("chorus_fence_gate", PLANK), J.loot_self("chorus_fence_gate"))
    emit(J.door("chorus_door"), loot_door("chorus_door"))
    emit(J.trapdoor("chorus_trapdoor", "chorus_trapdoor"), J.loot_self("chorus_trapdoor"))
    emit(J.pressure_plate("chorus_pressure_plate", PLANK), J.loot_self("chorus_pressure_plate"))
    emit(J.button("chorus_button", PLANK), J.loot_self("chorus_button"))
    emit(J.leaves("chorus_leaves", "chorus_leaves"), J.loot_self("chorus_leaves"))

    wood_blocks = ["chorus_log", "stripped_chorus_log", "chorus_wood", "stripped_chorus_wood",
                   "chorus_planks", "chorus_stairs", "chorus_slab", "chorus_fence",
                   "chorus_fence_gate", "chorus_door", "chorus_trapdoor",
                   "chorus_pressure_plate", "chorus_button", "chorus_leaves"]
    for name in wood_blocks:
        lang[f"block.endreborn.{name}"] = title(name)
    lang["item.endreborn.chorus_door"] = "Chorus Door"

    # merge axe-mineable tag
    axe_path = "data/minecraft/tags/block/mineable/axe.json"
    axe_full = os.path.join(RES, axe_path)
    axe = json.load(open(axe_full)) if os.path.exists(axe_full) else {"replace": False, "values": []}
    for name in wood_blocks:
        v = f"endreborn:{name}"
        if v not in axe["values"]:
            axe["values"].append(v)
    writej(axe_path, {"replace": False, "values": sorted(axe["values"])})

    json.dump(lang, open(lang_path, "w"), indent=2)
    print(f"emitted wood set: {len(wood_blocks)} blocks + door item.")


if __name__ == "__main__":
    main()
