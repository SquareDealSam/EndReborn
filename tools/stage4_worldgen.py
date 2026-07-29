#!/usr/bin/env python3
"""Stage 4 - worldgen: 6 End biomes + ore/tree/flora features, and 2 flora blocks.

Emits data/endreborn/worldgen/{biome,configured_feature,placed_feature}/*.json plus
flora textures/models/loot/lang. Biomes are slotted into the End outer islands by
ModWorldgen (TheEndBiomes). Run:  python tools/stage4_worldgen.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import textures as T
import mcjson as J
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
WG = "data/endreborn/worldgen"


def writej(rel, obj):
    p = os.path.join(RES, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)


def rgb(hexc):
    return int(hexc.lstrip("#"), 16)


# ---------- feature helpers ----------
def ore_cf(name, block, size):
    writej(f"{WG}/configured_feature/{name}.json", {
        "type": "minecraft:ore",
        "config": {"size": size, "discard_chance_on_air_exposure": 0.0,
                   "targets": [{"state": {"Name": block},
                                "target": {"predicate_type": "minecraft:block_match",
                                           "block": "minecraft:end_stone"}}]}})


def ore_pf(name, cf, count, ymin=0, ymax=120):
    writej(f"{WG}/placed_feature/{name}.json", {
        "feature": f"endreborn:{cf}",
        "placement": [
            {"type": "minecraft:count", "count": count},
            {"type": "minecraft:in_square"},
            {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform",
             "min_inclusive": {"absolute": ymin}, "max_inclusive": {"absolute": ymax}}},
            {"type": "minecraft:biome"}]})


def surface_pf(name, cf, count):
    writej(f"{WG}/placed_feature/{name}.json", {
        "feature": f"endreborn:{cf}",
        "placement": [
            {"type": "minecraft:count", "count": count},
            {"type": "minecraft:in_square"},
            {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"},
            {"type": "minecraft:biome"}]})


def chorus_tree_cf():
    writej(f"{WG}/configured_feature/chorus_tree.json", {
        "type": "minecraft:tree",
        "config": {
            "ignore_vines": True,
            "minimum_size": {"type": "minecraft:two_layers_feature_size"},
            "trunk_placer": {"type": "minecraft:straight_trunk_placer",
                             "base_height": 5, "height_rand_a": 3, "height_rand_b": 0},
            "trunk_provider": {"type": "minecraft:simple_state_provider",
                               "state": {"Name": "endreborn:chorus_log", "Properties": {"axis": "y"}}},
            "foliage_placer": {"type": "minecraft:blob_foliage_placer", "height": 3, "offset": 0, "radius": 2},
            "foliage_provider": {"type": "minecraft:simple_state_provider", "state": {"Name": "endreborn:chorus_leaves"}},
            "below_trunk_provider": {"type": "minecraft:simple_state_provider", "state": {"Name": "minecraft:end_stone"}},
            "decorators": []}})


def patch_cf(name, block):
    # 26.2 has no random_patch feature; flora is a simple_block scattered by the placed feature.
    writej(f"{WG}/configured_feature/{name}.json", {
        "type": "minecraft:simple_block",
        "config": {"to_place": {"type": "minecraft:simple_state_provider", "state": {"Name": block}}}})


def flora_pf(name, cf, count):
    writej(f"{WG}/placed_feature/{name}.json", {
        "feature": f"endreborn:{cf}",
        "placement": [
            {"type": "minecraft:count", "count": count},
            {"type": "minecraft:in_square"},
            {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"},
            {"type": "minecraft:block_predicate_filter",
             "predicate": {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"}},
            {"type": "minecraft:biome"}]})


# ---------- features ----------
def build_features():
    ore_cf("ore_chorus", "endreborn:chorus_ore", 6)
    ore_cf("ore_void_crystal", "endreborn:void_crystal_ore", 4)
    ore_cf("ore_obsidian", "endreborn:obsidian", 14)
    chorus_tree_cf()
    patch_cf("patch_void_bloom", "endreborn:void_bloom")
    patch_cf("patch_crystal_bloom", "endreborn:crystal_bloom")

    ore_pf("ore_chorus", "ore_chorus", 8)
    ore_pf("ore_void_crystal", "ore_void_crystal", 5, 0, 100)
    ore_pf("ore_void_crystal_rich", "ore_void_crystal", 12, 0, 100)
    ore_pf("ore_obsidian", "ore_obsidian", 8, 0, 90)
    surface_pf("chorus_tree", "chorus_tree", 2)
    surface_pf("chorus_tree_dense", "chorus_tree", 8)
    flora_pf("patch_void_bloom", "patch_void_bloom", 6)
    flora_pf("patch_crystal_bloom", "patch_crystal_bloom", 4)


# ---------- biomes ----------
def spawners(ambient=None, creature=None, monster=None):
    def lst(x):
        return x or []
    return {"ambient": lst(ambient), "axolotls": [], "creature": lst(creature), "misc": [],
            "monster": lst(monster), "underground_water_creature": [], "water_ambient": [],
            "water_creature": []}


def spawn(entity, weight, lo, hi):
    return {"type": f"endreborn:{entity}", "weight": weight, "minCount": lo, "maxCount": hi}


def biome(name, sky, fog, spawn_cfg, ores, veg, particle=None):
    features = [[] for _ in range(11)]
    features[6] = [f"endreborn:{o}" for o in ores]          # UNDERGROUND_ORES
    features[9] = [f"endreborn:{v}" for v in veg]           # VEGETAL_DECORATION
    effects = {"sky_color": rgb(sky), "fog_color": rgb(fog),
               "water_color": rgb("#3f76e4"), "water_fog_color": rgb("#050533")}
    if particle:
        effects["particle"] = {"probability": 0.006, "options": {"type": particle}}
    writej(f"{WG}/biome/{name}.json", {
        "has_precipitation": False, "temperature": 0.5, "downfall": 0.5,
        "carvers": [], "spawn_costs": {}, "features": features,
        "effects": effects, "spawners": spawn_cfg})


def build_biomes():
    biome("shattered_barrens", "#0a0a14", "#14101f",
          spawners(monster=[spawn("void_wraith", 12, 1, 2)]),
          ["ore_void_crystal"], [])
    biome("void_gardens", "#1a0f2e", "#2a1a40",
          spawners(ambient=[spawn("void_moth", 15, 2, 4), spawn("chorus_sprite", 10, 1, 3)]),
          ["ore_chorus"], ["patch_void_bloom", "chorus_tree"], particle="minecraft:end_rod")
    biome("obsidian_wastes", "#08060e", "#100a18",
          spawners(monster=[spawn("obsidian_golem", 14, 1, 2), spawn("abyss_stalker", 6, 1, 2)]),
          ["ore_obsidian", "ore_void_crystal"], [])
    biome("crystal_highlands", "#12203a", "#1a2f52",
          spawners(creature=[spawn("crystal_strider", 12, 1, 3)],
                   monster=[spawn("crystal_sentinel", 10, 1, 2)]),
          ["ore_void_crystal", "ore_chorus"], ["patch_crystal_bloom"])
    biome("endless_abyss", "#050308", "#0a0612",
          spawners(monster=[spawn("abyss_stalker", 12, 1, 3), spawn("void_wraith", 8, 1, 2)]),
          ["ore_void_crystal_rich"], [], particle="minecraft:reverse_portal")
    biome("chorus_jungle", "#200f30", "#301a48",
          spawners(ambient=[spawn("chorus_sprite", 15, 2, 4), spawn("void_moth", 8, 1, 2)]),
          ["ore_chorus"], ["chorus_tree_dense"])


# ---------- flora blocks ----------
def build_flora():
    lang_path = os.path.join(RES, "assets", "endreborn", "lang", "en_us.json")
    lang = json.load(open(lang_path))
    flora = {"void_bloom": ("#b060ff", True), "crystal_bloom": ("#7fe0ff", False)}
    imgs = {}
    for name, (color, glow) in flora.items():
        img = T.plant_tex(color, name, glow=glow)
        imgs[name] = img
        T.save(img, os.path.join(RES, "assets", "endreborn", "textures", "block", name + ".png"))
        for rel, obj in J.cross(name, name):
            writej(rel, obj)
        writej(*J.loot_self(name))
        lang[f"block.endreborn.{name}"] = " ".join(w.capitalize() for w in name.split("_"))
    for name in ("shattered_barrens", "void_gardens", "obsidian_wastes",
                 "crystal_highlands", "endless_abyss", "chorus_jungle"):
        lang[f"biome.endreborn.{name}"] = " ".join(w.capitalize() for w in name.split("_"))
    json.dump(lang, open(lang_path, "w"), indent=2)
    return imgs


def main():
    build_features()
    build_biomes()
    imgs = build_flora()
    print("emitted 6 biomes + features + 2 flora blocks")
    try:
        bb = BB()
        for name, img in imgs.items():
            bb.call("create_project", {"name": name, "format": "java_block"})
            bb.call("create_texture", {"name": name, "data": T.to_data_url(img)})
        print("flora textures mirrored into Blockbench tabs")
    except Exception as e:
        print("Blockbench mirror skipped:", e)


if __name__ == "__main__":
    main()
