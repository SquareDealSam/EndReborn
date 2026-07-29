package com.caranci.endreborn.registry;

import com.caranci.endreborn.EndReborn;
import net.fabricmc.fabric.api.biome.v1.TheEndBiomes;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;

/**
 * Slots the six EndReborn biomes into the End's outer islands via Fabric's
 * TheEndBiomes API. The central island and dragon fight are left untouched.
 */
public final class ModWorldgen {
    private ModWorldgen() {}

    public static final ResourceKey<Biome> SHATTERED_BARRENS = key("shattered_barrens");
    public static final ResourceKey<Biome> VOID_GARDENS = key("void_gardens");
    public static final ResourceKey<Biome> OBSIDIAN_WASTES = key("obsidian_wastes");
    public static final ResourceKey<Biome> CRYSTAL_HIGHLANDS = key("crystal_highlands");
    public static final ResourceKey<Biome> ENDLESS_ABYSS = key("endless_abyss");
    public static final ResourceKey<Biome> CHORUS_JUNGLE = key("chorus_jungle");

    private static ResourceKey<Biome> key(String name) {
        return ResourceKey.create(Registries.BIOME, EndReborn.id(name));
    }

    public static void register() {
        // Large outer-island biomes.
        TheEndBiomes.addHighlandsBiome(CRYSTAL_HIGHLANDS, 6.0);
        TheEndBiomes.addHighlandsBiome(CHORUS_JUNGLE, 6.0);
        // Transitional rings around the highlands.
        TheEndBiomes.addMidlandsBiome(CRYSTAL_HIGHLANDS, VOID_GARDENS, 6.0);
        TheEndBiomes.addMidlandsBiome(CHORUS_JUNGLE, OBSIDIAN_WASTES, 6.0);
        // Scattered small islands + the deep, dangerous barrens edge.
        TheEndBiomes.addSmallIslandsBiome(SHATTERED_BARRENS, 5.0);
        TheEndBiomes.addBarrensBiome(CRYSTAL_HIGHLANDS, ENDLESS_ABYSS, 4.0);

        EndReborn.LOGGER.info("[EndReborn] Registered 6 End biomes.");
    }
}
