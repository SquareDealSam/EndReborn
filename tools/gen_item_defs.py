#!/usr/bin/env python3
"""Generate 1.21.4+ item-model definitions (assets/voidweaver/items/<name>.json).

Since MC 1.21.4 the inventory/held item render is driven by a definition in
`items/` that points at a model, NOT by `models/item/<name>.json` directly.
Without it, block items show the missing (black/purple) texture in the inventory
even though the placed block renders fine.

We already emit a correct `models/item/<name>.json` for every block and item, so
each `items/<name>.json` simply references `voidweaver:item/<name>`.

Run:  python tools/gen_item_defs.py
"""
import json
import os

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
ITEM_MODELS = os.path.join(RES, "assets", "voidweaver", "models", "item")
ITEM_DEFS = os.path.join(RES, "assets", "voidweaver", "items")


def main():
    os.makedirs(ITEM_DEFS, exist_ok=True)
    names = sorted(f[:-5] for f in os.listdir(ITEM_MODELS)
                   if f.endswith(".json") and " " not in f)  # skip iCloud "name 2.json" dupes
    for name in names:
        obj = {"model": {"type": "minecraft:model", "model": f"voidweaver:item/{name}"}}
        with open(os.path.join(ITEM_DEFS, name + ".json"), "w") as fh:
            json.dump(obj, fh, indent=2)
    print(f"wrote {len(names)} item-model definitions to assets/voidweaver/items/")


if __name__ == "__main__":
    main()
