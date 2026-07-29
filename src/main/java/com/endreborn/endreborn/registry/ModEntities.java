package com.caranci.endreborn.registry;

import com.caranci.endreborn.EndReborn;
import com.caranci.endreborn.entity.AbyssStalker;
import com.caranci.endreborn.entity.ChorusGuardian;
import com.caranci.endreborn.entity.ChorusSprite;
import com.caranci.endreborn.entity.CrystalSentinel;
import com.caranci.endreborn.entity.CrystalStrider;
import com.caranci.endreborn.entity.ObsidianGolem;
import com.caranci.endreborn.entity.VoidMoth;
import com.caranci.endreborn.entity.Voidbringer;
import com.caranci.endreborn.entity.VoidWraith;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/** Entity-type registration for EndReborn mobs. */
public final class ModEntities {
    private ModEntities() {}

    // Passive
    public static final EntityType<VoidMoth> VOID_MOTH = register("void_moth",
            EntityType.Builder.of(VoidMoth::new, MobCategory.AMBIENT).sized(0.6F, 0.5F).clientTrackingRange(8));
    public static final EntityType<ChorusSprite> CHORUS_SPRITE = register("chorus_sprite",
            EntityType.Builder.of(ChorusSprite::new, MobCategory.AMBIENT).sized(0.4F, 0.4F).clientTrackingRange(8));
    public static final EntityType<CrystalStrider> CRYSTAL_STRIDER = register("crystal_strider",
            EntityType.Builder.of(CrystalStrider::new, MobCategory.CREATURE).sized(0.9F, 1.4F).clientTrackingRange(10));

    // Hostile
    public static final EntityType<VoidWraith> VOID_WRAITH = register("void_wraith",
            EntityType.Builder.of(VoidWraith::new, MobCategory.MONSTER).sized(0.7F, 1.8F).clientTrackingRange(10));
    public static final EntityType<ObsidianGolem> OBSIDIAN_GOLEM = register("obsidian_golem",
            EntityType.Builder.of(ObsidianGolem::new, MobCategory.MONSTER).sized(1.4F, 2.8F).clientTrackingRange(10));
    public static final EntityType<AbyssStalker> ABYSS_STALKER = register("abyss_stalker",
            EntityType.Builder.of(AbyssStalker::new, MobCategory.MONSTER).sized(0.9F, 0.7F).clientTrackingRange(10));
    public static final EntityType<CrystalSentinel> CRYSTAL_SENTINEL = register("crystal_sentinel",
            EntityType.Builder.of(CrystalSentinel::new, MobCategory.MONSTER).sized(0.8F, 1.6F).clientTrackingRange(12));

    // Bosses
    public static final EntityType<ChorusGuardian> CHORUS_GUARDIAN = register("chorus_guardian",
            EntityType.Builder.of(ChorusGuardian::new, MobCategory.MONSTER).sized(1.4F, 3.0F).fireImmune().clientTrackingRange(16));
    public static final EntityType<Voidbringer> VOIDBRINGER = register("voidbringer",
            EntityType.Builder.of(Voidbringer::new, MobCategory.MONSTER).sized(1.6F, 3.6F).fireImmune().clientTrackingRange(20));

    private static <T extends Entity> EntityType<T> register(String name, EntityType.Builder<T> builder) {
        ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, EndReborn.id(name));
        return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
    }

    public static void register() {
        FabricDefaultAttributeRegistry.register(VOID_MOTH, VoidMoth.createAttributes());
        FabricDefaultAttributeRegistry.register(CHORUS_SPRITE, ChorusSprite.createAttributes());
        FabricDefaultAttributeRegistry.register(CRYSTAL_STRIDER, CrystalStrider.createAttributes());
        FabricDefaultAttributeRegistry.register(VOID_WRAITH, VoidWraith.createAttributes());
        FabricDefaultAttributeRegistry.register(OBSIDIAN_GOLEM, ObsidianGolem.createAttributes());
        FabricDefaultAttributeRegistry.register(ABYSS_STALKER, AbyssStalker.createAttributes());
        FabricDefaultAttributeRegistry.register(CRYSTAL_SENTINEL, CrystalSentinel.createAttributes());
        FabricDefaultAttributeRegistry.register(CHORUS_GUARDIAN, ChorusGuardian.createAttributes());
        FabricDefaultAttributeRegistry.register(VOIDBRINGER, Voidbringer.createAttributes());
        EndReborn.LOGGER.info("[EndReborn] Registered 7 mobs + 2 bosses.");
    }
}
