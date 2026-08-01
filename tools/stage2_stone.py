#!/usr/bin/env python3
"""Stage 2 - stone families (void_stone, crystal_stone, obsidian).

Generates the 9 NEW derived textures (each in its OWN new Blockbench tab), saves
PNGs into the mod, and emits every blockstate/model/item-model/loot/lang/tag file
for the full families (+ fixes chorus_log to a pillar and re-emits ores/planks).

Run:  python tools/stage2_stone.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
import mcjson as J
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
TEX = os.path.join(RES, "assets", "voidweaver", "textures")

FAMILIES = {
    "void_stone":    dict(base="#2b2340", polish="#33294d", chisel="#4a3d63", brick="#3c3357", tier="iron"),
    "crystal_stone": dict(base="#5f6f96", polish="#6b7ba6", chisel="#8090b8", brick="#4a577a", tier="iron"),
    "obsidian":      dict(base="#0f0c18", polish="#16121f", chisel="#2a2340", brick="#241c36", tier="diamond"),
}
# base texture already exists on disk for these (made in the slice)
BASE_EXISTS = {"void_stone", "crystal_stone"}
# brick texture already exists for these
BRICK_EXISTS = {"obsidian"}  # obsidian_bricks.png from the slice


def new_textures():
    """(texname, PIL image) for every NEW texture this stage introduces."""
    out = []
    for base, c in FAMILIES.items():
        if base not in BASE_EXISTS:
            out.append((base, T.stone(c["base"], base)))
        out.append(("polished_" + base, T.polished(c["polish"], "polished_" + base)))
        out.append(("chiseled_" + base, T.chiseled(c["base"], c["chisel"], "chiseled_" + base)))
        if base not in BRICK_EXISTS:
            out.append((base + "_bricks", T.bricks(c["base"], c["brick"], base + "_bricks")))
    return out


def family_pieces(base):
    br = base + "_bricks"
    return [
        (base, base, "cube"), (base + "_stairs", base, "stairs"),
        (base + "_slab", base, "slab", base), (base + "_wall", base, "wall"),
        ("polished_" + base, "polished_" + base, "cube"),
        ("polished_" + base + "_stairs", "polished_" + base, "stairs"),
        ("polished_" + base + "_slab", "polished_" + base, "slab", "polished_" + base),
        ("polished_" + base + "_wall", "polished_" + base, "wall"),
        ("chiseled_" + base, "chiseled_" + base, "cube"),
        (br, br, "cube"), (br + "_stairs", br, "stairs"),
        (br + "_slab", br, "slab", br), (br + "_wall", br, "wall"),
    ]


def writej(relpath, obj):
    p = os.path.join(RES, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)


def title(name):
    parts = name.split("_")
    # keep natural order: "void_stone_stairs" -> "Void Stone Stairs"
    return " ".join(w.capitalize() for w in parts)


def main():
    # 1) NEW textures -> save + one new Blockbench tab each.
    news = new_textures()
    for name, img in news:
        T.save(img, os.path.join(TEX, "block", name + ".png"))
    bb = BB()
    for name, img in news:
        bb.call("create_project", {"name": name, "format": "java_block"})   # new tab
        bb.call("create_texture", {"name": name, "data": T.to_data_url(img)})
        bb.call("place_cube", {"elements": [{"name": name, "from": [0, 0, 0],
                 "to": [16, 16, 16], "origin": [8, 8, 8]}], "texture": name, "faces": True})
        print(f"  tab+texture -> {name}")

    # 2) JSON for all stone families.
    lang_path = os.path.join(RES, "assets", "voidweaver", "lang", "en_us.json")
    lang = json.load(open(lang_path)) if os.path.exists(lang_path) else {}
    mineable, needs_iron, needs_diamond = [], [], []

    def emit_block(name, texture, kind, dbl=None):
        if kind == "cube":
            files = J.cube_all(name, texture); loot = J.loot_self(name)
        elif kind == "stairs":
            files = J.stairs(name, texture); loot = J.loot_self(name)
        elif kind == "slab":
            files = J.slab(name, texture, dbl); loot = J.loot_slab(name)
        elif kind == "wall":
            files = J.wall(name, texture); loot = J.loot_self(name)
        else:
            raise ValueError(kind)
        for rel, obj in files:
            writej(rel, obj)
        writej(*loot)
        lang[f"block.voidweaver.{name}"] = title(name)

    for base, c in FAMILIES.items():
        for piece in family_pieces(base):
            emit_block(*piece)
            name = piece[0]
            mineable.append(f"voidweaver:{name}")
            (needs_diamond if c["tier"] == "diamond" else needs_iron).append(f"voidweaver:{name}")

    # 3) Fix chorus_log -> pillar; re-emit ores + planks as cube_all.
    for rel, obj in J.cube_column("chorus_log", "chorus_log", "chorus_log_top"):
        writej(rel, obj)
    writej(*J.loot_self("chorus_log"))
    for name in ("chorus_ore", "void_crystal_ore", "chorus_planks"):
        for rel, obj in J.cube_all(name, name):
            writej(rel, obj)
        writej(*J.loot_self(name))
    mineable += ["voidweaver:chorus_ore", "voidweaver:void_crystal_ore"]
    needs_iron.append("voidweaver:chorus_ore")
    needs_diamond.append("voidweaver:void_crystal_ore")

    # 4) Tags: pickaxe-mineable + tool tiers; chorus wood -> axe.
    writej("data/minecraft/tags/block/mineable/pickaxe.json",
           {"replace": False, "values": sorted(set(mineable))})
    writej("data/minecraft/tags/block/mineable/axe.json",
           {"replace": False, "values": ["voidweaver:chorus_log", "voidweaver:chorus_planks"]})
    writej("data/minecraft/tags/block/needs_iron_tool.json",
           {"replace": False, "values": sorted(set(needs_iron))})
    writej("data/minecraft/tags/block/needs_diamond_tool.json",
           {"replace": False, "values": sorted(set(needs_diamond))})

    json.dump(lang, open(lang_path, "w"), indent=2)
    print(f"emitted JSON for {sum(len(family_pieces(b)) for b in FAMILIES)} stone blocks + "
          f"chorus fixes; {len(mineable)} pickaxe entries.")


if __name__ == "__main__":
    main()
