#!/usr/bin/env python3
"""Builds a massive End-themed palace and exports it as a Litematica .litematic.

Uses EndReborn blocks + vanilla End blocks. Composition: foundation + dungeon,
grand entrance stair & portico, a tall great-hall arena with colonnades / arched
windows / chandeliers / a throne dais, two two-storey room wings with balconies,
a garden atrium, four battlemented corner towers with glow beacons, and roofs.

Run:  python tools/palace.py   ->  schematics/void_palace.litematic
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import nbt

# ---- palette (EndReborn + vanilla End) ----
FOUND = "endreborn:polished_void_stone"
WALL = "endreborn:obsidian_bricks"
ACCENT = "minecraft:end_stone_bricks"
FLOOR = "endreborn:void_stone_bricks"
CRYS = "endreborn:crystal_stone_bricks"
GLOWB = "endreborn:void_crystal_block"
LAMP = "minecraft:sea_lantern"
SHROOM = "minecraft:shroomlight"
TRIM = "endreborn:chorus_planks"
ROOF = "endreborn:obsidian"
ROOF2 = "minecraft:purpur_block"
GLASS = "minecraft:purple_stained_glass"
CARPET = "minecraft:purple_carpet"
BARS = "minecraft:iron_bars"
PILLAR = "minecraft:purpur_pillar"
OBSW = "endreborn:obsidian_bricks_wall"
CFENCE = "endreborn:chorus_fence"
GRASS = "endreborn:alien_grass_block"
MOSS = "endreborn:void_moss_block"
CLOG = "endreborn:chorus_log"
CLEAF = "endreborn:chorus_leaves"
GLOWSTALK = "endreborn:glowstalk"
GFUNGUS = "endreborn:glow_fungus"
BLOOM = "endreborn:giant_bloom"
OBS_STAIR = "endreborn:obsidian_bricks_stairs"
VOID_STAIR = "endreborn:polished_void_stone_stairs"
CRYS_STAIR = "endreborn:crystal_stone_bricks_stairs"
OBS_SLAB = "endreborn:obsidian_bricks_slab"
AIR = "minecraft:air"


class Pal:
    def __init__(self):
        self.g = {}  # (x,y,z)->(name, props tuple or None)

    def set(self, x, y, z, name, props=None):
        self.g[(int(x), int(y), int(z))] = (name, props)

    def fill(self, x0, x1, y0, y1, z0, z1, name, props=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, name, props)

    def walls(self, x0, x1, y0, y1, z0, z1, name, props=None):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if x in (x0, x1) or z in (z0, z1):
                        self.set(x, y, z, name, props)

    def floor(self, x0, x1, y, z0, z1, name, props=None):
        self.fill(x0, x1, y, y, z0, z1, name, props)

    def pillar(self, x, z, y0, y1, name, props=None):
        self.fill(x, x, y0, y1, z, z, name, props)

    def clear(self, x0, x1, y0, y1, z0, z1):
        self.fill(x0, x1, y0, y1, z0, z1, AIR)

    def stair(self, x, y, z, name, facing, half="bottom"):
        self.set(x, y, z, name, {"facing": facing, "half": half, "shape": "straight"})

    # ---------- Litematica export ----------
    def export(self, path, name, author, desc):
        xs = [p[0] for p in self.g]; ys = [p[1] for p in self.g]; zs = [p[2] for p in self.g]
        minx, miny, minz = min(xs), min(ys), min(zs)
        W, H, D = max(xs) - minx + 1, max(ys) - miny + 1, max(zs) - minz + 1
        vol = W * H * D

        # palette: air first
        palette = [(AIR, None)]
        pidx = {(AIR, None): 0}
        indices = [0] * vol
        for (x, y, z), (nm, props) in self.g.items():
            pk = tuple(sorted(props.items())) if props else None
            key = (nm, pk)
            if key not in pidx:
                pidx[key] = len(palette); palette.append(key)
            lx, ly, lz = x - minx, y - miny, z - minz
            indices[(ly * D + lz) * W + lx] = pidx[key]

        bits = max(2, (len(palette) - 1).bit_length())
        arr_len = (vol * bits + 63) // 64
        longs = [0] * arr_len
        M = (1 << bits) - 1
        MASK64 = (1 << 64) - 1
        for i, v in enumerate(indices):
            off = i * bits; ai = off >> 6; bo = off & 63; val = v & M
            longs[ai] = (longs[ai] | (val << bo)) & MASK64
            end = ((i + 1) * bits - 1) >> 6
            if end != ai:
                longs[end] |= (val >> (64 - bo))

        # self-check: unpack the long array and confirm it round-trips to `indices`
        for i in range(vol):
            off = i * bits; ai = off >> 6; bo = off & 63
            val = (longs[ai] >> bo) & M
            if bo + bits > 64:
                val = (val | (longs[ai + 1] << (64 - bo))) & M
            if val != indices[i]:
                raise AssertionError(f"pack mismatch at {i}: {val} != {indices[i]}")

        def pal_node(nm, props):
            e = {"Name": ("string", nm)}
            if props:
                e["Properties"] = ("compound", {k: ("string", str(v)) for k, v in props})
            return ("compound", e)

        def c3(x, y, z):
            return ("compound", {"x": ("int", x), "y": ("int", y), "z": ("int", z)})

        region = ("compound", {
            "Position": c3(0, 0, 0),
            "Size": c3(W, H, D),
            "BlockStatePalette": ("list", "compound", [pal_node(n, p) for n, p in palette]),
            "BlockStates": ("long_array", longs),
            "Entities": ("list", "compound", []),
            "TileEntities": ("list", "compound", []),
            "PendingBlockTicks": ("list", "compound", []),
            "PendingFluidTicks": ("list", "compound", []),
        })
        now = int(time.time() * 1000)
        root = ("compound", {
            "MinecraftDataVersion": ("int", nbt.DATA_VERSION),
            "Version": ("int", 6),
            "SubVersion": ("int", 1),
            "Metadata": ("compound", {
                "Name": ("string", name), "Author": ("string", author),
                "Description": ("string", desc),
                "TimeCreated": ("long", now), "TimeModified": ("long", now),
                "EnclosingSize": c3(W, H, D),
                "TotalVolume": ("int", vol),
                "TotalBlocks": ("int", len(self.g)),
                "RegionCount": ("int", 1),
            }),
            "Regions": ("compound", {name: region}),
        })
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nbt.write_nbt(path, root)
        return W, H, D, len(self.g), len(palette)


def build():
    p = Pal()
    W, D = 48, 60                       # footprint (x, z)
    GY = 5                              # great-hall floor level
    x0, x1, z0, z1 = 0, W - 1, 0, D - 1

    # ---- foundation + dungeon ----
    p.fill(x0, x1, 0, GY - 1, z0, z1, FOUND)                       # solid base
    # dungeon corridor + 4 cells carved inside the base
    p.clear(20, 27, 1, 3, 14, 45)
    p.floor(20, 27, 0, 14, 45, FLOOR)
    for cz in (18, 30, 42):
        for cx in (16, 31):
            p.clear(cx - 3, cx + 3, 1, 3, cz - 3, cz + 3)
            p.walls(cx - 3, cx + 3, 1, 3, cz - 3, cz + 3, WALL)
        p.fill(19, 19, 1, 3, cz - 1, cz + 1, BARS)                 # cell bars
        p.fill(28, 28, 1, 3, cz - 1, cz + 1, BARS)
    for lz in range(16, 45, 6):
        p.set(23, 3, lz, LAMP); p.set(24, 3, lz, LAMP)

    # ---- main floor ----
    p.floor(2, W - 3, GY, 2, D - 3, FLOOR)
    # stairs from great hall down to dungeon (back-center)
    p.clear(23, 24, GY, GY, 44, 47)
    for i, zz in enumerate(range(44, 48)):
        p.fill(23, 24, GY - 1 - i, GY - 1 - i, zz, zz, FOUND)

    # ---- outer shell ----
    HALL_TOP = GY + 20
    p.walls(x0 + 2, x1 - 2, GY, HALL_TOP, z0 + 2, z1 - 2, WALL)
    # accent banding
    for by in (GY + 5, GY + 12, HALL_TOP - 1):
        for xx in range(x0 + 2, x1 - 1):
            p.set(xx, by, z0 + 2, ACCENT); p.set(xx, by, z1 - 2, ACCENT)
        for zz in range(z0 + 2, z1 - 1):
            p.set(x0 + 2, by, zz, ACCENT); p.set(x1 - 2, by, zz, ACCENT)

    # ---- great hall interior ----
    hx0, hx1, hz0, hz1 = 8, 39, 6, 52
    p.clear(hx0, hx1, GY + 1, HALL_TOP - 1, hz0, hz1)
    p.floor(hx0, hx1, GY, hz0, hz1, FLOOR)
    # carpet runner to throne
    p.fill(22, 25, GY + 1, GY + 1, 8, 46, CARPET)
    # colonnades
    for cz in range(10, 49, 6):
        for cx in (11, 36):
            p.pillar(cx, cz, GY + 1, HALL_TOP - 3, PILLAR, {"axis": "y"})
            p.set(cx, HALL_TOP - 2, cz, ACCENT)
            p.set(cx, GY + 1, cz, CRYS)
            p.set(cx, GY + 3, cz, GLOWSTALK)          # sconce
        # arch beam between columns
        p.fill(11, 36, HALL_TOP - 3, HALL_TOP - 3, cz, cz, ACCENT)
    # arched windows in side walls
    for wz in range(10, 49, 6):
        for wx in (x0 + 2, x1 - 2):
            p.fill(wx, wx, GY + 4, GY + 9, wz - 1, wz + 1, GLASS)
            p.set(wx, GY + 10, wz, GLASS)
    # chandeliers
    for cz in (18, 30, 42):
        p.fill(23, 24, HALL_TOP - 1, HALL_TOP - 1, cz, cz + 1, CFENCE)
        p.fill(22, 25, HALL_TOP - 4, HALL_TOP - 4, cz - 1, cz + 2, CFENCE)
        p.set(23, HALL_TOP - 5, cz, LAMP); p.set(24, HALL_TOP - 5, cz + 1, LAMP)
        p.set(22, HALL_TOP - 5, cz, GLOWSTALK); p.set(25, HALL_TOP - 5, cz + 1, GLOWSTALK)

    # ---- throne dais ----
    for i in range(3):
        p.fill(18 - 0, 29, GY + i, GY + i, 46 + i, 46 + i, CRYS)
        p.stair(18 + 0, GY + i, 45 + i, CRYS_STAIR, "north")
    p.fill(18, 29, GY + 3, GY + 3, 47, 51, FOUND)                 # dais top
    p.fill(20, 27, GY + 4, GY + 10, 51, 51, GLOWB)               # glowing backdrop
    p.fill(19, 19, GY + 3, GY + 9, 47, 51, PILLAR, {"axis": "y"})
    p.fill(28, 28, GY + 3, GY + 9, 47, 51, PILLAR, {"axis": "y"})
    p.set(23, GY + 4, 50, PILLAR, {"axis": "y"}); p.set(24, GY + 4, 50, PILLAR, {"axis": "y"})
    p.set(23, GY + 5, 50, GLOWB); p.set(24, GY + 5, 50, GLOWB)   # boss pedestal
    for xx in (20, 27):
        p.set(xx, GY + 4, 49, GLOWSTALK)

    # ---- entrance: grand stair + portico + doorway ----
    for i in range(6):
        p.fill(18 - i, 29 + i, GY - 1 - i, GY - 1 - i, 1 - 0, 1, FOUND)
        p.stair(18 - i, GY - 1 - i, 2, VOID_STAIR, "south")
        p.stair(29 + i, GY - 1 - i, 2, VOID_STAIR, "south")
    p.clear(21, 26, GY + 1, GY + 6, 2, 5)                         # doorway
    for px in (19, 28):
        p.pillar(px, 4, GY, GY + 8, PILLAR, {"axis": "y"})
        p.set(px, GY + 9, 4, ACCENT)
        p.set(px, GY + 1, 4, GLOWSTALK)
    p.fill(19, 28, GY + 9, GY + 9, 3, 5, ACCENT)                  # portico lintel

    # ---- two room wings (2 storeys) ----
    def room(rx0, rx1, ry0, rz0, rz1, floors=2):
        for fl in range(floors):
            fy = ry0 + fl * 6
            p.clear(rx0 + 1, rx1 - 1, fy + 1, fy + 5, rz0 + 1, rz1 - 1)
            p.floor(rx0, rx1, fy, rz0, rz1, FLOOR)
            # windows
            for wz in range(rz0 + 2, rz1 - 1, 4):
                p.set(rx0, fy + 3, wz, GLASS); p.set(rx1, fy + 3, wz, GLASS)
            p.set(rx0 + 2, fy + 4, rz0 + 2, LAMP)                 # light
    # left wing rooms
    for rz0, rz1 in ((8, 22), (24, 38), (40, 51)):
        room(2, 7, GY, rz0, rz1)
        p.clear(7, 8, GY + 1, GY + 3, (rz0 + rz1) // 2 - 1, (rz0 + rz1) // 2 + 1)  # door to hall
    # right wing rooms
    for rz0, rz1 in ((8, 22), (24, 38), (40, 51)):
        room(40, 45, GY, rz0, rz1)
        p.clear(39, 40, GY + 1, GY + 3, (rz0 + rz1) // 2 - 1, (rz0 + rz1) // 2 + 1)
    # wing dividing floor already handled; balconies overlooking hall
    for zz in range(10, 49, 3):
        p.stair(8, GY + 7, zz, OBS_STAIR, "east", "top")
        p.stair(39, GY + 7, zz, OBS_STAIR, "west", "top")

    # ---- garden atrium (back-left upper room) ----
    gx0, gx1, gz0, gz1 = 2, 7, 40, 51
    p.floor(gx0, gx1, GY + 6, gz0, gz1, GRASS)
    for gz in range(gz0 + 1, gz1, 3):
        for gx in (gx0 + 1, gx1 - 1):
            if (gx + gz) % 2:
                p.pillar(gx, gz, GY + 7, GY + 9, CLOG, {"axis": "y"})
                p.fill(gx - 1, gx + 1, GY + 10, GY + 10, gz - 1, gz + 1, CLEAF)
                p.set(gx, GY + 11, gz, CLEAF)
            else:
                p.set(gx, GY + 7, gz, GLOWSTALK)
        p.set((gx0 + gx1) // 2, GY + 7, gz, BLOOM)
    p.floor(gx0 + 1, gx1 - 1, GY + 6, gz0 + 1, gz1 - 1, MOSS)

    # ---- corner towers ----
    def tower(tx, tz):
        t0x, t1x, t0z, t1z = tx, tx + 6, tz, tz + 6
        top = HALL_TOP + 8
        p.walls(t0x, t1x, GY, top, t0z, t1z, WALL)
        for fy in range(GY, top, 6):
            p.floor(t0x + 1, t1x - 1, fy, t0z + 1, t1z - 1, FLOOR)
            p.clear(t0x + 1, t1x - 1, fy + 1, fy + 5, t0z + 1, t1z - 1)
            for wx, wz in ((t0x, (t0z + t1z) // 2), (t1x, (t0z + t1z) // 2)):
                p.set(wx, fy + 3, wz, GLASS)
        # beacon
        p.pillar((t0x + t1x) // 2, (t0z + t1z) // 2, GY + 1, top - 1, LAMP)
        # battlements
        for xx in range(t0x, t1x + 1, 2):
            p.set(xx, top + 1, t0z, OBSW); p.set(xx, top + 1, t1z, OBSW)
        for zz in range(t0z, t1z + 1, 2):
            p.set(t0x, top + 1, zz, OBSW); p.set(t1x, top + 1, zz, OBSW)
        # crystal spire roof
        for i in range(4):
            p.fill(t0x + i, t1x - i, top + 1 + i, top + 1 + i, t0z + i, t1z - i, CRYS)
        p.set((t0x + t1x) // 2, top + 6, (t0z + t1z) // 2, GLOWB)
    tower(0, 0); tower(0, D - 7); tower(W - 7, 0); tower(W - 7, D - 7)

    # ---- great-hall roof (stepped gable) + wing roofs ----
    for i in range(9):
        p.stair(hx0 - 1 + i, HALL_TOP + i, hz0 - 1, ROOF and OBS_STAIR, "east") if False else None
    # simple stepped gable over the hall
    for i in range(8):
        xa, xb = 8 + i, 39 - i
        p.fill(xa, xb, HALL_TOP + i, HALL_TOP + i, hz0 - 1, hz1 + 1, ROOF if i % 2 else ROOF2)
        if xa >= xb:
            break
    # wing flat battlemented roofs
    for side in ((2, 7), (40, 45)):
        p.floor(side[0], side[1], GY + 12, 8, 51, ACCENT)
        for zz in range(8, 52, 2):
            p.set(side[0], GY + 13, zz, OBSW); p.set(side[1], GY + 13, zz, OBSW)

    return p


def main():
    p = build()
    out = os.path.join(os.path.dirname(__file__), "..", "schematics", "void_palace.litematic")
    W, H, D, blocks, pal = p.export(os.path.abspath(out), "Void Palace",
                                    "SquareDealSam", "A massive End palace for EndReborn.")
    print(f"wrote {out}\n  size {W}x{H}x{D} | {blocks} blocks | {pal} palette entries")


if __name__ == "__main__":
    main()
