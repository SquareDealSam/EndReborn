package com.caranci.endreborn.client;

import com.caranci.endreborn.EndReborn;
import com.caranci.endreborn.entity.VoidMoth;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.resources.Identifier;

public class VoidMothRenderer extends MobRenderer<VoidMoth, LivingEntityRenderState, VoidMothModel> {
    private static final Identifier TEXTURE = EndReborn.id("textures/entity/void_moth.png");

    public VoidMothRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new VoidMothModel(ctx.bakeLayer(ModEntityRenderers.VOID_MOTH_LAYER)), 0.2F);
    }

    @Override
    public LivingEntityRenderState createRenderState() {
        return new LivingEntityRenderState();
    }

    @Override
    public Identifier getTextureLocation(LivingEntityRenderState state) {
        return TEXTURE;
    }
}
