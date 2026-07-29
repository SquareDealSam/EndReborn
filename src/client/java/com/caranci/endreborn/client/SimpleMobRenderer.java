package com.caranci.endreborn.client;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.Mob;

/** One renderer for all simple EndReborn mobs: swap in a model + texture. */
public class SimpleMobRenderer<T extends Mob>
        extends MobRenderer<T, LivingEntityRenderState, EntityModel<LivingEntityRenderState>> {
    private final Identifier texture;

    public SimpleMobRenderer(EntityRendererProvider.Context ctx,
                             EntityModel<LivingEntityRenderState> model, float shadow, Identifier texture) {
        super(ctx, model, shadow);
        this.texture = texture;
    }

    @Override
    public LivingEntityRenderState createRenderState() {
        return new LivingEntityRenderState();
    }

    @Override
    public Identifier getTextureLocation(LivingEntityRenderState state) {
        return this.texture;
    }
}
