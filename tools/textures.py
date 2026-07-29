#!/usr/bin/env python3
"""End-themed 16x16 pixel-art texture generator for EndReborn.

Pure procedural PIL/numpy. Deterministic per (name, seed) so re-runs are stable.
Each generator returns a PIL.Image (RGBA, 16x16). Helpers save PNG + data URLs so
the same bytes go both into the mod resources and into Blockbench live.
"""
import base64
import io
import numpy as np
from PIL import Image

S = 16  # texture size


def _rng(name, seed=0):
    return np.random.default_rng(abs(hash((name, seed))) % (2**32))


def _img(arr):
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def _hex(c):
    c = c.lstrip("#")
    if len(c) == 6:
        c += "ff"
    return [int(c[i:i + 2], 16) for i in (0, 2, 4, 6)]


def _base(color, name, seed=0, amp=14, alpha=255):
    """Speckled stone-like fill."""
    r, g, b, _ = _hex(color)
    rng = _rng(name, seed)
    noise = rng.integers(-amp, amp + 1, (S, S))
    arr = np.zeros((S, S, 4))
    arr[..., 0] = np.clip(r + noise, 0, 255)
    arr[..., 1] = np.clip(g + noise, 0, 255)
    arr[..., 2] = np.clip(b + noise, 0, 255)
    arr[..., 3] = alpha
    # a few darker pits / lighter grains
    for _ in range(10):
        y, x = rng.integers(0, S, 2)
        d = rng.choice([-30, 26])
        arr[y, x, :3] = np.clip(arr[y, x, :3] + d, 0, 255)
    return arr


def stone(color, name, seed=0):
    return _img(_base(color, name, seed))


def ore(base_color, blob_color, name, seed=0, blobs=5):
    arr = _base(base_color, name, seed)
    br, bg, bb_, _ = _hex(blob_color)
    rng = _rng(name + "_ore", seed)
    # scatter a few crystalline veins (2-3 px clusters)
    for _ in range(blobs):
        cy, cx = rng.integers(2, S - 2, 2)
        for dy, dx in [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1)]:
            if rng.random() < 0.7:
                y, x = cy + dy, cx + dx
                if 0 <= y < S and 0 <= x < S:
                    shade = rng.integers(-18, 19)
                    arr[y, x, 0] = np.clip(br + shade, 0, 255)
                    arr[y, x, 1] = np.clip(bg + shade, 0, 255)
                    arr[y, x, 2] = np.clip(bb_ + shade, 0, 255)
    return _img(arr)


def bricks(color, mortar, name, seed=0):
    r, g, b, _ = _hex(color)
    mr, mg, mb, _ = _hex(mortar)
    arr = _base(color, name, seed, amp=8)
    # mortar lines: horizontal every 4px, vertical offset per row-band
    for y in range(S):
        row_band = y // 4
        for x in range(S):
            on_h = (y % 4 == 0)
            offset = 0 if row_band % 2 == 0 else 4
            on_v = ((x + offset) % 8 == 0)
            if on_h or on_v:
                arr[y, x, :3] = [mr, mg, mb]
    return _img(arr)


def polished(color, name, seed=0):
    """Smoother, brighter version of a stone."""
    return _img(_base(color, name, seed, amp=5))


def chiseled(color, mortar, name, seed=0):
    arr = _base(color, name, seed, amp=6)
    mr, mg, mb, _ = _hex(mortar)
    # border frame + a central motif
    arr[0, :, :3] = arr[-1, :, :3] = [mr, mg, mb]
    arr[:, 0, :3] = arr[:, -1, :3] = [mr, mg, mb]
    r, g, b, _ = _hex(color)
    for y in range(4, 12):
        for x in range(4, 12):
            if (x + y) % 2 == 0:
                arr[y, x, :3] = np.clip(np.array([r, g, b]) + 22, 0, 255)
    return _img(arr)


