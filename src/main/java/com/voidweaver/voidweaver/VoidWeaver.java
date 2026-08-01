package com.voidweaver.voidweaver;

import com.voidweaver.voidweaver.registry.ModBlocks;
import com.voidweaver.voidweaver.registry.ModEntities;
import com.voidweaver.voidweaver.registry.ModItemGroups;
import com.voidweaver.voidweaver.registry.ModItems;
import com.voidweaver.voidweaver.registry.ModSounds;
import com.voidweaver.voidweaver.registry.ModWorldgen;
import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VoidWeaver implements ModInitializer {
    public static final String MOD_ID = "voidweaver";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    /** Helper for building namespaced identifiers under this mod. */
    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MOD_ID, path);
    }

    @Override
    public void onInitialize() {
        LOGGER.info("[VoidWeaver] Initializing — the Void-Weaver awakens.");

        ModSounds.register();
        ModBlocks.register();
        ModItems.register();
        ModItemGroups.register();
        ModEntities.register();
        ModWorldgen.register();

        // Structures are fully data-driven (minecraft:jigsaw + structure_set +
        // template_pool under data/voidweaver/worldgen), so they need no Java
        // registration here. Config loading is the remaining future stage.
    }
}
