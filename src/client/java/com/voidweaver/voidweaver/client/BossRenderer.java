package com.voidweaver.voidweaver.client;

import com.voidweaver.voidweaver.entity.AbstractBoss;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.Identifier;

/** Renderer for VoidWeaver bosses; extracts attack/phase state for animation. */
public class BossRenderer<T extends AbstractBoss> extends MobRenderer<T, BossRenderState, EntityModel<BossRenderState>> {
    private final Identifier texture;

    public BossRenderer(EntityRendererProvider.Context ctx, EntityModel<BossRenderState> model,
                        float shadow, Identifier texture) {
        super(ctx, model, shadow);
        this.texture = texture;
    }

    @Override
    public BossRenderState createRenderState() {
        return new BossRenderState();
    }

    @Override
    public void extractRenderState(T entity, BossRenderState state, float partialTick) {
        super.extractRenderState(entity, state, partialTick);
        state.attackState = entity.getAttackState();
        state.phase = entity.getPhase();
    }

    @Override
    public Identifier getTextureLocation(BossRenderState state) {
        return this.texture;
    }
}