def planks(color, name, seed=0):
    r, g, b, _ = _hex(color)
    arr = _base(color, name, seed, amp=10)
    dark = np.clip(np.array([r, g, b]) - 34, 0, 255)
    rng = _rng(name + "_pl", seed)
    # 4 vertical-plank seams + horizontal offsets
    for x in (0, 8):
        arr[:, x, :3] = dark
    for band, y0 in enumerate((0, 8)):
        seam_x = 4 if band % 2 == 0 else 12
        arr[y0, :, :3] = dark
        for y in range(y0, min(y0 + 8, S)):
            arr[y, seam_x % S, :3] = dark
    # grain flecks
    for _ in range(14):
        y, x = rng.integers(0, S, 2)
        arr[y, x, :3] = np.clip(arr[y, x, :3] - 18, 0, 255)
    return _img(arr)


def log_side(bark, streak, name, seed=0):
    r, g, b, _ = _hex(bark)
    arr = _base(bark, name, seed, amp=9)
    sc = _hex(streak)[:3]
    rng = _rng(name + "_ls", seed)
    for x in range(S):
        if rng.random() < 0.28:
            arr[:, x, :3] = np.clip(np.array(sc) + rng.integers(-10, 11), 0, 255)
    return _img(arr)


def log_top(ring, core, name, seed=0):
    arr = _base(ring, name, seed, amp=6)
    cc = _hex(core)[:3]
    rc = _hex(ring)[:3]
    yy, xx = np.mgrid[0:S, 0:S]
    dist = np.sqrt((yy - 7.5) ** 2 + (xx - 7.5) ** 2)
    for y in range(S):
        for x in range(S):
            d = dist[y, x]
            t = (np.sin(d * 1.4) + 1) / 2
            col = np.array(cc) * (1 - t) + np.array(rc) * t
            arr[y, x, :3] = np.clip(col, 0, 255)
    return _img(arr)


def _shape_item(mask, color, name, seed=0, shade=True):
    """Render an item silhouette (mask 16x16 bool) with simple shading."""
    r, g, b, _ = _hex(color)
    arr = np.zeros((S, S, 4))
    rng = _rng(name + "_it", seed)
    for y in range(S):
        for x in range(S):
            if mask[y, x]:
                s = rng.integers(-16, 12) if shade else 0
                # top-left light, bottom-right dark
                s += int((S - y - x) * 0.8)
                arr[y, x] = [np.clip(r + s, 0, 255), np.clip(g + s, 0, 255),
                             np.clip(b + s, 0, 255), 255]
    return _img(arr)


