#!/usr/bin/env python3
"""Minimal gzip-NBT writer + Minecraft structure-template (.nbt) builder.

Only the tag types needed for structure templates are implemented. Nodes are
typed tuples: ('int', v) ('double', v) ('string', v) ('list', subtype, [nodes])
('compound', {name: node}) ('int_array', [ints]).
"""
import gzip
import io
import struct

DATA_VERSION = 4903  # Minecraft 26.2

TYPEID = {"byte": 1, "short": 2, "int": 3, "long": 4, "float": 5,
          "double": 6, "string": 8, "list": 9, "compound": 10, "int_array": 11}


def _str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _payload(f, node):
    t = node[0]
    if t == "byte":
        f.write(struct.pack(">b", node[1]))
    elif t == "int":
        f.write(struct.pack(">i", node[1]))
    elif t == "long":
        f.write(struct.pack(">q", node[1]))
    elif t == "float":
        f.write(struct.pack(">f", node[1]))
    elif t == "double":
        f.write(struct.pack(">d", node[1]))
    elif t == "string":
        f.write(_str(node[1]))
    elif t == "int_array":
        f.write(struct.pack(">i", len(node[1])))
        for v in node[1]:
            f.write(struct.pack(">i", v))
    elif t == "list":
        _, subtype, items = node
        f.write(struct.pack(">b", TYPEID[subtype]))
        f.write(struct.pack(">i", len(items)))
        for it in items:
            _payload(f, it)
    elif t == "compound":
        for k, v in node[1].items():
            f.write(struct.pack(">b", TYPEID[v[0]]))
            f.write(_str(k))
            _payload(f, v)
        f.write(b"\x00")
    else:
        raise ValueError("unknown tag " + t)


def write_nbt(path, root):
    buf = io.BytesIO()
    buf.write(struct.pack(">b", TYPEID["compound"]))
    buf.write(_str(""))
    _payload(buf, root)
    with gzip.open(path, "wb") as f:
        f.write(buf.getvalue())


def ivec(xyz):
    return ("list", "int", [("int", int(v)) for v in xyz])


def dvec(xyz):
    return ("list", "double", [("double", float(v)) for v in xyz])


class Structure:
    """Build a structure by placing blocks in a grid, then export the template NBT."""

    def __init__(self):
        self.blocks = {}    # (x,y,z) -> (name, props_dict_or_None, be_node_or_None)
        self.entities = []  # (x,y,z, id)

    def set(self, x, y, z, name, props=None, be=None):
        self.blocks[(x, y, z)] = (name, props, be)

    def fill(self, x0, y0, z0, x1, y1, z1, name, props=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, name, props)

    def hollow(self, x0, y0, z0, x1, y1, z1, name, props=None):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if x in (x0, x1) or y in (y0, y1) or z in (z0, z1):
                        self.set(x, y, z, name, props)

    def chest(self, x, y, z, loot_table, facing="north"):
        be = ("compound", {"id": ("string", "minecraft:chest"),
                           "LootTable": ("string", loot_table)})
        self.set(x, y, z, "minecraft:chest", {"facing": facing}, be)

    def entity(self, x, y, z, entity_id):
        self.entities.append((x, y, z, entity_id))

    def _palette_key(self, name, props):
        return (name, tuple(sorted((props or {}).items())))

    def to_nbt(self):
        xs = [p[0] for p in self.blocks] or [0]
        ys = [p[1] for p in self.blocks] or [0]
        zs = [p[2] for p in self.blocks] or [0]
        sx, sy, sz = max(xs) + 1, max(ys) + 1, max(zs) + 1

        palette, pindex = [], {}
        for (name, props, _be) in self.blocks.values():
            k = self._palette_key(name, props)
            if k not in pindex:
                pindex[k] = len(palette)
                entry = {"Name": ("string", name)}
                if props:
                    entry["Properties"] = ("compound", {pk: ("string", str(pv)) for pk, pv in props.items()})
                palette.append(("compound", entry))

        block_nodes = []
        for (x, y, z), (name, props, be) in self.blocks.items():
            comp = {"pos": ivec((x, y, z)), "state": ("int", pindex[self._palette_key(name, props)])}
            if be is not None:
                comp["nbt"] = be
            block_nodes.append(("compound", comp))

        entity_nodes = []
        for (x, y, z, eid) in self.entities:
            enbt = ("compound", {"id": ("string", eid), "Pos": dvec((x + 0.5, y, z + 0.5))})
            entity_nodes.append(("compound", {
                "blockPos": ivec((x, y, z)),
                "pos": dvec((x + 0.5, y, z + 0.5)),
                "nbt": enbt}))

        return ("compound", {
            "size": ivec((sx, sy, sz)),
            "palette": ("list", "compound", palette),
            "blocks": ("list", "compound", block_nodes),
            "entities": ("list", "compound", entity_nodes),
            "DataVersion": ("int", DATA_VERSION),
        })

    def save(self, path):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_nbt(path, self.to_nbt())
