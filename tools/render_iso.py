#!/usr/bin/env python3
"""Render an isometric PNG preview of a builder's block grid (sanity-check builds).

Usage:  python tools/render_iso.py castle out.png [tile]
        python tools/render_iso.py palace out.png
"""
import importlib
import sys

from PIL import Image, ImageDraw

COLORS = {
    "obsidian_bricks": (52, 36, 62), "obsidian": (38, 26, 44),
    "polished_void_stone": (58, 50, 86), "void_stone_bricks": (66, 58, 96),
    "end_stone_bricks": (214, 212, 166), "crystal_stone_bricks": (152, 182, 214),
    "purpur": (178, 126, 184), "void_crystal_block": (92, 234, 255),
    "sea_lantern": (226, 242, 242), "purple_stained_glass": (152, 92, 182),
    "purple_carpet": (140, 70, 170), "magenta_carpet": (182, 92, 192),
    "chorus_leaves": (152, 72, 182), "chorus": (142, 92, 152),
    "glowstalk": (80, 255, 204), "glow_fungus": (255, 216, 90), "giant_bloom": (255, 110, 180),
    "alien_grass": (72, 182, 112), "void_moss": (122, 92, 192),
    "shroomlight": (255, 150, 90), "lantern": (255, 212, 122), "campfire": (255, 152, 82),
    "bookshelf": (172, 132, 82), "iron_bars": (142, 142, 152), "chain": (92, 92, 102),
    "barrel": (152, 112, 72), "chest": (162, 122, 72), "water": (64, 108, 220),
    "lectern": (168, 128, 78),
}


def color(name):
    for k, v in COLORS.items():
        if k in name:
            return v
    return (112, 102, 122)


def render(grid, out, t=6):
    g = {k: v for k, v in grid.items() if v[0] != "minecraft:air"}
    def proj(x, y, z):
        return (x - z) * t, (x + z) * (t // 2) - y * t
    pts = [proj(*c) for c in g]
    minsx = min(a for a, _ in pts); minsy = min(b for _, b in pts)
    W = max(a for a, _ in pts) - minsx + t * 3
    H = max(b for _, b in pts) - minsy + t * 3
    img = Image.new("RGBA", (W, H), (14, 12, 22, 255))
    d = ImageDraw.Draw(img)
    ox, oy = -minsx + t, -minsy + t
    N = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for (x, y, z) in sorted(g, key=lambda c: (c[0] + c[2]) * 2 - c[1]):
        if all((x + dx, y + dy, z + dz) in g for dx, dy, dz in N):
            continue
        r, gr, b = color(g[(x, y, z)][0])
        sx, sy = proj(x, y, z); sx += ox; sy += oy
        d.polygon([(sx, sy), (sx + t, sy + t // 2), (sx, sy + t), (sx - t, sy + t // 2)], fill=(r, gr, b))
        d.polygon([(sx - t, sy + t // 2), (sx, sy + t), (sx, sy + 2 * t), (sx - t, sy + t // 2 + t)],
                  fill=(int(r * .58), int(gr * .58), int(b * .58)))
        d.polygon([(sx, sy + t), (sx + t, sy + t // 2), (sx + t, sy + t // 2 + t), (sx, sy + 2 * t)],
                  fill=(int(r * .8), int(gr * .8), int(b * .8)))
    img.thumbnail((1600, 1600))
    img.save(out)
    return img.size


if __name__ == "__main__":
    mod = importlib.import_module(sys.argv[1])
    tile = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    print("rendered", render(mod.build().g, sys.argv[2], tile))
