#!/usr/bin/env python3
"""Stage 5 - structures: build 5 jigsaw single-piece structures (NBT templates) +
structure/structure_set/template_pool JSON + populated chest loot tables.

Run:  python tools/stage5_structures.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from nbt import Structure

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
WG = "data/voidweaver/worldgen"
E = "voidweaver"


def writej(rel, obj):
    p = os.path.join(RES, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)


def save_nbt(name, structure):
    structure.save(os.path.join(RES, "data", E, "structure", name + ".nbt"))


# ---------- JSON scaffolding for one structure ----------
def structure_json(name, biomes, salt, spacing, separation, step="surface_structures",
                   spawn_overrides=None):
    writej(f"{WG}/structure/{name}.json", {
        "type": "minecraft:jigsaw",
        "biomes": [f"{E}:{b}" for b in biomes],
        "step": step,
        "size": 1,
        "start_pool": f"{E}:{name}/start",
        "start_height": {"absolute": 0},
        "project_start_to_heightmap": "WORLD_SURFACE_WG",
        "max_distance_from_center": 80,
        "use_expansion_hack": False,
        "terrain_adaptation": "beard_thin",
        "spawn_overrides": spawn_overrides or {}})
    writej(f"{WG}/template_pool/{name}/start.json", {
        "name": f"{E}:{name}/start",
        "fallback": "minecraft:empty",
        "elements": [{"weight": 1, "element": {
            "element_type": "minecraft:single_pool_element",
            "location": f"{E}:{name}",
            "processors": "minecraft:empty",
            "projection": "rigid"}}]})
    writej(f"{WG}/structure_set/{name}.json", {
        "structures": [{"structure": f"{E}:{name}", "weight": 1}],
        "placement": {"type": "minecraft:random_spread",
                      "spacing": spacing, "separation": separation, "salt": salt}})


def uni(lo, hi):
    return {"type": "minecraft:uniform", "min": lo, "max": hi}


def chest_loot(name, rolls, entries):
    writej(f"data/{E}/loot_table/chests/{name}.json", {
        "type": "minecraft:chest",
        "pools": [{"rolls": rolls, "entries": [
            {"type": "minecraft:item", "name": it, "weight": w,
             "functions": [{"function": "minecraft:set_count", "count": uni(cl, ch)}]}
            for (it, w, cl, ch) in entries]}]})


# ---------- the five structures ----------
def build():
    # 1) Void Sanctum — sealed void-stone dungeon with a mini-boss + loot.
    s = Structure()
    s.hollow(0, 0, 0, 10, 6, 10, f"{E}:void_stone_bricks")
    for (cx, cz) in [(2, 2), (8, 8), (2, 8), (8, 2)]:
        s.fill(cx, 1, cz, cx, 4, cz, f"{E}:crystal_stone")
    s.chest(3, 1, 5, f"{E}:chests/void_sanctum")
    s.chest(7, 1, 5, f"{E}:chests/void_sanctum")
    s.entity(5, 1, 5, f"{E}:obsidian_golem")
    save_nbt("void_sanctum", s)
    structure_json("void_sanctum", ["void_gardens", "shattered_barrens"], 74100001, 24, 8)
    chest_loot("void_sanctum", uni(3, 6), [
        (f"{E}:chorus_alloy_ingot", 10, 1, 3), (f"{E}:crystal_shard", 12, 2, 5),
        (f"{E}:void_crystal", 3, 1, 1), (f"{E}:chorus_planks", 8, 3, 8),
        ("minecraft:ender_pearl", 6, 1, 2)])

    # 2) Crystal Spire — tall climb, Chorus Guardian at the top.
    s = Structure()
    s.hollow(0, 0, 0, 6, 24, 6, f"{E}:crystal_stone")
    for fy in (6, 12, 18):                       # interior floors
        s.fill(1, fy, 1, 5, fy, 5, f"{E}:crystal_stone_bricks")
    s.chest(1, 7, 1, f"{E}:chests/crystal_spire")
    s.chest(5, 13, 5, f"{E}:chests/crystal_spire")
    s.entity(3, 19, 3, f"{E}:chorus_guardian")
    save_nbt("crystal_spire", s)
    structure_json("crystal_spire", ["crystal_highlands"], 74100002, 40, 12)
    chest_loot("crystal_spire", uni(3, 5), [
        (f"{E}:crystal_shard", 14, 3, 8), (f"{E}:void_crystal", 5, 1, 2),
        (f"{E}:crystal_stone", 10, 4, 12), (f"{E}:chorus_alloy_pickaxe", 3, 1, 1)])

    # 3) Sunken Ruins — obsidian vault, dense loot.
    s = Structure()
    s.hollow(0, 0, 0, 8, 5, 8, f"{E}:obsidian_bricks")
    s.chest(2, 1, 2, f"{E}:chests/sunken_ruins")
    s.chest(6, 1, 6, f"{E}:chests/sunken_ruins")
    s.chest(2, 1, 6, f"{E}:chests/sunken_ruins")
    save_nbt("sunken_ruins", s)
    structure_json("sunken_ruins", ["obsidian_wastes"], 74100003, 26, 8)
    chest_loot("sunken_ruins", uni(4, 7), [
        (f"{E}:obsidian", 12, 2, 6), (f"{E}:void_crystal", 6, 1, 3),
        (f"{E}:chorus_alloy_ingot", 10, 2, 5), ("minecraft:obsidian", 8, 2, 6)])

    # 4) Abyss Temple — Voidbringer arena, best-in-mod chests.
    s = Structure()
    s.fill(0, 0, 0, 14, 0, 14, f"{E}:void_stone")
    s.hollow(0, 0, 0, 14, 8, 14, f"{E}:obsidian_bricks")
    for (cx, cz) in [(3, 3), (11, 11), (3, 11), (11, 3)]:
        s.fill(cx, 1, cz, cx, 7, cz, f"{E}:obsidian")
        s.chest(cx, 1, cz + 1 if cz < 7 else cz - 1, f"{E}:chests/abyss_temple")
    s.entity(7, 1, 7, f"{E}:voidbringer")
    save_nbt("abyss_temple", s)
    structure_json("abyss_temple", ["endless_abyss"], 74100004, 48, 16,
                   spawn_overrides={"monster": {"bounding_box": "full", "spawns": []}})
    chest_loot("abyss_temple", uni(4, 6), [
        (f"{E}:void_crystal", 14, 3, 8), (f"{E}:void_crystal_sword", 3, 1, 1),
        (f"{E}:void_crystal_helmet", 2, 1, 1), (f"{E}:chorus_alloy_block", 6, 1, 2),
        (f"{E}:void_crystal_block", 4, 1, 1)])

    # 5) End Outpost — small early-game hut.
    s = Structure()
    s.hollow(0, 0, 0, 4, 4, 4, f"{E}:chorus_planks")
    s.fill(1, 4, 1, 3, 4, 3, f"{E}:chorus_planks")
    s.chest(2, 1, 2, f"{E}:chests/end_outpost")
    save_nbt("end_outpost", s)
    structure_json("end_outpost",
                   ["void_gardens", "chorus_jungle", "crystal_highlands", "shattered_barrens"],
                   74100005, 18, 6)
    chest_loot("end_outpost", uni(2, 4), [
        (f"{E}:chorus_planks", 12, 4, 10), (f"{E}:chorus_alloy_ingot", 8, 1, 2),
        (f"{E}:crystal_shard", 10, 1, 3), ("minecraft:ender_pearl", 5, 1, 1)])


def main():
    build()
    # sanity: re-read each NBT gzip and confirm the root keys exist
    import gzip
    struct_dir = os.path.join(RES, "data", E, "structure")
    for f in sorted(os.listdir(struct_dir)):
        raw = gzip.open(os.path.join(struct_dir, f), "rb").read()
        ok = all(k in raw for k in (b"size", b"palette", b"blocks", b"DataVersion"))
        print(f"  {f}: {len(raw)} bytes gunzipped, keys_ok={ok}")
    print("built 5 structures + JSON + loot")


if __name__ == "__main__":
    main()
