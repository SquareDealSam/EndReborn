package com.caranci.endreborn.entity;

import com.caranci.endreborn.registry.ModEntities;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/**
 * Chorus Guardian — mid-boss guarding the Crystal Spire. Cycles between a homing-bolt
 * volley, summoning Crystal Sentinels, and a crystalline shockwave.
 */
public class ChorusGuardian extends AbstractBoss {

    public ChorusGuardian(EntityType<? extends Monster> type, Level level) {
        super(type, level, BossEvent.BossBarColor.PURPLE);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 150.0)
                .add(Attributes.ATTACK_DAMAGE, 8.0)
                .add(Attributes.MOVEMENT_SPEED, 0.25)
                .add(Attributes.ARMOR, 8.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 40.0);
    }

    @Override
    protected void performAttack(ServerLevel level, LivingEntity target) {
        switch (this.random.nextInt(3)) {
            case 0 -> {                       // homing-bolt volley
                this.triggerAttack(2, 20);
                for (int i = 0; i < 3; i++) {
                    this.shootBolt(target);
                }
                this.playSound(SoundEvents.SHULKER_SHOOT, 1.2F, 0.8F);
                this.globalCooldown = 60;
            }
            case 1 -> {                       // summon two Crystal Sentinels
                this.triggerAttack(3, 30);
                this.summon(ModEntities.CRYSTAL_SENTINEL, level);
                this.summon(ModEntities.CRYSTAL_SENTINEL, level);
                this.playSound(SoundEvents.AMETHYST_BLOCK_CHIME, 1.5F, 0.7F);
                this.globalCooldown = 160;
            }
            default -> {                      // crystalline shockwave
                this.triggerAttack(1, 20);
                this.nova(level, 5.0F, 7.0F, 1.4, ParticleTypes.END_ROD);
                this.playSound(SoundEvents.AMETHYST_BLOCK_BREAK, 1.6F, 0.6F);
                this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(),
                        SoundSource.HOSTILE, 1.0F, 1.3F);
                this.globalCooldown = 90;
            }
        }
    }

    @Override
    protected net.minecraft.sounds.SoundEvent getAmbientSound() { return com.caranci.endreborn.registry.ModSounds.CHORUS_GUARDIAN_AMBIENT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source) { return com.caranci.endreborn.registry.ModSounds.CHORUS_GUARDIAN_HURT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getDeathSound() { return com.caranci.endreborn.registry.ModSounds.CHORUS_GUARDIAN_DEATH; }
}
