#!/usr/bin/env python3
"""Render clean concept images of the Voidbringer (corrupted villager) from the
same cuboid definition, with exact per-part colors (glowing eyes/crystals)."""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from voidbringer_concept import PARTS

COL = {
    "skin": (152, 140, 168), "robe": (44, 28, 64), "crystal": (96, 232, 255),
    "eye": (210, 255, 255), "dark": (22, 14, 30),
}
GLOW = {"crystal", "eye"}     # rendered near-flat (emissive)


def voxels():
    g = {}
    for name, group, frm, to, texture in PARTS:
        x0, x1 = sorted((round(frm[0]), round(to[0])))
        y0, y1 = sorted((round(frm[1]), round(to[1])))
        z0, z1 = sorted((round(frm[2]), round(to[2])))
        for x in range(x0, max(x1, x0 + 1)):
            for y in range(y0, max(y1, y0 + 1)):
                for z in range(z0, max(z1, z0 + 1)):
                    key = (x, y, z)
                    # let crystal/eye/nose win over body so details show
                    if key not in g or texture in GLOW or name == "nose":
                        g[key] = texture
    return g


def render(g, out, mode="iso", t=10):
    if mode == "iso":
        def proj(x, y, z):
            return (x - z) * t, (x + z) * (t // 2) - y * t
        order = sorted(g, key=lambda c: (c[0] + c[2]) * 2 - c[1])
    else:  # front (look along +z), nose/face toward viewer
        def proj(x, y, z):
            return x * t + (z * t) // 6, -y * t - (z * t) // 6
        order = sorted(g, key=lambda c: -c[2])
    pts = [proj(*c) for c in g]
    minx = min(a for a, _ in pts); miny = min(b for _, b in pts)
    W = max(a for a, _ in pts) - minx + t * 4
    H = max(b for _, b in pts) - miny + t * 4
    img = Image.new("RGBA", (W, H), (18, 15, 26, 255)); d = ImageDraw.Draw(img)
    ox, oy = -minx + t * 2, -miny + t * 2
    N = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for c in order:
        if all((c[0] + dx, c[1] + dy, c[2] + dz) in g for dx, dy, dz in N):
            continue
        r, gr, b = COL[g[c]]
        glow = g[c] in GLOW
        sx, sy = proj(*c); sx += ox; sy += oy
        if mode == "iso":
            top = 1.0 if glow else 1.0
            l = 1.0 if glow else 0.62
            ri = 1.0 if glow else 0.82
            d.polygon([(sx, sy), (sx + t, sy + t // 2), (sx, sy + t), (sx - t, sy + t // 2)],
                      fill=(int(r * top), int(gr * top), int(b * top)))
            d.polygon([(sx - t, sy + t // 2), (sx, sy + t), (sx, sy + 2 * t), (sx - t, sy + t // 2 + t)],
                      fill=(int(r * l), int(gr * l), int(b * l)))
            d.polygon([(sx, sy + t), (sx + t, sy + t // 2), (sx + t, sy + t // 2 + t), (sx, sy + 2 * t)],
                      fill=(int(r * ri), int(gr * ri), int(b * ri)))
        else:
            sh = 1.0 if glow else 0.9
            d.rectangle([sx, sy, sx + t, sy + t], fill=(int(r * sh), int(gr * sh), int(b * sh)),
                        outline=(10, 8, 16))
    img.thumbnail((1100, 1100))
    img.save(out)
    return img.size


if __name__ == "__main__":
    out = sys.argv[1]
    g = voxels()
    print("iso:", render(g, os.path.join(out, "voidbringer_concept_iso.png"), "iso"))
    print("front:", render(g, os.path.join(out, "voidbringer_concept_front.png"), "front"))
