# EndReborn

A **Fabric mod for Minecraft 26.2** that overhauls the **End dimension** beyond the dragon
fight — new biomes, mobs, bosses, materials, structures, and a full set of custom sound
effects, built as a distinct post-dragon progression track.

> ⚠️ **Early / work-in-progress (v0.1.0).** It builds and runs, but textures, biome variety,
> and the boss encounters are actively being overhauled. Expect rough edges — feedback welcome.

## Features

- **6 End biomes** (outer islands, main island + dragon left intact): Shattered Barrens,
  Void Gardens, Obsidian Wastes, Crystal Highlands, Endless Abyss, Chorus Jungle.
- **9 mobs** with custom models, animations, AI, and sounds — 3 passive (Void Moth, Chorus
  Sprite, Crystal Strider), 4 hostile (Void Wraith, Obsidian Golem, Abyss Stalker, Crystal
  Sentinel), and **2 multi-phase bosses** (Chorus Guardian, The Voidbringer) with boss bars.
- **Materials & gear**: Chorus Alloy (mid-tier) and Void Crystal (above netherite) — full
  tool + armor sets, ores, and storage blocks.
- **Full Chorus wood set** + three stone families (Void Stone, Crystal Stone, Obsidian) with
  stairs/slabs/walls/polished/chiseled/brick variants.
- **5 structures** with loot: Void Sanctum, Crystal Spire, Sunken Ruins, Abyss Temple, End Outpost.
- **80+ custom sound effects** (mob voices, block material sounds, per-biome ambience).

## Requirements

- Minecraft **26.2**, **Fabric Loader** 0.19.3+, **Fabric API** 0.155.2+26.2
- **JDK 25+** to build

## Build

```bash
./gradlew build
```

The mod jar lands in `build/libs/`. Drop it and Fabric API into your `.minecraft/mods/`.

## Dev run

```bash
./gradlew runClient
```

## Repo layout

- `src/main` / `src/client` — mod source (registration, entities, worldgen, renderers)
- `src/main/resources` — assets (models, textures, sounds) + data (worldgen, loot, tags)
- `tools/` — the Python asset pipeline (procedural textures, sound synthesis, structure NBT,
  and a live Blockbench sync bridge) used to generate much of the content

## License

MIT — see [LICENSE](LICENSE).
