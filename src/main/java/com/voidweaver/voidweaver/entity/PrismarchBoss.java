package com.voidweaver.voidweaver.entity;

import com.voidweaver.voidweaver.registry.ModEntities;
import com.voidweaver.voidweaver.registry.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/**
 * The Prismarch — a crystal-armoured colossus with four floating hands that orbit it.
 * A ranged, three-phase boss: hurls homing crystal bolts from its hands, unleashes
 * radiant crystal novas, and (when wounded) summons Crystal Sentinels.
 */
public class PrismarchBoss extends AbstractBoss {

    public PrismarchBoss(EntityType<? extends Monster> type, Level level) {
        super(type, level, BossEvent.BossBarColor.BLUE);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 260.0)
                .add(Attributes.MOVEMENT_SPEED, 0.24)
                .add(Attributes.ARMOR, 12.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.ATTACK_DAMAGE, 8.0)
                .add(Attributes.FOLLOW_RANGE, 48.0);
    }

    @Override
    protected void performAttack(ServerLevel level, LivingEntity target) {
        int phase = this.getHealth() > 175.0F ? 1 : (this.getHealth() > 85.0F ? 2 : 3);
        this.setPhase(phase);
        switch (this.random.nextInt(phase >= 2 ? 4 : 3)) {
            case 0, 1 -> {                              // crystal-bolt volley from the hands
                this.triggerAttack(2, 25);
                int bolts = 3 + phase;                  // 4..6
                for (int i = 0; i < bolts; i++) {
                    this.shootBolt(target);
                }
                this.playSound(SoundEvents.AMETHYST_BLOCK_CHIME, 1.4F, 0.9F);
                this.playSound(SoundEvents.SHULKER_SHOOT, 1.2F, 1.3F);
                this.globalCooldown = 55 - phase * 8;
            }
            case 2 -> {                                 // radiant crystal nova
                this.triggerAttack(1, 22);
                this.nova(level, 5.0F + phase, 8.0F, 1.5, ParticleTypes.END_ROD);
                this.playSound(SoundEvents.AMETHYST_BLOCK_BREAK, 1.6F, 0.6F);
                this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(),
                        SoundSource.HOSTILE, 1.0F, 1.4F);
                this.globalCooldown = 80;
            }
            default -> {                                // summon Crystal Sentinels (phase 2+)
                this.triggerAttack(3, 30);
                this.summon(ModEntities.CRYSTAL_SENTINEL, level);
                this.summon(ModEntities.CRYSTAL_SENTINEL, level);
                this.playSound(SoundEvents.AMETHYST_BLOCK_CHIME, 1.5F, 0.6F);
                this.globalCooldown = 140;
            }
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.CHORUS_GUARDIAN_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.CHORUS_GUARDIAN_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.CHORUS_GUARDIAN_DEATH;
    }
}
