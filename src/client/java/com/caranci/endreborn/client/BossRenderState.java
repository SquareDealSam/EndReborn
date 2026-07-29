package com.caranci.endreborn.client;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;

/** Carries boss attack/phase state from the entity to the model for animation. */
public class BossRenderState extends LivingEntityRenderState {
    public int attackState;
    public int phase = 1;
}
