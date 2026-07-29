package com.endreborn.endreborn;

import com.endreborn.endreborn.client.ModEntityRenderers;
import net.fabricmc.api.ClientModInitializer;

public class EndRebornClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        EndReborn.LOGGER.info("[EndReborn] Client init.");
        ModEntityRenderers.register();

        // Client-side registration wired in over later stages:
        //   Entity renderers, model layers, particle factories,
        //   block render layers, screen handlers.
    }
}
