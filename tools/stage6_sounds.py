#!/usr/bin/env python3
"""Stage 6 - all sound effects (mobs, blocks, ambient). NO music.

Synthesizes Minecraft-flavoured SFX (tools/sfx.py), writes .ogg into the mod,
and generates sounds.json + registry/ModSounds.java so registration stays in sync.
A curated hero set is loaded into Audacity for you to see/hear/tweak.

Run:  python tools/stage6_sounds.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import soundfile as sf
import sfx as S

RES = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
SND = os.path.join(RES, "assets", "endreborn", "sounds")
JAVA = os.path.join(os.path.dirname(__file__), "..", "src", "main", "java",
                    "com", "caranci", "endreborn", "registry", "ModSounds.java")

CATALOG = []   # each: dict(event, field, category, files=[(relpath, ndarray)])
SOUNDTYPES = []  # each: (field, material) -> uses <MAT>_BREAK/STEP/PLACE/HIT/FALL


def add(event, field, category, files):
    CATALOG.append(dict(event=event, field=field, category=category, files=files))


def field_of(event):
    return event.replace("endreborn.", "").replace("entity.", "").replace("block.", "") \
                .replace("ambient.", "amb.").replace(".", "_").upper()


# ---------------- MOB SOUNDS ----------------
def mob(name, ambient, hurt, death, extra=None):
    base = f"mob/{name}"
    add(f"entity.endreborn.{name}.ambient", f"{name}_AMBIENT".upper(), "neutral",
        [(f"{base}/ambient{i+1}", a) for i, a in enumerate(ambient)])
    add(f"entity.endreborn.{name}.hurt", f"{name}_HURT".upper(), "neutral",
        [(f"{base}/hurt{i+1}", a) for i, a in enumerate(hurt)])
    add(f"entity.endreborn.{name}.death", f"{name}_DEATH".upper(), "neutral",
        [(f"{base}/death", death)])
    for evt, arrs in (extra or {}).items():
        add(f"entity.endreborn.{name}.{evt}", f"{name}_{evt}".upper(), "hostile",
            [(f"{base}/{evt}{i+1}" if len(arrs) > 1 else f"{base}/{evt}", a) for i, a in enumerate(arrs)])


def chord(freqs, dur, ramp=None):
    x = S.mix(*[S.sine(f, dur) for f in freqs]) / len(freqs)
    if ramp is not None:
        x = x * np.linspace(ramp[0], ramp[1], len(x))
    return x


def build_mobs():
    m = S.master
    mx = S.mix
    # passive
    mob("void_moth",
        [m(mx(S.tremolo(S.lowpass(S.white(0.45, s), 2600), 22, 0.6) * 0.5,
              0.35 * S.voice(1250, 0.45, "warble", s, (1800, 3000), 0.3))) for s in (11, 12)],
        [m(S.voice(1600, 0.22, "down", s, (2000, 3400), 0.2)) for s in (13, 14)],
        m(mx(S.voice(1300, 0.6, "down", 15, (1600, 3000), 0.35), 0.3 * S.bell(1800, 0.6, decay=0.3, seed=16))))
    mob("chorus_sprite",
        [m(mx(S.bell(1700 + 200 * (s % 2), 0.3, decay=0.16, seed=s), 0.2 * S.glide(1200, 2200, 0.15))) for s in (21, 22)],
        [m(S.perc(S.glide(1400, 2400, 0.16, kind="square"), 0.002, 0.08)) for s in (23, 24)],
        m(mx(S.bell(2000, 0.5, decay=0.28, seed=25), 0.5 * S.voice(1600, 0.5, "down", 26, (2200, 3600), 0.3))))
    mob("crystal_strider",
        [m(mx(S.voice(230, 0.55, "warble", s, (430, 950), 0.3), 0.2 * S.bell(900, 0.4, decay=0.2, seed=s))) for s in (31, 32)],
        [m(S.voice(260, 0.28, "down", s, (500, 1100), 0.2)) for s in (33, 34)],
        m(S.voice(240, 0.7, "down", 35, (450, 1000), 0.3)))
    # hostile
    mob("void_wraith",
        [m(S.reverb(mx(S.lowpass(S.white(0.7, s), 1800)[::-1] * np.linspace(0, 1, int(S.SR * 0.7)),
           0.4 * S.voice(400, 0.7, "warble", s, (600, 1900), 0.4)), decay=0.6, mix=0.45)) for s in (41, 42)],
        [m(S.voice(720, 0.32, "down", s, (900, 2300), 0.4)) for s in (43, 44)],
        m(S.voice(600, 1.0, "down", 45, (700, 2000), 0.5)))
    mob("obsidian_golem",
        [m(mx(S.thud(70, 0.6, s, noise=0.5), 0.4 * S.lowpass(S.brown(0.6, s), 400))) for s in (51, 52)],
        [m(mx(S.thud(90, 0.35, s, noise=0.6), 0.5 * S.voice(150, 0.35, "down", s, (250, 700), 0.2))) for s in (53, 54)],
        m(S.reverb(mx(S.thud(60, 1.1, 55, noise=0.7), 0.5 * S.lowpass(S.white(1.1, 56), 900)), decay=0.7, mix=0.4)))
    mob("abyss_stalker",
        [m(S.formant(S.softclip(mx(S.lowpass(S.brown(0.5, s), 700), 0.3 * S.glide(120, 90, 0.5, kind="saw")), 2), (300, 800)) * 0.8) for s in (61, 62)],
        [m(mx(S.voice(320, 0.28, "down", s, (500, 1400), 0.25), 0.3 * S.softclip(S.white(0.1, s)))) for s in (63, 64)],
        m(S.voice(280, 0.7, "down", 65, (400, 1200), 0.3)))
    mob("crystal_sentinel",
        [m(mx(0.6 * S.sine(440, 0.6) * np.linspace(1, 0.4, int(S.SR * 0.6)), 0.5 * S.bell(880, 0.6, decay=0.4, seed=s))) for s in (71, 72)],
        [m(mx(S.dig("crystal", 0.25, s), 0.6 * S.bell(1600, 0.25, decay=0.1, seed=s))) for s in (73, 74)],
        m(S.reverb(mx(*[S.bell(600 * k, 0.7, decay=0.4, seed=80 + k) * (0.6 ** k) for k in range(1, 4)]), decay=0.5, mix=0.4)),
        extra={"zap": [S.master(S.zap(0.35, s)) for s in (75, 76)]})
    # bosses
    mob("chorus_guardian",
        [m(S.reverb(chord((196, 233, 294), 1.2, ramp=(0.3, 1.0)), decay=0.7, mix=0.4)) for s in (81, 82)],
        [m(mx(S.dig("crystal", 0.3, s), 0.7 * S.bell(420, 0.3, decay=0.2, seed=s), 0.4 * S.thud(120, 0.3, s))) for s in (83, 84)],
        m(S.reverb(mx(*[S.bell(300 * k, 1.2, decay=0.6, seed=90 + k) * 0.5 ** k for k in range(1, 4)],
          0.5 * S.thud(70, 1.2, 93)), decay=0.9, mix=0.5)),
        extra={"roar": [S.master(S.reverb(mx(chord((196, 262, 311), 1.4), 0.4 * S.roar(90, 1.4, 94)), decay=0.8, mix=0.45))]})
    mob("voidbringer",
        [m(S.roar(60, 1.6, s)) for s in (101, 102)],
        [m(mx(S.softclip(S.roar(80, 0.5, s), 2.5), 0.4 * S.voice(160, 0.5, "down", s, (300, 900), 0.3))) for s in (103, 104)],
        m(S.reverb(mx(S.roar(50, 2.4, 105), 0.6 * S.thud(45, 2.4, 106)), decay=1.0, mix=0.5)),
        extra={"roar": [S.master(S.roar(65, 2.0, s)) for s in (107, 108)]})


# ---------------- BLOCK SOUNDS ----------------
def build_blocks():
    m = S.master
    mats = {  # material -> (dig color, break freq body)
        "void_stone": "stone", "crystal": "crystal", "obsidian": "obsidian", "chorus_wood": "wood",
    }
    for mat, color in mats.items():
        base = f"block/{mat}"
        add(f"block.endreborn.{mat}.break", f"{mat}_BREAK".upper(), "block",
            [(f"{base}/break", m(S.dig(color, 0.28, 1)))])
        add(f"block.endreborn.{mat}.step", f"{mat}_STEP".upper(), "block",
            [(f"{base}/step{i+1}", m(S.dig(color, 0.13, s) * 0.5)) for i, s in enumerate((2, 3))])
        add(f"block.endreborn.{mat}.place", f"{mat}_PLACE".upper(), "block",
            [(f"{base}/place", m(S.dig(color, 0.22, 4) * 0.8))])
        add(f"block.endreborn.{mat}.hit", f"{mat}_HIT".upper(), "block",
            [(f"{base}/hit", m(S.dig(color, 0.10, 5) * 0.5))])
        add(f"block.endreborn.{mat}.fall", f"{mat}_FALL".upper(), "block",
            [(f"{base}/fall", m(S.thud(120 if color != "wood" else 160, 0.2, 6, noise=0.3)))])
        SOUNDTYPES.append((f"{mat}_SOUNDS".upper(), mat.upper()))


# ---------------- AMBIENT BIOME LOOPS ----------------
def ambient_loop(kind, seed):
    dur = 3.0
    if kind == "void_gardens":
        x = 0.4 * S.lowpass(S.pink(dur, seed), 1400) + 0.25 * S.tremolo(S.sine(220, dur), 0.5, 0.5) + 0.15 * S.bell(1600, dur, decay=1.5, seed=seed)
    elif kind == "shattered_barrens":
        x = 0.6 * S.bandpass(S.brown(dur, seed), 200, 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * S.t(dur)))
    elif kind == "obsidian_wastes":
        x = 0.5 * S.lowpass(S.brown(dur, seed), 500) + 0.3 * S.sine(70, dur) + 0.15 * S.sine(104, dur)
    elif kind == "crystal_highlands":
        x = 0.4 * S.lowpass(S.pink(dur, seed), 2000) + 0.2 * S.bell(1200, dur, decay=1.8, seed=seed) + 0.15 * S.sine(330, dur)
    elif kind == "endless_abyss":
        x = 0.6 * S.sine(45, dur) + 0.3 * S.lowpass(S.brown(dur, seed), 300) + 0.1 * S.sine(58.5, dur)
    else:  # chorus_jungle
        x = 0.4 * S.lowpass(S.pink(dur, seed), 1800) + 0.3 * S.tremolo(S.voice(180, dur, "warble", seed, (400, 1100), 0.3), 0.7, 0.4)
    return S.normalize(S.loopable(S.reverb(x, decay=0.9, mix=0.4), xfade=0.25), 0.7).astype(np.float32)


def build_ambient():
    for b in ("shattered_barrens", "void_gardens", "obsidian_wastes",
              "crystal_highlands", "endless_abyss", "chorus_jungle"):
        add(f"ambient.endreborn.{b}.loop", f"AMBIENT_{b}".upper(), "ambient",
            [(f"ambient/{b}", ambient_loop(b, hash(b) % 1000))])


# ---------------- export + registration ----------------
def export_all():
    n = 0
    for e in CATALOG:
        for rel, arr in e["files"]:
            p = os.path.join(SND, rel + ".ogg")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            sf.write(p, np.asarray(arr, dtype="float32"), S.SR, format="OGG", subtype="VORBIS")
            n += 1
    return n


def write_sounds_json():
    obj = {}
    for e in CATALOG:
        obj[e["event"]] = {"category": e["category"],
                           "sounds": [f"endreborn:{rel}" for rel, _ in e["files"]]}
    p = os.path.join(RES, "assets", "endreborn", "sounds.json")
    json.dump(obj, open(p, "w"), indent=2)


def write_mod_sounds_java():
    lines = [
        "package com.caranci.endreborn.registry;", "",
        "import com.caranci.endreborn.EndReborn;",
        "import net.minecraft.core.Registry;",
        "import net.minecraft.core.registries.BuiltInRegistries;",
        "import net.minecraft.resources.Identifier;",
        "import net.minecraft.sounds.SoundEvent;",
        "import net.minecraft.world.level.block.SoundType;", "",
        "/** Sound events + custom block SoundTypes (generated by tools/stage6_sounds.py). */",
        "public final class ModSounds {",
        "    private ModSounds() {}", "",
        "    private static SoundEvent event(String name) {",
        "        Identifier id = EndReborn.id(name);",
        "        return Registry.register(BuiltInRegistries.SOUND_EVENT, id, SoundEvent.createVariableRangeEvent(id));",
        "    }", "",
    ]
    for e in CATALOG:
        lines.append(f'    public static final SoundEvent {e["field"]} = event("{e["event"]}");')
    lines.append("")
    for field, mat in SOUNDTYPES:
        b = mat
        lines.append(f"    public static final SoundType {field} = new SoundType(1.0F, 1.0F, "
                     f"{b}_BREAK, {b}_STEP, {b}_PLACE, {b}_HIT, {b}_FALL);")
    lines += ["",
              "    public static void register() {",
              '        EndReborn.LOGGER.info("[EndReborn] Registered {} sound events.", '
              + str(sum(1 for _ in CATALOG)) + ");",
              "    }", "}", ""]
    open(JAVA, "w").write("\n".join(lines))


def audacity_review(hero):
    """Load a curated set into Audacity so the user can see/hear it."""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from aud import Audacity
        a = Audacity()
        a.do("SelectAll:", 10)
        a.do("RemoveTracks:", 10)
        for rel in hero:
            p = os.path.abspath(os.path.join(SND, rel + ".ogg"))
            a.do(f'Import2: Filename="{p}"', 25)
        print(f"loaded {len(hero)} hero sounds into Audacity for review")
    except Exception as ex:
        print("Audacity review load skipped:", ex)


def main():
    build_mobs()
    build_blocks()
    build_ambient()
    n = export_all()
    write_sounds_json()
    write_mod_sounds_java()
    print(f"exported {n} .ogg files across {len(CATALOG)} sound events; wrote sounds.json + ModSounds.java")
    audacity_review([
        "mob/voidbringer/roar1", "mob/voidbringer/ambient1", "mob/obsidian_golem/ambient1",
        "mob/crystal_sentinel/zap1", "mob/void_wraith/ambient1", "mob/void_moth/ambient1",
        "mob/chorus_guardian/roar1", "block/crystal/break", "block/obsidian/break",
        "ambient/endless_abyss",
    ])


if __name__ == "__main__":
    main()
