package com.endreborn.endreborn.client;

import com.endreborn.endreborn.EndReborn;
import com.endreborn.endreborn.registry.ModEntities;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.resources.Identifier;

/** Client-side entity model layers + renderers. */
public final class ModEntityRenderers {
    private ModEntityRenderers() {}

    public static final ModelLayerLocation VOID_MOTH_LAYER = layer("void_moth");
    public static final ModelLayerLocation CHORUS_SPRITE_LAYER = layer("chorus_sprite");
    public static final ModelLayerLocation CRYSTAL_STRIDER_LAYER = layer("crystal_strider");
    public static final ModelLayerLocation VOID_WRAITH_LAYER = layer("void_wraith");
    public static final ModelLayerLocation OBSIDIAN_GOLEM_LAYER = layer("obsidian_golem");
    public static final ModelLayerLocation ABYSS_STALKER_LAYER = layer("abyss_stalker");
    public static final ModelLayerLocation CRYSTAL_SENTINEL_LAYER = layer("crystal_sentinel");
    public static final ModelLayerLocation CHORUS_GUARDIAN_LAYER = layer("chorus_guardian");
    public static final ModelLayerLocation VOIDBRINGER_LAYER = layer("voidbringer");

    private static ModelLayerLocation layer(String name) {
        return new ModelLayerLocation(EndReborn.id(name), "main");
    }

    private static Identifier tex(String name) {
        return EndReborn.id("textures/entity/" + name + ".png");
    }

    public static void register() {
        ModelLayerRegistry.registerModelLayer(VOID_MOTH_LAYER, VoidMothModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(CHORUS_SPRITE_LAYER, ChorusSpriteModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(CRYSTAL_STRIDER_LAYER, CrystalStriderModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(VOID_WRAITH_LAYER, VoidWraithModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(OBSIDIAN_GOLEM_LAYER, ObsidianGolemModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(ABYSS_STALKER_LAYER, AbyssStalkerModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(CRYSTAL_SENTINEL_LAYER, CrystalSentinelModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(CHORUS_GUARDIAN_LAYER, ChorusGuardianModel::createBodyLayer);
        ModelLayerRegistry.registerModelLayer(VOIDBRINGER_LAYER, VoidbringerModel::createBodyLayer);

        EntityRendererRegistry.register(ModEntities.VOID_MOTH, ctx ->
                new VoidMothRenderer(ctx));
        EntityRendererRegistry.register(ModEntities.CHORUS_SPRITE, ctx ->
                new SimpleMobRenderer<>(ctx, new ChorusSpriteModel(ctx.bakeLayer(CHORUS_SPRITE_LAYER)), 0.2F, tex("chorus_sprite")));
        EntityRendererRegistry.register(ModEntities.CRYSTAL_STRIDER, ctx ->
                new SimpleMobRenderer<>(ctx, new CrystalStriderModel(ctx.bakeLayer(CRYSTAL_STRIDER_LAYER)), 0.5F, tex("crystal_strider")));
        EntityRendererRegistry.register(ModEntities.VOID_WRAITH, ctx ->
                new SimpleMobRenderer<>(ctx, new VoidWraithModel(ctx.bakeLayer(VOID_WRAITH_LAYER)), 0.5F, tex("void_wraith")));
        EntityRendererRegistry.register(ModEntities.OBSIDIAN_GOLEM, ctx ->
                new SimpleMobRenderer<>(ctx, new ObsidianGolemModel(ctx.bakeLayer(OBSIDIAN_GOLEM_LAYER)), 0.9F, tex("obsidian_golem")));
        EntityRendererRegistry.register(ModEntities.ABYSS_STALKER, ctx ->
                new SimpleMobRenderer<>(ctx, new AbyssStalkerModel(ctx.bakeLayer(ABYSS_STALKER_LAYER)), 0.5F, tex("abyss_stalker")));
        EntityRendererRegistry.register(ModEntities.CRYSTAL_SENTINEL, ctx ->
                new SimpleMobRenderer<>(ctx, new CrystalSentinelModel(ctx.bakeLayer(CRYSTAL_SENTINEL_LAYER)), 0.4F, tex("crystal_sentinel")));
        EntityRendererRegistry.register(ModEntities.CHORUS_GUARDIAN, ctx ->
                new BossRenderer<>(ctx, new ChorusGuardianModel(ctx.bakeLayer(CHORUS_GUARDIAN_LAYER)), 0.8F, tex("chorus_guardian")));
        EntityRendererRegistry.register(ModEntities.VOIDBRINGER, ctx ->
                new BossRenderer<>(ctx, new VoidbringerModel(ctx.bakeLayer(VOIDBRINGER_LAYER)), 1.0F, tex("voidbringer")));
    }
}
