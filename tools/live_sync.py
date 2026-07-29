#!/usr/bin/env python3
"""Live Blockbench -> mod resource sync.

Polls the running Blockbench (MCP) for the CURRENT project's textures and writes
any that changed into the mod's resource tree, mapping by texture name to the file
that already owns that name (block/, item/, entity/equipment/...). New names default
to textures/block/. Textures only — block MODELS are template-generated and must not
be clobbered by preview projects; entity models are exported explicitly when built.

Run (background):  python tools/live_sync.py
"""
import base64
import hashlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from bb_mcp import BB

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
TEXROOT = os.path.join(RES, "assets", "endreborn", "textures")
POLL = 2.5


def build_index():
    """texture-name -> absolute path, from existing PNGs in the mod."""
    idx = {}
    for root, _, files in os.walk(TEXROOT):
        for f in files:
            if f.endswith(".png"):
                idx[f[:-4]] = os.path.join(root, f)
    return idx


def sha(b):
    return hashlib.sha256(b).hexdigest()


def disk_hashes(index):
    h = {}
    for name, path in index.items():
        try:
            h[name] = sha(open(path, "rb").read())
        except OSError:
            pass
    return h


def png_of(result):
    for b in result.get("content", []):
        if b.get("type") == "image":
            return base64.b64decode(b["data"])
    return None


def main():
    bb = BB()
    index = build_index()
    hashes = disk_hashes(index)
    print(f"[live_sync] watching Blockbench; {len(index)} known textures. Poll {POLL}s.")
    misses = 0
    while True:
        try:
            index.update(build_index())  # pick up newly-added asset paths
            texs = bb.call("list_textures", {})
            names = []
            for b in texs.get("content", []):
                if b.get("type") == "text":
                    import json as _j
                    try:
                        data = _j.loads(b["text"])
                        names = [t.get("name") for t in (data if isinstance(data, list)
                                 else data.get("textures", [])) if t.get("name")]
                    except Exception:
                        pass
            for name in names:
                if not name:
                    continue
                png = png_of(bb.call("get_texture", {"texture": name}))
                if not png:
                    continue
                h = sha(png)
                if hashes.get(name) == h:
                    continue
                path = index.get(name) or os.path.join(TEXROOT, "block", name + ".png")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "wb").write(png)
                index[name] = path
                hashes[name] = h
                rel = os.path.relpath(path, RES)
                print(f"[live_sync] updated {rel}", flush=True)
            misses = 0
        except Exception as e:
            misses += 1
            if misses <= 3 or misses % 20 == 0:
                print(f"[live_sync] poll error ({misses}): {e}", flush=True)
            if misses in (4, 8, 16):  # session may have dropped; reconnect
                try:
                    bb = BB()
                except Exception:
                    pass
        time.sleep(POLL)


if __name__ == "__main__":
    main()
