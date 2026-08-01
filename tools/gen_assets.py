#!/usr/bin/env python3
"""Emit the client/data JSON for the current material slice: blockstates, block &
item models, en_us lang, and self-drop loot tables. Kept in Python alongside the
texture generator so the asset set scales; recipes/tags move to Fabric datagen later.

Run:  python tools/gen_assets.py
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
A = os.path.join(ROOT, "assets", "voidweaver")
D = os.path.join(ROOT, "data", "voidweaver")

# name -> display name. Blocks with a full-cube model use "cube_all".
CUBE_BLOCKS = {
    "void_stone": "Void Stone",
    "crystal_stone": "Crystal Stone",
    "obsidian_bricks": "Obsidian Bricks",
    "chorus_ore": "Chorus Ore",
    "void_crystal_ore": "Void Crystal Ore",
    "chorus_planks": "Chorus Planks",
    "chorus_log": "Chorus Log",  # temporary cube_all; becomes a pillar in the wood set
}
ITEMS = {
    "chorus_alloy_ingot": "Chorus Alloy Ingot",
    "void_crystal": "Void Crystal",
    "crystal_shard": "Crystal Shard",
}


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def main():
    lang = {"itemGroup.voidweaver": "EndReborn"}

    for name, disp in CUBE_BLOCKS.items():
        tex = f"voidweaver:block/{name}"
        w(os.path.join(A, "blockstates", f"{name}.json"),
          {"variants": {"": {"model": f"voidweaver:block/{name}"}}})
        w(os.path.join(A, "models", "block", f"{name}.json"),
          {"parent": "minecraft:block/cube_all", "textures": {"all": tex}})
        w(os.path.join(A, "models", "item", f"{name}.json"),
          {"parent": f"voidweaver:block/{name}"})
        w(os.path.join(D, "loot_table", "blocks", f"{name}.json"),
          self_drop(name))
        lang[f"block.voidweaver.{name}"] = disp

    for name, disp in ITEMS.items():
        w(os.path.join(A, "models", "item", f"{name}.json"),
          {"parent": "minecraft:item/generated",
           "textures": {"layer0": f"voidweaver:item/{name}"}})
        lang[f"item.voidweaver.{name}"] = disp

    w(os.path.join(A, "lang", "en_us.json"), lang)
    print(f"wrote {len(CUBE_BLOCKS)} block asset sets + {len(ITEMS)} item models + lang")


def self_drop(name):
    return {
        "type": "minecraft:block",
        "pools": [{
            "rolls": 1,
            "entries": [{"type": "minecraft:item", "name": f"voidweaver:{name}"}],
            "conditions": [{"condition": "minecraft:survives_explosion"}],
        }],
    }


if __name__ == "__main__":
    main()
