package com.voidweaver.voidweaver.entity;

import com.voidweaver.voidweaver.registry.ModItems;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Crystal Strider: wanders the Crystal Highlands; harvestable for crystal shards. */
public class CrystalStrider extends PathfinderMob {
    private int harvestCooldown;

    public CrystalStrider(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 14.0)
                .add(Attributes.MOVEMENT_SPEED, 0.2)
                .add(Attributes.FOLLOW_RANGE, 12.0);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new PanicGoal(this, 1.3));
        this.goalSelector.addGoal(2, new WaterAvoidingRandomStrollGoal(this, 1.0));
        this.goalSelector.addGoal(3, new LookAtPlayerGoal(this, Player.class, 6.0F));
        this.goalSelector.addGoal(4, new RandomLookAroundGoal(this));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (this.harvestCooldown > 0) {
            this.harvestCooldown--;
        }
    }

    @Override
    protected InteractionResult mobInteract(Player player, InteractionHand hand) {
        if (this.harvestCooldown <= 0) {
            if (!this.level().isClientSide()) {
                ItemEntity drop = new ItemEntity(this.level(), this.getX(), this.getY() + 0.6, this.getZ(),
                        new ItemStack(ModItems.CRYSTAL_SHARD, 1 + this.random.nextInt(2)));
                this.level().addFreshEntity(drop);
                this.level().playSound(null, this.blockPosition(), SoundEvents.AMETHYST_BLOCK_BREAK,
                        SoundSource.NEUTRAL, 1.0F, 1.2F);
            }
            this.harvestCooldown = 6000;
            return InteractionResult.SUCCESS;
        }
        return super.mobInteract(player, hand);
    }

    @Override
    protected net.minecraft.sounds.SoundEvent getAmbientSound() { return com.voidweaver.voidweaver.registry.ModSounds.CRYSTAL_STRIDER_AMBIENT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source) { return com.voidweaver.voidweaver.registry.ModSounds.CRYSTAL_STRIDER_HURT; }

    @Override
    protected net.minecraft.sounds.SoundEvent getDeathSound() { return com.voidweaver.voidweaver.registry.ModSounds.CRYSTAL_STRIDER_DEATH; }
}
