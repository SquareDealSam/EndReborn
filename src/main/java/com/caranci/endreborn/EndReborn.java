package com.caranci.endreborn;

import com.caranci.endreborn.registry.ModBlocks;
import com.caranci.endreborn.registry.ModEntities;
import com.caranci.endreborn.registry.ModItemGroups;
import com.caranci.endreborn.registry.ModItems;
import com.caranci.endreborn.registry.ModSounds;
import com.caranci.endreborn.registry.ModWorldgen;
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

        // Wired in over later stages:
        //   ModSounds.register();
        //   ModWorldgen.register();
        //   ModStructures.register();
        //   EndRebornConfig.load();
    }
}