def ingot(color, name, seed=0):
    mask = np.zeros((S, S), bool)
    # trapezoidal ingot
    for y in range(6, 12):
        inset = (y - 6)
        for x in range(3 + inset // 2, 13 - inset // 2):
            mask[y, x] = True
    mask[5, 5:11] = True
    return _shape_item(mask, color, name, seed)


def gem(color, name, seed=0):
    mask = np.zeros((S, S), bool)
    # diamond/crystal
    for y in range(2, 14):
        half = 7 - abs(y - 8)
        half = max(1, half)
        for x in range(8 - half, 8 + half):
            mask[y, x] = True
    return _shape_item(mask, color, name, seed)


def shard(color, name, seed=0):
    mask = np.zeros((S, S), bool)
    for y in range(4, 13):
        w = max(1, (12 - y) // 1)
        for x in range(7 - w // 2, 9 + w // 2):
            if 0 <= x < S:
                mask[y, x] = True
    mask[3, 7:9] = True
    return _shape_item(mask, color, name, seed)


def door_panel(color, name, top=False, seed=0):
    """16x16 door half: plank fill, frame, cross-brace, and a handle on the top half."""
    r, g, b, _ = _hex(color)
    arr = _base(color, name, seed, amp=9)
    dark = np.clip(np.array([r, g, b]) - 34, 0, 255)
    arr[0, :, :3] = arr[-1, :, :3] = dark
    arr[:, 0, :3] = arr[:, -1, :3] = dark
    for x in range(1, 15):        # horizontal braces
        arr[3, x, :3] = arr[12, x, :3] = dark
    if top:
        for y in range(6, 10):    # handle
            arr[y, 12, :3] = [210, 200, 120]
    else:
        arr[:, 8, :3] = dark      # vertical seam on lower half
    return _img(arr)


def door_item(color, name, seed=0):
    mask = np.zeros((S, S), bool)
    for y in range(1, 15):
        for x in range(4, 12):
            mask[y, x] = True
    img = _shape_item(mask, color, name, seed)
    a = np.array(img)
    a[7, 10] = [220, 210, 130, 255]   # handle
    return _img(a)


def trapdoor_tex(color, name, seed=0):
    r, g, b, _ = _hex(color)
    arr = _base(color, name, seed, amp=9)
    dark = np.clip(np.array([r, g, b]) - 34, 0, 255)
    arr[0, :, :3] = arr[-1, :, :3] = dark
    arr[:, 0, :3] = arr[:, -1, :3] = dark
    for y in (5, 10):
        arr[y, :, :3] = dark
    for _ in range(10):
        rng = _rng(name, seed)
        yy, xx = rng.integers(1, 15, 2)
        arr[yy, xx, :3] = np.clip(arr[yy, xx, :3] - 16, 0, 255)
    return _img(arr)


def leaves_tex(color, name, seed=0):
    r, g, b, _ = _hex(color)
    rng = _rng(name, seed)
    arr = np.zeros((S, S, 4))
    for y in range(S):
        for x in range(S):
            s = rng.integers(-24, 20)
            arr[y, x] = [np.clip(r + s, 0, 255), np.clip(g + s, 0, 255),
                         np.clip(b + s, 0, 255), 255]
    # punch transparent holes for a cutout foliage look
    for _ in range(24):
        y, x = rng.integers(0, S, 2)
        arr[y, x, 3] = 0
    return _img(arr)


def metal_block(color, name, seed=0):
    r, g, b, _ = _hex(color)
    arr = _base(color, name, seed, amp=8)
    light = np.clip(np.array([r, g, b]) + 40, 0, 255)
    dark = np.clip(np.array([r, g, b]) - 40, 0, 255)
    arr[0, :, :3] = arr[:, 0, :3] = light   # top/left bevel
    arr[-1, :, :3] = arr[:, -1, :3] = dark  # bottom/right bevel
    return _img(arr)


def crystal_block(color, name, seed=0):
    r, g, b, _ = _hex(color)
    arr = _base(color, name, seed, amp=18)
    rng = _rng(name, seed)
    # facet lines
    for _ in range(6):
        x0 = rng.integers(0, S)
        for y in range(S):
            x = (x0 + y) % S
            arr[y, x, :3] = np.clip(np.array([r, g, b]) + rng.integers(20, 60), 0, 255)
    return _img(arr)


_TOOL_MASKS = {
    "sword":   [(i, 14 - i) for i in range(2, 12)] + [(12, 2), (13, 1), (11, 3), (10, 4)],
    "pickaxe": [(i, 14 - i) for i in range(3, 13)] + [(2, 2), (2, 3), (2, 11), (2, 12), (3, 2), (3, 12)],
    "axe":     [(i, 14 - i) for i in range(3, 13)] + [(2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (4, 3), (5, 3)],
    "shovel":  [(i, 14 - i) for i in range(3, 12)] + [(2, 3), (2, 4), (3, 2), (3, 3), (3, 4), (4, 3)],
    "hoe":     [(i, 14 - i) for i in range(3, 13)] + [(2, 2), (2, 3), (2, 4), (3, 4)],
}


def tool(kind, color, name, seed=0):
    """Rough handheld-tool silhouette: diagonal handle + a head cluster."""
    mask = np.zeros((S, S), bool)
    # handle: diagonal from bottom-left up to top-right
    for i in range(2, 14):
        for w in (0, 1):
            y, x = 15 - i, i + w
            if 0 <= y < S and 0 <= x < S:
                mask[y, x] = True
    for (y, x) in _TOOL_MASKS[kind]:
        if 0 <= y < S and 0 <= x < S:
            mask[y, x] = True
            if x + 1 < S:
                mask[y, x + 1] = True
    return _shape_item(mask, color, name, seed)


def _fill_rect(mask, y0, y1, x0, x1):
    for y in range(y0, y1):
        for x in range(x0, x1):
            if 0 <= y < S and 0 <= x < S:
                mask[y, x] = True


def armor_icon(kind, color, name, seed=0):
    mask = np.zeros((S, S), bool)
    if kind == "helmet":
        _fill_rect(mask, 3, 9, 4, 12)
        _fill_rect(mask, 9, 11, 4, 6)
        _fill_rect(mask, 9, 11, 10, 12)
    elif kind == "chestplate":
        _fill_rect(mask, 4, 6, 3, 13)
        _fill_rect(mask, 6, 13, 4, 12)
    elif kind == "leggings":
        _fill_rect(mask, 3, 8, 4, 12)
        _fill_rect(mask, 8, 14, 4, 7)
        _fill_rect(mask, 8, 14, 9, 12)
    elif kind == "boots":
        _fill_rect(mask, 6, 10, 3, 6)
        _fill_rect(mask, 6, 10, 9, 12)
        _fill_rect(mask, 10, 13, 2, 7)
        _fill_rect(mask, 10, 13, 8, 13)
    return _shape_item(mask, color, name, seed)


def armor_layer(color, name, seed=0):
    """64x32 equipment layer, flat-tinted with light noise (placeholder)."""
    r, g, b, _ = _hex(color)
    rng = _rng(name, seed)
    w, h = 64, 32
    noise = rng.integers(-10, 11, (h, w))
    arr = np.zeros((h, w, 4))
    arr[..., 0] = np.clip(r + noise, 0, 255)
    arr[..., 1] = np.clip(g + noise, 0, 255)
    arr[..., 2] = np.clip(b + noise, 0, 255)
    arr[..., 3] = 255
    return _img(arr)


def entity_moth(body_color, wing_color, name, seed=0):
    """32x32 entity sheet: body region top-left (texOffs 0,0), wings at (0,10)."""
    rng = _rng(name, seed)
    arr = np.zeros((32, 32, 4))
    br = _hex(body_color)[:3]
    wr = _hex(wing_color)[:3]
    # body block area ~ (0..20, 0..10)
    for y in range(0, 10):
        for x in range(0, 20):
            s = rng.integers(-14, 12)
            arr[y, x] = [np.clip(br[0] + s, 0, 255), np.clip(br[1] + s, 0, 255),
                         np.clip(br[2] + s, 0, 255), 255]
    # wing area ~ (10..22, 0..24)
    for y in range(10, 22):
        for x in range(0, 24):
            s = rng.integers(-20, 24)
            arr[y, x] = [np.clip(wr[0] + s, 0, 255), np.clip(wr[1] + s, 0, 255),
                         np.clip(wr[2] + s, 0, 255), 255]
    # glowing eye speckles on the body
    for _ in range(6):
        y, x = rng.integers(0, 6), rng.integers(0, 18)
        arr[y, x, :3] = [140, 240, 255]
    return _img(arr)


def entity_sheet(base_color, accent_color, name, seed=0, size=64):
    """Generic tinted entity sheet with noise + accent speckles."""
    rng = _rng(name, seed)
    r, g, b, _ = _hex(base_color)
    ar, ag, ab, _ = _hex(accent_color)
    noise = rng.integers(-16, 16, (size, size))
    arr = np.zeros((size, size, 4))
    arr[..., 0] = np.clip(r + noise, 0, 255)
    arr[..., 1] = np.clip(g + noise, 0, 255)
    arr[..., 2] = np.clip(b + noise, 0, 255)
    arr[..., 3] = 255
    for _ in range(size * 3):
        y, x = rng.integers(0, size, 2)
        if rng.random() < 0.5:
            arr[y, x, :3] = [np.clip(ar + rng.integers(-20, 20), 0, 255),
                             np.clip(ag + rng.integers(-20, 20), 0, 255),
                             np.clip(ab + rng.integers(-20, 20), 0, 255)]
    return _img(arr)


def plant_tex(color, name, seed=0, glow=False):
    """16x16 transparent cross-plant: a stem with a bloom cluster on top."""
    r, g, b, _ = _hex(color)
    rng = _rng(name, seed)
    arr = np.zeros((S, S, 4))
    stem = [70, 120, 90] if not glow else [90, 150, 120]
    for y in range(7, 15):            # stem
        arr[y, 7, :3] = stem
        arr[y, 8, :3] = stem
        arr[y, 7, 3] = arr[y, 8, 3] = 255
    for _ in range(26):               # bloom cluster
        y, x = rng.integers(2, 9), rng.integers(4, 12)
        s = rng.integers(-24, 24)
        arr[y, x] = [np.clip(r + s, 0, 255), np.clip(g + s, 0, 255), np.clip(b + s, 0, 255), 255]
    return _img(arr)


def _outline(arr, color=(18, 10, 26, 255)):
    """Add a 1px dark outline around opaque pixels — the key to readable pixel art."""
    op = arr[..., 3] > 10
    out = arr.copy()
    h, w = arr.shape[:2]
    for y in range(h):
        for x in range(w):
            if not op[y, x]:
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and op[ny, nx]:
                        out[y, x] = color
                        break
    return out


def _shade(color, d):
    r, g, b, _ = _hex(color)
    return [np.clip(r + d, 0, 255), np.clip(g + d, 0, 255), np.clip(b + d, 0, 255), 255]


def lush_ground(name, base, moss, spots, seed=0):
    """Vibrant mottled ground cover (alien grass / moss)."""
    rng = _rng(name, seed)
    r, g, b, _ = _hex(base)
    arr = np.zeros((S, S, 4))
    for y in range(S):
        for x in range(S):
            d = rng.integers(-16, 16)
            arr[y, x] = _shade(base, d)
    for _ in range(70):
        y, x = rng.integers(0, S, 2)
        c = moss if rng.random() < 0.6 else rng.choice(spots)
        arr[y, x] = _shade(c, rng.integers(-14, 22))
    return _img(arr)


def alien_plant(name, kind, stem, bloom, glow=False, seed=0):
    """Readable cross-plant: outlined stem + a shaped, highlighted bloom."""
    rng = _rng(name, seed)
    arr = np.zeros((S, S, 4))

    def put(y, x, color, d=0):
        if 0 <= y < S and 0 <= x < S:
            arr[y, x] = _shade(color, d)

    # stem (curved a touch for organic feel)
    sx = 8
    for y in range(15, 5, -1):
        if rng.random() < 0.25:
            sx += rng.choice([-1, 1])
        sx = int(np.clip(sx, 6, 9))
        put(y, sx, stem, rng.integers(-10, 6))
        put(y, sx - 1, stem, rng.integers(-22, -6))

    top = 5
    if kind == "flower":
        for (dy, dx) in [(-1, 0), (-2, 0), (-1, -1), (-1, 1), (-2, -1), (-2, 1), (-3, 0), (0, -2), (0, 2), (-1, -2), (-1, 2)]:
            put(top + dy, sx + dx, bloom, rng.integers(-18, 22))
        put(top - 1, sx, bloom, 60)  # bright center
    elif kind == "stalk":
        for y in range(top - 3, 8):
            put(y, sx, bloom, rng.integers(-6, 30))
            if rng.random() < 0.4:
                put(y, sx + rng.choice([-1, 1]), bloom, 10)
        put(top - 3, sx, bloom, 80)  # luminous tip
    elif kind == "fungus":
        for dx in range(-3, 4):            # cap
            put(top, sx + dx, bloom, rng.integers(-10, 20))
        for dx in range(-2, 3):
            put(top - 1, sx + dx, bloom, rng.integers(0, 30))
        put(top - 2, sx, bloom, 40)
        for dx in (-3, -1, 1, 3):          # spots
            put(top, sx + dx, _hex(bloom)[:3] and "#ffffff", 0)
    elif kind == "crystal":
        for i, (dy, dx) in enumerate([(0, 0), (-1, 0), (-2, 0), (-3, 0), (-1, -2), (-2, -2), (0, 2), (-1, 2), (-2, 3)]):
            put(top + dy, sx + dx, bloom, 20 if i % 2 else -10)
        put(top - 3, sx, bloom, 90)
        put(top - 2, sx - 2, bloom, 70)
    elif kind == "fern":
        for y in range(top, 12):
            put(y, sx, bloom, -6)
            for dx in (-2, -1, 1, 2):
                if rng.random() < 0.6:
                    put(y, sx + dx, bloom, rng.integers(-14, 14))

    arr = _outline(arr)
    if glow:  # brighten a few pixels so emissive plants pop
        op = arr[..., 3] > 10
        ys, xs = np.where(op)
        for _ in range(min(8, len(ys))):
            i = rng.integers(0, len(ys))
            arr[ys[i], xs[i], :3] = np.clip(arr[ys[i], xs[i], :3] + 70, 0, 255)
    return _img(arr)


# ---------- IO helpers ----------

def to_png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def to_data_url(img):
    return "data:image/png;base64," + base64.b64encode(to_png_bytes(img)).decode()


def save(img, path):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG")
