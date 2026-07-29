package com.caranci.endreborn.entity;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ShulkerBullet;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.UUID;

/** Shared boss behaviour: boss bar, synced attack/phase state (for animation), and attack helpers. */
public abstract class AbstractBoss extends Monster {
    protected static final EntityDataAccessor<Integer> ATTACK_STATE =
            SynchedEntityData.defineId(AbstractBoss.class, EntityDataSerializers.INT);
    protected static final EntityDataAccessor<Integer> PHASE =
            SynchedEntityData.defineId(AbstractBoss.class, EntityDataSerializers.INT);

    protected final ServerBossEvent bossEvent;
    protected int attackTicks;
    protected int globalCooldown = 40;

    protected AbstractBoss(EntityType<? extends Monster> type, Level level, BossEvent.BossBarColor color) {
        super(type, level);
        this.bossEvent = new ServerBossEvent(UUID.randomUUID(), this.getType().getDescription(),
                color, BossEvent.BossBarOverlay.PROGRESS);
        this.setPersistenceRequired();
        this.xpReward = 50;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(ATTACK_STATE, 0);
        builder.define(PHASE, 1);
    }

    public int getAttackState() {
        return this.entityData.get(ATTACK_STATE);
    }

    public int getPhase() {
        return this.entityData.get(PHASE);
    }

    protected void setPhase(int phase) {
        this.entityData.set(PHASE, phase);
    }

    protected void triggerAttack(int state, int durationTicks) {
        this.entityData.set(ATTACK_STATE, state);
        this.attackTicks = durationTicks;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.0, true));
        this.goalSelector.addGoal(2, new WaterAvoidingRandomStrollGoal(this, 0.7));
        this.goalSelector.addGoal(3, new LookAtPlayerGoal(this, Player.class, 20.0F));
        this.targetSelector.addGoal(0, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (this.level() instanceof ServerLevel sl) {
            this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
            if (this.attackTicks > 0 && --this.attackTicks == 0) {
                this.entityData.set(ATTACK_STATE, 0);
            }
            if (this.globalCooldown > 0) {
                this.globalCooldown--;
            }
            LivingEntity target = this.getTarget();
            if (this.globalCooldown <= 0 && target != null && target.isAlive() && this.hasLineOfSight(target)) {
                this.performAttack(sl, target);
            }
        }
    }

    /** Subclasses choose an attack, trigger its animation, and set {@link #globalCooldown}. */
    protected abstract void performAttack(ServerLevel level, LivingEntity target);

    // ---- shared attack effects ----
    protected void shootBolt(LivingEntity target) {
        ShulkerBullet bolt = new ShulkerBullet(this.level(), this, target, this.getDirection().getAxis());
        this.level().addFreshEntity(bolt);
    }

    protected void nova(ServerLevel level, float radius, float damage, double knockback, ParticleOptions particle) {
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class,
                this.getBoundingBox().inflate(radius), le -> le != this && !(le instanceof AbstractBoss))) {
            e.hurtServer(level, this.damageSources().mobAttack(this), damage);
            Vec3 dir = e.position().subtract(this.position());
            if (dir.lengthSqr() > 0.01) {
                dir = dir.normalize().scale(knockback);
                e.push(dir.x, 0.45, dir.z);
            }
        }
        level.sendParticles(particle, this.getX(), this.getY() + 1.0, this.getZ(),
                100, radius / 2.0, 1.0, radius / 2.0, 0.15);
    }

    protected void summon(EntityType<? extends Mob> type, ServerLevel level) {
        Mob mob = type.create(level, EntitySpawnReason.MOB_SUMMONED);
        if (mob != null) {
            double a = this.random.nextDouble() * Math.PI * 2.0;
            mob.setPos(this.getX() + Math.cos(a) * 3.0, this.getY(), this.getZ() + Math.sin(a) * 3.0);
            mob.setYRot(this.random.nextFloat() * 360.0F);
            level.addFreshEntity(mob);
        }
    }

    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        this.bossEvent.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        this.bossEvent.removePlayer(player);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
