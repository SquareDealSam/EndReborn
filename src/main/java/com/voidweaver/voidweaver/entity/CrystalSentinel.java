package com.voidweaver.voidweaver.entity;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RangedAttackGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.RangedAttackMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ShulkerBullet;
import net.minecraft.world.level.Level;

/** Crystal Sentinel: a ranged guardian of the Crystal Highlands that fires homing bolts. */
public class CrystalSentinel extends Monster implements RangedAttackMob {

    public CrystalSentinel(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 24.0)
                .add(Attributes.MOVEMENT_SPEED, 0.24)
                .add(Attributes.ARMOR, 4.0)
                .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new RangedAttackGoal(this, 1.0, 50, 18.0F));
        this.goalSelector.addGoal(2, new WaterAvoidingRandomStrollGoal(this, 0.8));
        this.goalSelector.addGoal(3, new LookAtPlayerGoal(this, Player.class, 12.0F));
        this.goalSelector.addGoal(4, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(0, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public void performRangedAttack(LivingEntity target, float velocity) {
        if (!this.level().isClientSide()) {
            ShulkerBullet bullet = new ShulkerBullet(this.level(), this, target, this.getDirection().getAxis());
            this.level().addFreshEntity(bullet);
            this.level().playSound(null, this.blockPosition(),
                    com.voidweaver.voidweaver.registry.ModSounds.CRYSTAL_SENTINEL_ZAP,
                    SoundSource.HOSTILE, 1.0F, 1.0F);
        }
    }

    @Override
    protected net.minecraft.sounds.SoundEvent getAmbientSound() { return com.voidweaver.voidweaver.registry.ModSounds.CRYSTAL_SENTINEL_AMBIENT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source) { return com.voidweaver.voidweaver.registry.ModSounds.CRYSTAL_SENTINEL_HURT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getDeathSound() { return com.voidweaver.voidweaver.registry.ModSounds.CRYSTAL_SENTINEL_DEATH; }
}
