package com.voidweaver.voidweaver.registry;

import com.voidweaver.voidweaver.VoidWeaver;
import com.voidweaver.voidweaver.entity.AbyssStalker;
import com.voidweaver.voidweaver.entity.ChorusGuardian;
import com.voidweaver.voidweaver.entity.ChorusSprite;
import com.voidweaver.voidweaver.entity.CrystalSentinel;
import com.voidweaver.voidweaver.entity.CrystalStrider;
import com.voidweaver.voidweaver.entity.ObsidianGolem;
import com.voidweaver.voidweaver.entity.VoidMoth;
import com.voidweaver.voidweaver.entity.Voidbringer;
import com.voidweaver.voidweaver.entity.VoidWraith;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;

/** Entity-type registration for VoidWeaver mobs. */
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
        ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, VoidWeaver.id(name));
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

        registerSpawnPlacements();

        VoidWeaver.LOGGER.info("[VoidWeaver] Registered 7 mobs + 2 bosses.");
    }

    /**
     * Registers the spawn placement rules that gate where and when each mob may
     * naturally spawn. The two bosses are omitted on purpose — they are placed by
     * structures / summoned, never by the natural mob-spawning loop.
     */
    private static void registerSpawnPlacements() {
        // Ambient flyers: drift through the air, so no ground restriction and any light.
        SpawnPlacements.register(VOID_MOTH, SpawnPlacementTypes.NO_RESTRICTIONS,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules);
        SpawnPlacements.register(CHORUS_SPRITE, SpawnPlacementTypes.NO_RESTRICTIONS,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules);

        // Ground creature: needs a solid block underfoot.
        SpawnPlacements.register(CRYSTAL_STRIDER, SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules);

        // Ground monsters: the End is hostile territory, so spawn regardless of light.
        SpawnPlacements.register(OBSIDIAN_GOLEM, SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkAnyLightMonsterSpawnRules);
        SpawnPlacements.register(ABYSS_STALKER, SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkAnyLightMonsterSpawnRules);
        SpawnPlacements.register(CRYSTAL_SENTINEL, SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkAnyLightMonsterSpawnRules);

        // Flying monster: haunts the open air of the Barrens and the Abyss.
        SpawnPlacements.register(VOID_WRAITH, SpawnPlacementTypes.NO_RESTRICTIONS,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkAnyLightMonsterSpawnRules);
    }
}
