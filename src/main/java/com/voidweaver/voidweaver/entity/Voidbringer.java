package com.voidweaver.voidweaver.entity;

import com.voidweaver.voidweaver.registry.ModEntities;
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
 * The Voidbringer — end-game, three-phase boss of the Endless Abyss.
 * P1: bolt volleys + void shockwaves. P2: blink-strikes, summons Void Wraiths.
 * P3: enraged — wide void novas, bolt storms, relentless summons.
 */
public class Voidbringer extends AbstractBoss {

    public Voidbringer(EntityType<? extends Monster> type, Level level) {
        super(type, level, BossEvent.BossBarColor.RED);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 300.0)
                .add(Attributes.ATTACK_DAMAGE, 12.0)
                .add(Attributes.MOVEMENT_SPEED, 0.28)
                .add(Attributes.ARMOR, 10.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 48.0);
    }

    @Override
    protected void performAttack(ServerLevel level, LivingEntity target) {
        int phase = this.getHealth() > 200.0F ? 1 : (this.getHealth() > 100.0F ? 2 : 3);
        this.setPhase(phase);

        switch (phase) {
            case 1 -> {
                if (this.random.nextBoolean()) {
                    this.triggerAttack(2, 20);
                    for (int i = 0; i < 3; i++) {
                        this.shootBolt(target);
                    }
                    this.playSound(SoundEvents.SHULKER_SHOOT, 1.2F, 0.6F);
                } else {
                    this.triggerAttack(1, 20);
                    this.nova(level, 4.0F, 8.0F, 1.2, ParticleTypes.REVERSE_PORTAL);
                }
                this.globalCooldown = 60;
            }
            case 2 -> {                       // blink-strike + summon
                double ox = (this.random.nextDouble() - 0.5) * 6.0;
                double oz = (this.random.nextDouble() - 0.5) * 6.0;
                this.teleportTo(target.getX() + ox, target.getY(), target.getZ() + oz);
                level.sendParticles(ParticleTypes.PORTAL, this.getX(), this.getY() + 1.0, this.getZ(),
                        60, 0.5, 1.0, 0.5, 0.2);
                this.triggerAttack(2, 20);
                this.shootBolt(target);
                this.shootBolt(target);
                this.summon(ModEntities.VOID_WRAITH, level);
                this.playSound(SoundEvents.ENDERMAN_TELEPORT, 1.0F, 0.7F);
                this.globalCooldown = 50;
            }
            default -> {                      // phase 3 — enraged
                this.triggerAttack(3, 30);
                this.nova(level, 6.0F, 10.0F, 1.7, ParticleTypes.REVERSE_PORTAL);
                for (int i = 0; i < 5; i++) {
                    this.shootBolt(target);
                }
                this.summon(ModEntities.VOID_WRAITH, level);
                this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(),
                        SoundSource.HOSTILE, 1.4F, 0.7F);
                this.globalCooldown = 45;
            }
        }
    }

    @Override
    protected net.minecraft.sounds.SoundEvent getAmbientSound() { return com.voidweaver.voidweaver.registry.ModSounds.VOIDBRINGER_AMBIENT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source) { return com.voidweaver.voidweaver.registry.ModSounds.VOIDBRINGER_HURT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getDeathSound() { return com.voidweaver.voidweaver.registry.ModSounds.VOIDBRINGER_DEATH; }
}
