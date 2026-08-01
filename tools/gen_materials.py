#!/usr/bin/env python3
"""Stage 2 driver: generate EndReborn material textures, save into mod resources,
and mirror them live into the running Blockbench workspace (textures + cubes).

Run:  python tools/gen_materials.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources",
                   "assets", "voidweaver", "textures")

# (dest_subdir, name, PIL image, is_block_cube)
def catalog():
    return [
        ("block", "void_stone",        T.stone("#2b2340", "void_stone"),                 True),
        ("block", "crystal_stone",     T.stone("#5f6f96", "crystal_stone"),              True),
        ("block", "obsidian_bricks",   T.bricks("#141020", "#241c36", "obsidian_bricks"),True),
        ("block", "chorus_ore",        T.ore("#dcdcae", "#b048d8", "chorus_ore"),        True),
        ("block", "void_crystal_ore",  T.ore("#241d33", "#57e8ff", "void_crystal_ore"),  True),
        ("block", "chorus_planks",     T.planks("#7a4a86", "chorus_planks"),             True),
        ("block", "chorus_log",        T.log_side("#42304f", "#5a4168", "chorus_log"),   True),
        ("block", "chorus_log_top",    T.log_top("#7a4a86", "#4a2f57", "chorus_log_top"),False),
        ("item",  "chorus_alloy_ingot",T.ingot("#4fb39a", "chorus_alloy_ingot"),         False),
        ("item",  "void_crystal",      T.gem("#57e8ff", "void_crystal"),                 False),
        ("item",  "crystal_shard",     T.shard("#8fe6ff", "crystal_shard"),              False),
    ]


def main():
    items = catalog()

    # 1) Save PNGs into the mod resources.
    for sub, name, img, _ in items:
        path = os.path.join(RES, sub, name + ".png")
        T.save(img, path)
        print(f"saved  {sub}/{name}.png")

    # 2) Mirror into Blockbench live.
    bb = BB()
    bb.call("create_project", {"name": "EndReborn Materials", "format": "java_block"})
    print("created Blockbench project 'EndReborn Materials'")

    for sub, name, img, _ in items:
        bb.call("create_texture", {"name": name, "data": T.to_data_url(img)})
        print(f"  texture -> {name}")

    # 3) Place a cube per block texture, spaced in a row so they're all visible.
    x = 0
    for sub, name, img, is_cube in items:
        if not is_cube:
            continue
        bb.call("place_cube", {
            "elements": [{"name": name, "from": [x, 0, 0], "to": [x + 16, 16, 16],
                          "origin": [x + 8, 8, 8]}],
            "texture": name,
            "faces": True,
        })
        print(f"  cube    -> {name} @ x={x}")
        x += 24

    print("\nStage-2 slice mirrored into Blockbench. Check your workspace.")


if __name__ == "__main__":
    main()
