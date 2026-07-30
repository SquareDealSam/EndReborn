#!/usr/bin/env python3
"""Build the corrupted-villager Voidbringer in Blockbench with correctly applied
per-part textures (the earlier version rendered one muddy colour because the
place_cube texture arg didn't stick — we force it with apply_texture), then render.

Run:  python tools/voidbringer_bb.py <out_dir>
"""
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from bb_mcp import BB
from voidbringer_concept import PARTS, tex, SKIN, ROBE, CRYS, EYE, DARK


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    bb = BB()
    bb.call("create_project", {"name": "voidbringer", "format": "modded_entity"})
    textures = {
        SKIN: tex("#7a7092", "skin", veins="#3a2456", flecks="#c050e0"),
        ROBE: tex("#211534", "robe", veins="#5a2a7a", flecks="#57e8ff"),
        CRYS: tex("#57e8ff", "crystal", flecks="#c8ffff"),
        EYE:  tex("#d6ffff", "eye"),
        DARK: tex("#130b1c", "dark"),
    }
    for name, data in textures.items():
        bb.call("create_texture", {"name": name, "data": data})
    for g in ("legs", "body", "arms", "head", "shards"):
        bb.call("add_group", {"name": g, "origin": [0, 20, 0], "rotation": [0, 0, 0]})
    for name, group, frm, to, texture in PARTS:
        bb.call("place_cube", {"elements": [{"name": name, "from": frm, "to": to,
                 "origin": [(frm[0] + to[0]) / 2, (frm[1] + to[1]) / 2, (frm[2] + to[2]) / 2]}],
                 "group": group, "texture": texture, "faces": True})
    # force the correct texture onto every element (the fix)
    applied = 0
    for name, group, frm, to, texture in PARTS:
        try:
            bb.call("apply_texture", {"id": name, "texture": texture, "applyTo": "all"})
            applied += 1
        except Exception as e:
            print("apply failed", name, e)
    print(f"built model; textures applied to {applied}/{len(PARTS)} parts")

    for vname, pos in {"front": [0, 30, -95], "threequarter": [70, 46, -70],
                       "side": [95, 32, 0]}.items():
        bb.call("set_camera_angle", {"position": pos, "target": [0, 24, 0], "projection": "perspective"})
        r = bb.call("capture_screenshot", {})
        for blk in r.get("content", []):
            if blk.get("type") == "image":
                p = os.path.join(out_dir, f"vb_bb_{vname}.png")
                open(p, "wb").write(base64.b64decode(blk["data"]))
                print("rendered", p)
                break
    # full-app view so the user sees it inside Blockbench
    r = bb.call("capture_app_screenshot", {})
    for blk in r.get("content", []):
        if blk.get("type") == "image":
            open(os.path.join(out_dir, "vb_bb_app.png"), "wb").write(base64.b64decode(blk["data"]))
            print("rendered app view")
            break


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
