package com.endreborn.endreborn.registry;

import com.endreborn.endreborn.EndReborn;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;

import java.util.EnumMap;
import java.util.Map;

/** Tool and armor materials for the two EndReborn tiers. */
public final class ModMaterials {
    private ModMaterials() {}

    // Repair-item tags (populated by data/endreborn/tags/item/*.json).
    public static final TagKey<Item> CHORUS_ALLOY_REPAIR =
            TagKey.create(Registries.ITEM, EndReborn.id("chorus_alloy_repair"));
    public static final TagKey<Item> VOID_CRYSTAL_REPAIR =
            TagKey.create(Registries.ITEM, EndReborn.id("void_crystal_repair"));

    // Tool tiers: Chorus Alloy ~ diamond+, Void Crystal above netherite.
    public static final ToolMaterial CHORUS_ALLOY = new ToolMaterial(
            BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1200, 7.0F, 3.0F, 18, CHORUS_ALLOY_REPAIR);
    public static final ToolMaterial VOID_CRYSTAL = new ToolMaterial(
            BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 2600, 10.0F, 5.0F, 20, VOID_CRYSTAL_REPAIR);

    // Equipment-asset keys -> assets/endreborn/equipment/<id>.json layer definitions.
    public static final ResourceKey<EquipmentAsset> CHORUS_ALLOY_ASSET =
            ResourceKey.create(EquipmentAssets.ROOT_ID, EndReborn.id("chorus_alloy"));
    public static final ResourceKey<EquipmentAsset> VOID_CRYSTAL_ASSET =
            ResourceKey.create(EquipmentAssets.ROOT_ID, EndReborn.id("void_crystal"));

    public static final ArmorMaterial CHORUS_ALLOY_ARMOR = new ArmorMaterial(
            25, defense(3, 7, 6, 3), 15, SoundEvents.ARMOR_EQUIP_IRON,
            2.0F, 0.0F, CHORUS_ALLOY_REPAIR, CHORUS_ALLOY_ASSET);
    public static final ArmorMaterial VOID_CRYSTAL_ARMOR = new ArmorMaterial(
            40, defense(4, 9, 7, 4), 20, SoundEvents.ARMOR_EQUIP_DIAMOND,
            4.0F, 0.15F, VOID_CRYSTAL_REPAIR, VOID_CRYSTAL_ASSET);

    private static Map<ArmorType, Integer> defense(int helmet, int chest, int legs, int boots) {
        EnumMap<ArmorType, Integer> m = new EnumMap<>(ArmorType.class);
        m.put(ArmorType.HELMET, helmet);
        m.put(ArmorType.CHESTPLATE, chest);
        m.put(ArmorType.LEGGINGS, legs);
        m.put(ArmorType.BOOTS, boots);
        return m;
    }
}
