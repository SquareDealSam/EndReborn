#!/usr/bin/env python3
"""Builds a massive End-themed CASTLE palace and exports a Litematica .litematic.

Grand version: full battlemented roof deck over the whole footprint + a big peaked
great-hall roof, four TALL corner spires + a central spire, and fully furnished
interiors (banquet tables, chairs, bookshelves, braziers, hanging lanterns, rugs,
chests, a garden atrium, and a dungeon). EndReborn + vanilla End blocks.

Run:  python tools/palace.py   ->  schematics/void_palace.litematic
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import nbt

# ---- palette ----
FOUND = "voidweaver:polished_void_stone"
WALL = "voidweaver:obsidian_bricks"
ACCENT = "minecraft:end_stone_bricks"
FLOOR = "voidweaver:void_stone_bricks"
CRYS = "voidweaver:crystal_stone_bricks"
GLOWB = "voidweaver:void_crystal_block"
LAMP = "minecraft:sea_lantern"
SHROOM = "minecraft:shroomlight"
TRIM = "voidweaver:chorus_planks"
ROOF = "voidweaver:obsidian"
ROOF2 = "minecraft:purpur_block"
GLASS = "minecraft:purple_stained_glass"
CARPET = "minecraft:purple_carpet"
CARPET2 = "minecraft:magenta_carpet"
BARS = "minecraft:iron_bars"
PILLAR = "minecraft:purpur_pillar"
OBSW = "voidweaver:obsidian_bricks_wall"
CFENCE = "voidweaver:chorus_fence"
CSLAB = "voidweaver:chorus_slab"
CSTAIR = "voidweaver:chorus_stairs"
GRASS = "voidweaver:alien_grass_block"
MOSS = "voidweaver:void_moss_block"
CLOG = "voidweaver:chorus_log"
CLEAF = "voidweaver:chorus_leaves"
GLOWSTALK = "voidweaver:glowstalk"
GFUNGUS = "voidweaver:glow_fungus"
BLOOM = "voidweaver:giant_bloom"
OBS_STAIR = "voidweaver:obsidian_bricks_stairs"
VOID_STAIR = "voidweaver:polished_void_stone_stairs"
CRYS_STAIR = "voidweaver:crystal_stone_bricks_stairs"
OBS_SLAB = "voidweaver:obsidian_bricks_slab"
BOOK = "minecraft:bookshelf"
LECTERN = "minecraft:lectern"
BARREL = "minecraft:barrel"
CHEST = "minecraft:chest"
BRAZIER = "minecraft:campfire"      # lit = brazier (light + embers)
LANTERN = "minecraft:lantern"
CHAIN = "minecraft:chain"
AIR = "minecraft:air"
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


class Pal:
    def __init__(self):
        self.g = {}

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

    def slab(self, x, y, z, name, ty="bottom"):
        self.set(x, y, z, name, {"type": ty})

    # crenellations (merlons every other block) around a rectangle perimeter
    def crenellate(self, x0, x1, z0, z1, y, block):
        for x in range(x0, x1 + 1):
            if x % 2 == 0:
                self.set(x, y, z0, block); self.set(x, y, z1, block)
        for z in range(z0, z1 + 1):
            if z % 2 == 0:
                self.set(x0, y, z, block); self.set(x1, y, z, block)

    def hang_lantern(self, x, y, z, drop=2):
        for i in range(drop):
            self.set(x, y - i, z, CHAIN, {"axis": "y"})
        self.set(x, y - drop, z, LANTERN, {"hanging": "true"})

    def brazier(self, x, y, z):
        self.set(x, y, z, PILLAR, {"axis": "y"})
        self.set(x, y + 1, z, BRAZIER, {"lit": "true", "facing": "north"})

    # tall square spire: straight shaft, then a tapering cap to a glowing point
    def spire(self, cx, cz, base_y, shaft_h, r, shaft, cap):
        top = base_y + shaft_h
        self.walls(cx - r, cx + r, base_y, top, cz - r, cz + r, shaft)
        for i in range(base_y, top, 3):
            self.set(cx - r, i + 1, cz, GLASS); self.set(cx + r, i + 1, cz, GLASS)
        self.pillar(cx, cz, base_y + 1, top, LAMP)          # interior beacon
        cur, y = r, top + 1
        while cur >= 0:
            self.walls(cx - cur, cx + cur, y, y, cz - cur, cz + cur, cap)
            if cur == 0:
                break
            y += 1
            if (y - top) % 2 == 0:
                cur -= 1
        self.set(cx, y + 1, cz, GLOWB)
        self.set(cx, y + 2, cz, GLOWSTALK)

    def export(self, path, name, author, desc):
        xs = [p[0] for p in self.g]; ys = [p[1] for p in self.g]; zs = [p[2] for p in self.g]
        minx, miny, minz = min(xs), min(ys), min(zs)
        W, H, D = max(xs) - minx + 1, max(ys) - miny + 1, max(zs) - minz + 1
        vol = W * H * D
        palette = [(AIR, None)]; pidx = {(AIR, None): 0}; indices = [0] * vol
        for (x, y, z), (nm, props) in self.g.items():
            pk = tuple(sorted(props.items())) if props else None
            key = (nm, pk)
            if key not in pidx:
                pidx[key] = len(palette); palette.append(key)
            lx, ly, lz = x - minx, y - miny, z - minz
            indices[(ly * D + lz) * W + lx] = pidx[key]
        bits = max(2, (len(palette) - 1).bit_length())
        longs = [0] * ((vol * bits + 63) // 64)
        M = (1 << bits) - 1; MASK64 = (1 << 64) - 1
        for i, v in enumerate(indices):
            off = i * bits; ai = off >> 6; bo = off & 63; val = v & M
            longs[ai] = (longs[ai] | (val << bo)) & MASK64
            end = ((i + 1) * bits - 1) >> 6
            if end != ai:
                longs[end] |= (val >> (64 - bo))
        for i, v in enumerate(indices):          # round-trip self-check
            off = i * bits; ai = off >> 6; bo = off & 63
            val = (longs[ai] >> bo) & M
            if bo + bits > 64:
                val = (val | (longs[ai + 1] << (64 - bo))) & M
            assert val == v, f"pack mismatch at {i}"

        def pal_node(nm, props):
            e = {"Name": ("string", nm)}
            if props:
                e["Properties"] = ("compound", {k: ("string", str(v)) for k, v in props})
            return ("compound", e)

        def c3(x, y, z):
            return ("compound", {"x": ("int", x), "y": ("int", y), "z": ("int", z)})

        region = ("compound", {
            "Position": c3(0, 0, 0), "Size": c3(W, H, D),
            "BlockStatePalette": ("list", "compound", [pal_node(n, p) for n, p in palette]),
            "BlockStates": ("long_array", longs),
            "Entities": ("list", "compound", []), "TileEntities": ("list", "compound", []),
            "PendingBlockTicks": ("list", "compound", []), "PendingFluidTicks": ("list", "compound", []),
        })
        now = int(time.time() * 1000)
        root = ("compound", {
            "MinecraftDataVersion": ("int", nbt.DATA_VERSION), "Version": ("int", 6), "SubVersion": ("int", 1),
            "Metadata": ("compound", {
                "Name": ("string", name), "Author": ("string", author), "Description": ("string", desc),
                "TimeCreated": ("long", now), "TimeModified": ("long", now),
                "EnclosingSize": c3(W, H, D), "TotalVolume": ("int", vol),
                "TotalBlocks": ("int", len(self.g)), "RegionCount": ("int", 1)}),
            "Regions": ("compound", {name: region}),
        })
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nbt.write_nbt(path, root)
        return W, H, D, len(self.g), len(palette)


def build():
    p = Pal()
    W, D = 56, 72
    GY = 5
    WT = 30                       # wall top / roof-deck level
    hx0, hx1, hz0, hz1 = 12, 43, 8, 62      # great hall

    # ---- foundation + dungeon ----
    p.fill(0, W - 1, 0, GY - 1, 0, D - 1, FOUND)
    p.clear(24, 31, 1, 3, 16, 52)
    p.floor(24, 31, 0, 16, 52, FLOOR)
    for cz in (20, 30, 40, 50):
        for cx in (20, 35):
            p.clear(cx - 3, cx + 3, 1, 3, cz - 2, cz + 2); p.walls(cx - 3, cx + 3, 1, 3, cz - 2, cz + 2, WALL)
            p.fill(cx + (3 if cx < 27 else -3), cx + (3 if cx < 27 else -3), 1, 3, cz - 1, cz + 1, BARS)
        p.set(27, 3, cz, LAMP)

    # ---- main floor ----
    p.floor(2, W - 3, GY, 2, D - 3, FLOOR)
    p.clear(27, 28, GY, GY, 50, 53)
    for i, zz in enumerate(range(50, 54)):
        p.fill(27, 28, GY - 1 - i, GY - 1 - i, zz, zz, FOUND)

    # ---- outer shell + buttresses + windows ----
    p.walls(2, W - 3, GY, WT - 1, 2, D - 3, WALL)
    for by in (GY + 6, GY + 13, GY + 20):
        for xx in range(2, W - 2):
            p.set(xx, by, 2, ACCENT); p.set(xx, by, D - 3, ACCENT)
        for zz in range(2, D - 2):
            p.set(2, by, zz, ACCENT); p.set(W - 3, by, zz, ACCENT)
    for zz in range(8, D - 6, 6):            # tall arched windows all around
        for wx in (2, W - 3):
            p.fill(wx, wx, GY + 4, GY + 11, zz - 1, zz + 1, GLASS); p.set(wx, GY + 12, zz, GLASS)
    for xx in range(10, W - 8, 8):
        p.fill(xx, xx, GY + 4, GY + 11, 2, 2, GLASS); p.fill(xx, xx, GY + 4, GY + 11, D - 3, D - 3, GLASS)

    # ---- great hall ----
    p.clear(hx0, hx1, GY + 1, WT - 1, hz0, hz1)
    p.floor(hx0, hx1, GY, hz0, hz1, FLOOR)
    p.fill(26, 29, GY + 1, GY + 1, 8, 56, CARPET)                 # runner
    p.fill(25, 30, GY + 1, GY + 1, 8, 56, CARPET2)
    p.fill(26, 29, GY + 1, GY + 1, 8, 56, CARPET)
    for cz in range(12, 60, 6):                                   # colonnade + sconces + braziers
        for cx in (15, 40):
            p.pillar(cx, cz, GY + 1, WT - 3, PILLAR, {"axis": "y"})
            p.set(cx, GY + 4, cz, GLOWSTALK); p.set(cx, WT - 2, cz, ACCENT)
        p.fill(15, 40, WT - 3, WT - 3, cz, cz, ACCENT)
        p.hang_lantern(23, WT - 2, cz, 4); p.hang_lantern(32, WT - 2, cz, 4)
    for cz in (14, 26, 38, 50):
        p.brazier(18, GY + 1, cz); p.brazier(37, GY + 1, cz)
    # banquet tables + chairs down the hall
    for cz in (16, 34):
        p.fill(20, 35, GY + 2, GY + 2, cz, cz + 1, CSLAB, {"type": "top"})
        for tx in range(20, 36, 3):
            p.set(tx, GY + 2, cz, LANTERN);
        for tx in range(20, 36, 2):
            p.stair(tx, GY + 1, cz - 1, CSTAIR, "south")
            p.stair(tx, GY + 1, cz + 2, CSTAIR, "north")

    # ---- throne dais ----
    for i in range(4):
        p.fill(20 - 0, 35, GY + i, GY + i, 52 + i, 52 + i, CRYS)
        p.stair(20, GY + i, 51 + i, CRYS_STAIR, "north")
    p.fill(20, 35, GY + 4, GY + 4, 55, 60, FOUND)
    p.fill(22, 33, GY + 5, GY + 13, 60, 60, GLOWB)               # glowing backdrop
    for xx in (21, 34):
        p.pillar(xx, 60, GY + 4, GY + 12, PILLAR, {"axis": "y"})
        p.brazier(xx, GY + 4, 56)
    p.set(27, GY + 5, 58, PILLAR, {"axis": "y"}); p.set(28, GY + 5, 58, PILLAR, {"axis": "y"})
    p.set(27, GY + 6, 58, GLOWB); p.set(28, GY + 6, 58, GLOWB)   # boss pedestal
    p.stair(27, GY + 5, 57, CSTAIR, "south"); p.stair(28, GY + 5, 57, CSTAIR, "south")
    # bookshelves flanking throne
    for zz in range(56, 61):
        p.fill(20, 20, GY + 1, GY + 3, zz, zz, BOOK); p.fill(35, 35, GY + 1, GY + 3, zz, zz, BOOK)

    # ---- entrance: grand stair + portico ----
    for i in range(7):
        p.fill(22 - i, 33 + i, GY - 1 - i, GY - 1 - i, 2, 2, FOUND)
        p.stair(22 - i, GY - 1 - i, 3, VOID_STAIR, "south"); p.stair(33 + i, GY - 1 - i, 3, VOID_STAIR, "south")
    p.clear(25, 30, GY + 1, GY + 7, 2, 6)
    for px in (23, 32):
        p.pillar(px, 5, GY, GY + 10, PILLAR, {"axis": "y"}); p.brazier(px, GY, 5)
    p.fill(23, 32, GY + 11, GY + 11, 3, 6, ACCENT)

    # ---- furnished wing rooms (3 floors) ----
    def furnish(kind, rx0, rx1, fy, rz0, rz1):
        p.set(rx0 + 1, fy + 1, rz0 + 1, CHEST, {"facing": "south"})
        p.hang_lantern((rx0 + rx1) // 2, fy + 5, (rz0 + rz1) // 2, 2)
        p.fill(rx0 + 1, rx1 - 1, fy + 1, fy + 1, rz0 + 1, rz1 - 1, CARPET)
        if kind == "library":
            for zz in range(rz0 + 1, rz1):
                p.fill(rx1 - 1, rx1 - 1, fy + 1, fy + 3, zz, zz, BOOK)
                p.fill(rx0 + 1, rx0 + 1, fy + 1, fy + 3, zz, zz, BOOK)
            p.set((rx0 + rx1) // 2, fy + 1, (rz0 + rz1) // 2, LECTERN, {"facing": "north"})
        elif kind == "dining":
            p.fill(rx0 + 2, rx1 - 2, fy + 2, fy + 2, (rz0 + rz1) // 2, (rz0 + rz1) // 2, CSLAB, {"type": "top"})
            for tx in range(rx0 + 2, rx1 - 1, 2):
                p.stair(tx, fy + 1, (rz0 + rz1) // 2 - 1, CSTAIR, "south")
                p.stair(tx, fy + 1, (rz0 + rz1) // 2 + 1, CSTAIR, "north")
            p.set((rx0 + rx1) // 2, fy + 2, (rz0 + rz1) // 2, LANTERN)
        elif kind == "store":
            for zz in range(rz0 + 1, rz1, 2):
                p.set(rx1 - 1, fy + 1, zz, BARREL, {"facing": "up"})
                p.set(rx1 - 1, fy + 2, zz, BARREL, {"facing": "up"})
        else:  # quarters
            p.fill(rx0 + 1, rx0 + 2, fy + 1, fy + 1, rz1 - 2, rz1 - 1, CSLAB, {"type": "top"})  # bed-ish
            p.set(rx0 + 3, fy + 1, rz1 - 1, LECTERN, {"facing": "west"})

    kinds = ["library", "dining", "quarters", "store"]
    for side in ((2, 11), (44, 53)):
        for fi, fy in enumerate((GY, GY + 8, GY + 16)):
            for ri, (rz0, rz1) in enumerate(((8, 24), (26, 42), (44, 61))):
                p.clear(side[0] + 1, side[1] - 1, fy + 1, fy + 6, rz0 + 1, rz1 - 1)
                p.floor(side[0], side[1], fy, rz0, rz1, FLOOR)
                for wz in range(rz0 + 2, rz1, 4):
                    p.set(side[0], fy + 3, wz, GLASS); p.set(side[1], fy + 3, wz, GLASS)
                furnish(kinds[(fi + ri) % 4], side[0], side[1], fy, rz0, rz1)
            # doorway into hall on ground floor
            mz = 35
            if fy == GY:
                if side[0] < 12:
                    p.clear(11, 12, GY + 1, GY + 3, mz - 1, mz + 1)
                else:
                    p.clear(43, 44, GY + 1, GY + 3, mz - 1, mz + 1)
        # balcony railings overlooking hall (upper floors)
        edge = 11 if side[0] < 12 else 44
        for fy in (GY + 8, GY + 16):
            for zz in range(hz0, hz1, 1):
                p.set(edge, fy, zz, OBSW)

    # ---- garden atrium (top-back-left room) ----
    gx0, gx1, gz0, gz1 = 2, 11, 44, 61
    p.floor(gx0, gx1, GY + 17, gz0, gz1, GRASS)
    p.floor(gx0 + 2, gx1 - 2, GY + 17, gz0 + 2, gz1 - 2, MOSS)
    for gz in range(gz0 + 2, gz1, 4):
        p.pillar(gx0 + 3, gz, GY + 18, GY + 20, CLOG, {"axis": "y"})
        p.fill(gx0 + 1, gx0 + 5, GY + 21, GY + 21, gz - 1, gz + 1, CLEAF)
        p.set(gx0 + 3, GY + 22, gz, CLEAF)
        p.set(gx1 - 2, GY + 18, gz, GLOWSTALK); p.set(gx0 + 6, GY + 18, gz + 1, BLOOM)

    # ---- full roof deck (covers everything) + battlements ----
    p.floor(2, W - 3, WT, 2, D - 3, ROOF)
    p.crenellate(2, W - 3, 2, D - 3, WT + 1, OBSW)
    # rooftop walkway lighting
    for zz in range(6, D - 4, 8):
        p.set(4, WT + 1, zz, LANTERN, {"hanging": "false"}); p.set(W - 5, WT + 1, zz, LANTERN, {"hanging": "false"})

    # ---- big peaked great-hall roof (on the deck) ----
    rx0, rx1 = hx0 - 1, hx1 + 1
    half = (rx1 - rx0) // 2
    for i in range(half + 1):
        y = WT + 1 + i
        xa, xb = rx0 + i, rx1 - i
        p.fill(xa, xa, y, y, hz0 - 1, hz1 + 1, ROOF if i % 2 else ROOF2)
        p.fill(xb, xb, y, y, hz0 - 1, hz1 + 1, ROOF if i % 2 else ROOF2)
        if xa >= xb:
            break
    # gable-end triangles
    for i in range(half + 1):
        p.fill(rx0 + i, rx1 - i, WT + 1 + i, WT + 1 + i, hz0 - 1, hz0 - 1, ACCENT)
        p.fill(rx0 + i, rx1 - i, WT + 1 + i, WT + 1 + i, hz1 + 1, hz1 + 1, ACCENT)

    # ---- tall corner spires + grand central spire ----
    for (cx, cz) in ((6, 6), (6, D - 7), (W - 7, 6), (W - 7, D - 7)):
        p.spire(cx, cz, GY, 34, 3, WALL, CRYS)
    p.spire((rx0 + rx1) // 2, (hz0 + hz1) // 2, WT + half, 12, 3, CRYS, GLOWB)   # central

    return p


def main():
    p = build()
    out = os.path.join(os.path.dirname(__file__), "..", "schematics", "void_palace.litematic")
    W, H, D, blocks, pal = p.export(os.path.abspath(out), "Void Palace",
                                    "SquareDealSam", "A massive End castle palace for EndReborn.")
    print(f"wrote {out}\n  size {W}x{H}x{D} | {blocks} blocks | {pal} palette entries")


if __name__ == "__main__":
    main()
