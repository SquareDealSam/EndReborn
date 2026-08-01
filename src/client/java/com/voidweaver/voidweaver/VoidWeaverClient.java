package com.voidweaver.voidweaver;

import com.voidweaver.voidweaver.client.ModEntityRenderers;
import net.fabricmc.api.ClientModInitializer;

public class VoidWeaverClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        VoidWeaver.LOGGER.info("[VoidWeaver] Client init.");
        ModEntityRenderers.register();

        // Client-side registration wired in over later stages:
        //   Entity renderers, model layers, particle factories,
        //   block render layers, screen handlers.
    }
}
