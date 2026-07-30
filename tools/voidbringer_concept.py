#!/usr/bin/env python3
"""Build a 'corrupted villager' concept model of The Voidbringer in Blockbench and
render it from several angles. Keeps the Minecraft villager silhouette (square head,
big protruding nose, robe) but twisted by the End: void-cracked skin, glowing eyes,
crystal growths, tattered dark robe.

Run:  python tools/voidbringer_concept.py <out_dir>
"""
import base64
import io
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from bb_mcp import BB


def tex(color, name, veins=None, flecks=None, seed=0):
    rng = np.random.default_rng(abs(hash((name, seed))) % 2**32)
    r, g, b = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    a = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            d = int(rng.integers(-12, 12))
            a[y, x] = [min(255, max(0, r + d)), min(255, max(0, g + d)), min(255, max(0, b + d)), 255]
    if veins:
        vr, vg, vb = [int(veins[i:i + 2], 16) for i in (1, 3, 5)]
        for _ in range(10):
            x = int(rng.integers(2, 14)); y0 = int(rng.integers(0, 10))
            for y in range(y0, min(16, y0 + int(rng.integers(3, 7)))):
                xx = min(15, max(0, x + int(rng.integers(-1, 2))))
                a[y, xx, :3] = [vr, vg, vb]
    if flecks:
        fr, fg, fb = [int(flecks[i:i + 2], 16) for i in (1, 3, 5)]
        for _ in range(8):
            y, x = int(rng.integers(0, 16)), int(rng.integers(0, 16))
            a[y, x, :3] = [fr, fg, fb]
    buf = io.BytesIO(); Image.fromarray(a, "RGBA").save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# part: (name, group, from, to, texture)
SKIN, ROBE, CRYS, EYE, DARK = "skin", "robe", "crystal", "eye", "dark"
PARTS = [
    ("leg_l", "legs", [-5, 0, -2], [-1, 13, 2], ROBE),
    ("leg_r", "legs", [1, 0, -2], [5, 13, 2], ROBE),
    ("robe_skirt", "body", [-7, 11, -4], [7, 21, 4], ROBE),
    ("body", "body", [-6, 21, -3], [6, 32, 3], ROBE),
    ("sash", "body", [-6, 26, -3.3], [6, 28, -2.7], CRYS),
    ("arm_l", "arms", [-9, 19, -2], [-6, 32, 2], ROBE),
    ("hand_l", "arms", [-9, 14, -2], [-6, 19, 2], SKIN),
    ("arm_r", "arms", [6, 19, -2], [9, 32, 2], ROBE),
    ("hand_r", "arms", [6, 14, -2], [9, 19, 2], SKIN),
    ("collar", "head", [-7, 41, -3], [7, 45, 4], DARK),
    ("head", "head", [-6, 32, -4], [6, 44, 4], SKIN),
    ("brow", "head", [-6, 40, -4.6], [6, 41, -3.6], DARK),
    ("nose", "head", [-2, 36, -7], [2, 41, -4], SKIN),
    ("eye_l", "head", [-5, 37, -4.7], [-2, 39, -4.1], EYE),
    ("eye_r", "head", [2, 37, -4.7], [5, 39, -4.1], EYE),
    # crystal growths
    ("shard_sl", "shards", [-8.5, 31, -1], [-6, 39, 1], CRYS),
    ("shard_sr", "shards", [6, 31, -1], [8.5, 39, 1], CRYS),
    ("crown1", "shards", [-4, 44, -1], [-2.5, 50, 0.5], CRYS),
    ("crown2", "shards", [-1, 44, -1], [0.5, 52, 0.5], CRYS),
    ("crown3", "shards", [2, 44, -1], [3.5, 49, 0.5], CRYS),
    ("back1", "shards", [-2, 25, 3], [-0.5, 34, 5.5], CRYS),
    ("back2", "shards", [1, 27, 3], [2.5, 37, 5.5], CRYS),
]


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    bb = BB()
    bb.call("create_project", {"name": "voidbringer_concept", "format": "modded_entity"})
    bb.call("create_texture", {"name": SKIN, "data": tex("#6f6684", "skin", veins="#3a2456", flecks="#c050e0")})
    bb.call("create_texture", {"name": ROBE, "data": tex("#241636", "robe", veins="#5a2a7a", flecks="#57e8ff")})
    bb.call("create_texture", {"name": CRYS, "data": tex("#57e8ff", "crystal", flecks="#b0ffff")})
    bb.call("create_texture", {"name": EYE, "data": tex("#c8ffff", "eye")})
    bb.call("create_texture", {"name": DARK, "data": tex("#140c1c", "dark")})
    for g in ("legs", "body", "arms", "head", "shards"):
        bb.call("add_group", {"name": g, "origin": [0, 20, 0], "rotation": [0, 0, 0]})
    for name, group, frm, to, texture in PARTS:
        bb.call("place_cube", {"elements": [{"name": name, "from": frm, "to": to,
                 "origin": [(frm[0] + to[0]) / 2, (frm[1] + to[1]) / 2, (frm[2] + to[2]) / 2]}],
                 "group": group, "texture": texture, "faces": True})
    print("built corrupted-villager model")

    views = {
        "front":   [0, 30, -95],
        "threequarter": [70, 46, -70],
        "side":    [95, 32, 0],
        "back":    [40, 40, 85],
    }
    for vname, pos in views.items():
        bb.call("set_camera_angle", {"position": pos, "target": [0, 24, 0], "projection": "perspective"})
        r = bb.call("capture_screenshot", {})
        for blk in r.get("content", []):
            if blk.get("type") == "image":
                p = os.path.join(out_dir, f"voidbringer_{vname}.png")
                open(p, "wb").write(base64.b64decode(blk["data"]))
                print("rendered", p)
                break


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
