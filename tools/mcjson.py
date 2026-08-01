#!/usr/bin/env python3
"""Minecraft blockstate/model JSON templates (Java edition, 1.21.x shape).

Each function returns (list of (relpath_under_assets_or_data, dict)) describing
the files to write for a block/item, mirroring what vanilla datagen emits. `NS`
is the mod namespace. Textures are referenced as voidweaver:block/<tex>.
"""
import json
import os
import zipfile

NS = "voidweaver"
CLIENT_JAR = os.path.expanduser(
    "~/.gradle/caches/fabric-loom/26.2/minecraft-client.jar")

_vanilla_cache = {}


def _vanilla_blockstate(vanilla_name):
    """Read a vanilla blockstate JSON (as text) from the client jar, cached."""
    if vanilla_name not in _vanilla_cache:
        with zipfile.ZipFile(CLIENT_JAR) as z:
            _vanilla_cache[vanilla_name] = z.read(
                f"assets/minecraft/blockstates/{vanilla_name}.json").decode()
    return _vanilla_cache[vanilla_name]


def _remap_blockstate(vanilla_name, replacements):
    """Load a vanilla blockstate and string-swap model id prefixes -> ours."""
    text = _vanilla_blockstate(vanilla_name)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return json.loads(text)


def tex(t):
    return f"{NS}:block/{t}"


# ---- simple full-cube block ----
def cube_all(name, texture):
    m = f"{NS}:block/{name}"
    return [
        (f"assets/{NS}/blockstates/{name}.json", {"variants": {"": {"model": m}}}),
        (f"assets/{NS}/models/block/{name}.json",
         {"parent": "minecraft:block/cube_all", "textures": {"all": tex(texture)}}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": m}),
    ]


def cube_column(name, side, top):
    """Pillar (log) with axis variants."""
    m = f"{NS}:block/{name}"
    return [
        (f"assets/{NS}/blockstates/{name}.json", {"variants": {
            "axis=y": {"model": m},
            "axis=z": {"model": m, "x": 90},
            "axis=x": {"model": m, "x": 90, "y": 90},
        }}),
        (f"assets/{NS}/models/block/{name}.json",
         {"parent": "minecraft:block/cube_column",
          "textures": {"side": tex(side), "end": tex(top)}}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": m}),
    ]


# ---- stairs (blockstate remapped from vanilla oak_stairs for exact rotations) ----
def stairs(name, texture):
    b = f"{NS}:block/{name}"
    t = tex(texture)
    tt = {"bottom": t, "top": t, "side": t}
    bs = _remap_blockstate("oak_stairs", {"minecraft:block/oak_stairs": b})
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}.json", {"parent": "minecraft:block/stairs", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_inner.json", {"parent": "minecraft:block/inner_stairs", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_outer.json", {"parent": "minecraft:block/outer_stairs", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": b}),
    ]


# ---- slab ----
def slab(name, texture, double_block):
    b = f"{NS}:block/{name}"
    t = tex(texture)
    tt = {"bottom": t, "top": t, "side": t}
    bs = _remap_blockstate("oak_slab", {
        "minecraft:block/oak_slab": b,
        "minecraft:block/oak_planks": f"{NS}:block/{double_block}",
    })
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}.json", {"parent": "minecraft:block/slab", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_top.json", {"parent": "minecraft:block/slab_top", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": b}),
    ]


