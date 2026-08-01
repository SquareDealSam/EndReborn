#!/usr/bin/env python3
"""Stage 7 - biome overhaul: lush alien vegetation + per-biome ground cover so the
biomes finally look distinct. Adds 7 flora/ground blocks, dense vegetation features
(vegetation_patch re-skins the ground), and rewrites each biome's feature set.

Run:  python tools/stage7_biomes.py   (then register the blocks in ModBlocks + build)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
import mcjson as J

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
TEX = os.path.join(RES, "assets", "voidweaver", "textures", "block")
WG = "data/voidweaver/worldgen"
E = "voidweaver"


def writej(rel, obj):
    p = os.path.join(RES, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)


# ---------------- textures + block assets ----------------
GROUND = {
    "alien_grass_block": T.lush_ground("alien_grass_block", "#356b48", "#57a866", ["#2a6f8a", "#8fe0a0"]),
    "void_moss_block":   T.lush_ground("void_moss_block", "#3a2a5c", "#6a4faa", ["#b070ff", "#44e6ff"]),
}
PLANTS = {  # name -> (image, light)
    "glowstalk":      (T.alien_plant("glowstalk", "stalk", "#2a6a5a", "#46ffcc", glow=True), 13),
    "glow_fungus":    (T.alien_plant("glow_fungus", "fungus", "#6a5330", "#ffd85a", glow=True), 12),
    "giant_bloom":    (T.alien_plant("giant_bloom", "flower", "#3a5a3a", "#ff63b0", glow=False), 6),
    "crystal_flower": (T.alien_plant("crystal_flower", "crystal", "#4a6a8a", "#93f2ff", glow=True), 9),
    "void_fern":      (T.alien_plant("void_fern", "fern", "#3a2a4a", "#7a53a0", glow=False), 0),
}


def build_blocks():
    lang_path = os.path.join(RES, "assets", "voidweaver", "lang", "en_us.json")
    lang = json.load(open(lang_path))
    for name, img in GROUND.items():
        T.save(img, os.path.join(TEX, name + ".png"))
        for rel, obj in J.cube_all(name, name):
            writej(rel, obj)
        writej(*J.loot_self(name))
        lang[f"block.{E}.{name}"] = " ".join(w.capitalize() for w in name.split("_"))
    for name, (img, _light) in PLANTS.items():
        T.save(img, os.path.join(TEX, name + ".png"))
        for rel, obj in J.cross(name, name):
            writej(rel, obj)
        writej(*J.loot_self(name))
        lang[f"block.{E}.{name}"] = " ".join(w.capitalize() for w in name.split("_"))
    json.dump(lang, open(lang_path, "w"), indent=2)
    # ground blocks: mineable
    writej("data/minecraft/tags/block/mineable/shovel.json",
           {"replace": False, "values": [f"{E}:alien_grass_block", f"{E}:void_moss_block"]})
    writej(f"data/{E}/tags/block/lush_replaceable.json",
           {"replace": False, "values": ["minecraft:end_stone"]})


# ---------------- features ----------------
def cf(name, obj):
    writej(f"{WG}/configured_feature/{name}.json", obj)


def simple_block(block):
    return {"type": "minecraft:simple_block",
            "config": {"to_place": {"type": "minecraft:simple_state_provider", "state": {"Name": f"{E}:{block}"}}}}


def weighted(entries):
    return {"type": "minecraft:simple_block",
            "config": {"to_place": {"type": "minecraft:weighted_state_provider",
                       "entries": [{"weight": w, "data": {"Name": f"{E}:{b}"}} for b, w in entries]}}}


def veg_patch(name, ground, veg_cf):
    cf(name, {"type": "minecraft:vegetation_patch", "config": {
        "surface": "floor", "depth": 1, "vertical_range": 5,
        "extra_bottom_block_chance": 0.0, "extra_edge_column_chance": 0.25,
        "vegetation_chance": 0.75,
        "xz_radius": {"type": "minecraft:uniform", "min_inclusive": 3, "max_inclusive": 6},
        "replaceable": f"#{E}:lush_replaceable",
        "ground_state": {"type": "minecraft:simple_state_provider", "state": {"Name": f"{E}:{ground}"}},
        "vegetation_feature": {"feature": f"{E}:{veg_cf}", "placement": []}}})


def tree(name, log, leaves, base_h, rand_a, radius, fol_h):
    cf(name, {"type": "minecraft:tree", "config": {
        "ignore_vines": True, "minimum_size": {"type": "minecraft:two_layers_feature_size"},
        "trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": base_h,
                         "height_rand_a": rand_a, "height_rand_b": 0},
        "trunk_provider": {"type": "minecraft:simple_state_provider", "state": {"Name": f"{E}:{log}", "Properties": {"axis": "y"}}},
        "foliage_placer": {"type": "minecraft:blob_foliage_placer", "height": fol_h, "offset": 0, "radius": radius},
        "foliage_provider": {"type": "minecraft:simple_state_provider", "state": {"Name": f"{E}:{leaves}"}},
        "below_trunk_provider": {"type": "minecraft:simple_state_provider", "state": {"Name": "minecraft:end_stone"}},
        "decorators": []}})


def surface_pf(name, feature, count, air_filter=True):
    pl = [{"type": "minecraft:count", "count": count}, {"type": "minecraft:in_square"},
          {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"}]
    if air_filter:
        pl.append({"type": "minecraft:block_predicate_filter",
                   "predicate": {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"}})
    pl.append({"type": "minecraft:biome"})
    writej(f"{WG}/placed_feature/{name}.json", {"feature": f"{E}:{feature}", "placement": pl})


def build_features():
    cf("lush_veg_garden", weighted([("glowstalk", 3), ("glow_fungus", 3), ("giant_bloom", 2)]))
    cf("lush_veg_jungle", weighted([("void_fern", 3), ("giant_bloom", 2), ("glowstalk", 2), ("glow_fungus", 1)]))
    veg_patch("garden_patch", "void_moss_block", "lush_veg_garden")
    veg_patch("jungle_patch", "alien_grass_block", "lush_veg_jungle")
    tree("chorus_tree_giant", "chorus_log", "chorus_leaves", 9, 5, 3, 4)
    for b in ("glowstalk", "glow_fungus", "giant_bloom", "crystal_flower", "void_fern"):
        cf(f"cf_{b}", simple_block(b))

    surface_pf("garden_patch", "garden_patch", 10, air_filter=False)
    surface_pf("jungle_patch", "jungle_patch", 14, air_filter=False)
    surface_pf("chorus_tree_giant", "chorus_tree_giant", 3, air_filter=False)
    surface_pf("scatter_glowstalk", "cf_glowstalk", 10)
    surface_pf("scatter_glow_fungus", "cf_glow_fungus", 8)
    surface_pf("scatter_giant_bloom", "cf_giant_bloom", 8)
    surface_pf("scatter_crystal_flower", "cf_crystal_flower", 14)
    surface_pf("scatter_void_fern", "cf_void_fern", 6)


# ---------------- biome rewrite (keep effects/spawners/ambient, swap features) ----------------
BIOME_FEATURES = {
    "void_gardens":     (["ore_chorus"], ["garden_patch", "scatter_glowstalk", "scatter_glow_fungus", "chorus_tree", "patch_void_bloom"]),
    "chorus_jungle":    (["ore_chorus"], ["jungle_patch", "chorus_tree_dense", "chorus_tree_giant", "scatter_giant_bloom", "scatter_void_fern"]),
    "crystal_highlands":(["ore_void_crystal", "ore_chorus"], ["scatter_crystal_flower", "patch_crystal_bloom", "scatter_glowstalk"]),
    "obsidian_wastes":  (["ore_obsidian", "ore_void_crystal"], ["scatter_void_fern"]),
    "shattered_barrens":(["ore_void_crystal"], ["scatter_void_fern"]),
    "endless_abyss":    (["ore_void_crystal_rich"], ["scatter_glow_fungus"]),
}


def rewrite_biomes():
    for b, (ores, veg) in BIOME_FEATURES.items():
        p = os.path.join(RES, WG, "biome", b + ".json")
        d = json.load(open(p))
        feats = [[] for _ in range(11)]
        feats[6] = [f"{E}:{o}" for o in ores]
        feats[9] = [f"{E}:{v}" for v in veg]
        d["features"] = feats
        json.dump(d, open(p, "w"), indent=2)
        print(f"  biome {b}: {len(veg)} veg features")


def main():
    build_blocks()
    build_features()
    rewrite_biomes()
    print("biome overhaul assets generated (register 7 blocks in ModBlocks, then build)")


if __name__ == "__main__":
    main()
