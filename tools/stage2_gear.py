#!/usr/bin/env python3
"""Stage 2 - materials: storage blocks, tools, and armor for both tiers.

Every new texture -> its own new Blockbench tab. Emits item/equipment/tag/lang JSON.
Run:  python tools/stage2_gear.py
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

MATS = {"chorus_alloy": "#4fb39a", "void_crystal": "#57e8ff"}
TOOLS = ["sword", "pickaxe", "axe", "shovel", "hoe"]
ARMOR = ["helmet", "chestplate", "leggings", "boots"]


def writej(rel, obj):
    p = os.path.join(RES, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)


def title(name):
    return " ".join(w.capitalize() for w in name.split("_"))


def build_textures():
    """Return list of (abs_save_path, tab_name, image, is_block_cube)."""
    out = []
    # storage blocks
    out.append((os.path.join(TEX, "block", "chorus_alloy_block.png"), "chorus_alloy_block",
                T.metal_block(MATS["chorus_alloy"], "chorus_alloy_block"), True))
    out.append((os.path.join(TEX, "block", "void_crystal_block.png"), "void_crystal_block",
                T.crystal_block(MATS["void_crystal"], "void_crystal_block"), True))
    for mat, color in MATS.items():
        for k in TOOLS:
            n = f"{mat}_{k}"
            out.append((os.path.join(TEX, "item", n + ".png"), n, T.tool(k, color, n), False))
        for k in ARMOR:
            n = f"{mat}_{k}"
            out.append((os.path.join(TEX, "item", n + ".png"), n, T.armor_icon(k, color, n), False))
        # equipment layer sheets (64x32)
        out.append((os.path.join(TEX, "entity", "equipment", "humanoid", mat + ".png"),
                    mat + "_layer", T.armor_layer(color, mat + "_layer"), False))
        out.append((os.path.join(TEX, "entity", "equipment", "humanoid_leggings", mat + ".png"),
                    mat + "_leggings_layer", T.armor_layer(color, mat + "_leg"), False))
    return out


def main():
    tex = build_textures()
    for path, _, img, _ in tex:
        T.save(img, path)
    bb = BB()
    for path, tabname, img, is_block in tex:
        bb.call("create_project", {"name": tabname, "format": "java_block"})  # new tab
        bb.call("create_texture", {"name": tabname, "data": T.to_data_url(img)})
        if is_block:
            bb.call("place_cube", {"elements": [{"name": tabname, "from": [0, 0, 0],
                     "to": [16, 16, 16], "origin": [8, 8, 8]}], "texture": tabname, "faces": True})
        print(f"  tab+texture -> {tabname}")

    lang = json.load(open(os.path.join(RES, "assets", "endreborn", "lang", "en_us.json")))

    # storage blocks
    for name in ("chorus_alloy_block", "void_crystal_block"):
        for rel, obj in J.cube_all(name, name):
            writej(rel, obj)
        writej(*J.loot_self(name))
        lang[f"block.endreborn.{name}"] = title(name)

    # tools + armor item models + lang
    for mat in MATS:
        for k in TOOLS:
            n = f"{mat}_{k}"
            for rel, obj in J.item_handheld(n):
                writej(rel, obj)
            lang[f"item.endreborn.{n}"] = title(n)
        for k in ARMOR:
            n = f"{mat}_{k}"
            for rel, obj in J.item_generated(n):
                writej(rel, obj)
            lang[f"item.endreborn.{n}"] = title(n)
        # equipment definition
        writej(f"assets/endreborn/equipment/{mat}.json",
               {"layers": {"humanoid": [{"texture": f"endreborn:{mat}"}],
                           "humanoid_leggings": [{"texture": f"endreborn:{mat}"}]}})
    # material item lang (models already exist from the slice)
    lang["item.endreborn.chorus_alloy_ingot"] = "Chorus Alloy Ingot"
    lang["item.endreborn.void_crystal"] = "Void Crystal"
    lang["item.endreborn.crystal_shard"] = "Crystal Shard"

    # repair tags
    writej("data/endreborn/tags/item/chorus_alloy_repair.json",
           {"replace": False, "values": ["endreborn:chorus_alloy_ingot"]})
    writej("data/endreborn/tags/item/void_crystal_repair.json",
           {"replace": False, "values": ["endreborn:void_crystal"]})

    # merge storage blocks into mining tags
    def merge(path, adds):
        full = os.path.join(RES, path)
        d = json.load(open(full)) if os.path.exists(full) else {"replace": False, "values": []}
        vals = set(d.get("values", [])) | set(adds)
        writej(path, {"replace": False, "values": sorted(vals)})

    merge("data/minecraft/tags/block/mineable/pickaxe.json",
          ["endreborn:chorus_alloy_block", "endreborn:void_crystal_block"])
    merge("data/minecraft/tags/block/needs_iron_tool.json", ["endreborn:chorus_alloy_block"])
    merge("data/minecraft/tags/block/needs_diamond_tool.json", ["endreborn:void_crystal_block"])

    json.dump(lang, open(os.path.join(RES, "assets", "endreborn", "lang", "en_us.json"), "w"), indent=2)
    print("emitted gear: 2 storage blocks, 10 tools, 8 armor, 2 equipment defs, repair tags.")


if __name__ == "__main__":
    main()