# ---- wall (blockstate remapped from vanilla cobblestone_wall) ----
def wall(name, texture):
    b = f"{NS}:block/{name}"
    t = tex(texture)
    tt = {"wall": t}
    bs = _remap_blockstate("cobblestone_wall", {"minecraft:block/cobblestone_wall": b})
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}_post.json", {"parent": "minecraft:block/template_wall_post", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_side.json", {"parent": "minecraft:block/template_wall_side", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_side_tall.json", {"parent": "minecraft:block/template_wall_side_tall", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_inventory.json", {"parent": "minecraft:block/wall_inventory", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": b + "_inventory"}),
    ]


# ---- leaves (cutout render) ----
def leaves(name, texture):
    m = f"{NS}:block/{name}"
    return [
        (f"assets/{NS}/blockstates/{name}.json", {"variants": {"": {"model": m}}}),
        (f"assets/{NS}/models/block/{name}.json",
         {"parent": "minecraft:block/cube_all", "render_type": "minecraft:cutout_mipped",
          "textures": {"all": tex(texture)}}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": m}),
    ]


# ---- door (top/bottom textures) ----
def door(name):
    tt = {"bottom": f"{NS}:block/{name}_bottom", "top": f"{NS}:block/{name}_top"}
    bs = _remap_blockstate("oak_door", {"minecraft:block/oak_door": f"{NS}:block/{name}"})
    files = [(f"assets/{NS}/blockstates/{name}.json", bs)]
    for suffix in ("bottom_left", "bottom_left_open", "bottom_right", "bottom_right_open",
                   "top_left", "top_left_open", "top_right", "top_right_open"):
        files.append((f"assets/{NS}/models/block/{name}_{suffix}.json",
                      {"parent": f"minecraft:block/door_{suffix}", "textures": tt}))
    files.append((f"assets/{NS}/models/item/{name}.json",
                  {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{name}"}}))
    return files


def trapdoor(name, texture):
    tt = {"texture": tex(texture)}
    bs = _remap_blockstate("oak_trapdoor", {"minecraft:block/oak_trapdoor": f"{NS}:block/{name}"})
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}_bottom.json", {"parent": "minecraft:block/template_trapdoor_bottom", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_top.json", {"parent": "minecraft:block/template_trapdoor_top", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_open.json", {"parent": "minecraft:block/template_trapdoor_open", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": f"{NS}:block/{name}_bottom"}),
    ]


def fence(name, texture):
    tt = {"texture": tex(texture)}
    bs = _remap_blockstate("oak_fence", {"minecraft:block/oak_fence": f"{NS}:block/{name}"})
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}_post.json", {"parent": "minecraft:block/fence_post", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_side.json", {"parent": "minecraft:block/fence_side", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_inventory.json", {"parent": "minecraft:block/fence_inventory", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": f"{NS}:block/{name}_inventory"}),
    ]


def fence_gate(name, texture):
    tt = {"texture": tex(texture)}
    bs = _remap_blockstate("oak_fence_gate", {"minecraft:block/oak_fence_gate": f"{NS}:block/{name}"})
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}.json", {"parent": "minecraft:block/template_fence_gate", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_open.json", {"parent": "minecraft:block/template_fence_gate_open", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_wall.json", {"parent": "minecraft:block/template_fence_gate_wall", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_wall_open.json", {"parent": "minecraft:block/template_fence_gate_wall_open", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": f"{NS}:block/{name}"}),
    ]


def pressure_plate(name, texture):
    tt = {"texture": tex(texture)}
    bs = _remap_blockstate("oak_pressure_plate", {"minecraft:block/oak_pressure_plate": f"{NS}:block/{name}"})
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}.json", {"parent": "minecraft:block/pressure_plate_up", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_down.json", {"parent": "minecraft:block/pressure_plate_down", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": f"{NS}:block/{name}"}),
    ]


def button(name, texture):
    tt = {"texture": tex(texture)}
    bs = _remap_blockstate("oak_button", {"minecraft:block/oak_button": f"{NS}:block/{name}"})
    return [
        (f"assets/{NS}/blockstates/{name}.json", bs),
        (f"assets/{NS}/models/block/{name}.json", {"parent": "minecraft:block/button", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_pressed.json", {"parent": "minecraft:block/button_pressed", "textures": tt}),
        (f"assets/{NS}/models/block/{name}_inventory.json", {"parent": "minecraft:block/button_inventory", "textures": tt}),
        (f"assets/{NS}/models/item/{name}.json", {"parent": f"{NS}:block/{name}_inventory"}),
    ]


# ---- cross-shaped plant ----
def cross(name, texture):
    m = f"{NS}:block/{name}"
    return [
        (f"assets/{NS}/blockstates/{name}.json", {"variants": {"": {"model": m}}}),
        (f"assets/{NS}/models/block/{name}.json",
         {"parent": "minecraft:block/cross", "render_type": "minecraft:cutout",
          "textures": {"cross": tex(texture)}}),
        (f"assets/{NS}/models/item/{name}.json",
         {"parent": "minecraft:item/generated", "textures": {"layer0": tex(texture)}}),
    ]


# ---- items ----
def item_generated(name):
    return [(f"assets/{NS}/models/item/{name}.json",
             {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{name}"}})]


def item_handheld(name):
    return [(f"assets/{NS}/models/item/{name}.json",
             {"parent": "minecraft:item/handheld", "textures": {"layer0": f"{NS}:item/{name}"}})]


# ---- loot: block drops itself ----
def loot_self(name):
    return (f"data/{NS}/loot_table/blocks/{name}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:{name}"}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


def loot_slab(name):
    return (f"data/{NS}/loot_table/blocks/{name}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1, "conditions": [{"condition": "minecraft:survives_explosion"}],
                   "entries": [{"type": "minecraft:item", "name": f"{NS}:{name}",
                                "functions": [{"function": "minecraft:set_count", "count": 2,
                                               "conditions": [{"condition": "minecraft:block_state_property",
                                                               "block": f"{NS}:{name}",
                                                               "properties": {"type": "double"}}]},
                                              {"function": "minecraft:explosion_decay"}]}]}]})
