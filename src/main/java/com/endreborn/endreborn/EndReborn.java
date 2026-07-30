package com.endreborn.endreborn;

import com.endreborn.endreborn.registry.ModBlocks;
import com.endreborn.endreborn.registry.ModEntities;
import com.endreborn.endreborn.registry.ModItemGroups;
import com.endreborn.endreborn.registry.ModItems;
import com.endreborn.endreborn.registry.ModSounds;
import com.endreborn.endreborn.registry.ModWorldgen;
import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EndReborn implements ModInitializer {
    public static final String MOD_ID = "endreborn";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    /** Helper for building namespaced identifiers under this mod. */
    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MOD_ID, path);
    }

    @Override
    public void onInitialize() {
        LOGGER.info("[EndReborn] Initializing — the End, reborn.");

        ModSounds.register();
        ModBlocks.register();
        ModItems.register();
        ModItemGroups.register();
        ModEntities.register();
        ModWorldgen.register();

        // Structures are fully data-driven (minecraft:jigsaw + structure_set +
        // template_pool under data/endreborn/worldgen), so they need no Java
        // registration here. Config loading is the remaining future stage.
    }
}
