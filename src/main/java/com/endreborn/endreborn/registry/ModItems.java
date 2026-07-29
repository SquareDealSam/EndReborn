package com.endreborn.endreborn.registry;

import com.endreborn.endreborn.EndReborn;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;

import java.util.ArrayList;
import java.util.List;

/** Plain (non-block) item registration for EndReborn: materials, later tools/armor. */
public final class ModItems {
    private ModItems() {}

    /** Items to show in the creative tab, in display order. */
    public static final List<Item> TAB_ITEMS = new ArrayList<>();

    public static final Item CHORUS_ALLOY_INGOT = register("chorus_alloy_ingot");
    public static final Item VOID_CRYSTAL = register("void_crystal");
    public static final Item CRYSTAL_SHARD = register("crystal_shard");

    static {
        toolSet("chorus_alloy", ModMaterials.CHORUS_ALLOY, 3.0F, 1.0F, 6.0F, 1.5F);
        armorSet("chorus_alloy", ModMaterials.CHORUS_ALLOY_ARMOR);
        toolSet("void_crystal", ModMaterials.VOID_CRYSTAL, 4.0F, 2.0F, 8.0F, 2.5F);
        armorSet("void_crystal", ModMaterials.VOID_CRYSTAL_ARMOR);
    }

    private static void toolSet(String mat, ToolMaterial m, float sword, float pick, float axe, float shovel) {
        register(mat + "_sword", new Item.Properties().sword(m, sword, -2.4F));
        register(mat + "_pickaxe", new Item.Properties().pickaxe(m, pick, -2.8F));
        register(mat + "_axe", new Item.Properties().axe(m, axe, -3.0F));
        register(mat + "_shovel", new Item.Properties().shovel(m, shovel, -3.0F));
        register(mat + "_hoe", new Item.Properties().hoe(m, -2.0F, 0.0F));
    }

    private static void armorSet(String mat, ArmorMaterial m) {
        register(mat + "_helmet", new Item.Properties().humanoidArmor(m, ArmorType.HELMET));
        register(mat + "_chestplate", new Item.Properties().humanoidArmor(m, ArmorType.CHESTPLATE));
        register(mat + "_leggings", new Item.Properties().humanoidArmor(m, ArmorType.LEGGINGS));
        register(mat + "_boots", new Item.Properties().humanoidArmor(m, ArmorType.BOOTS));
    }

    private static Item register(String name) {
        return register(name, new Item.Properties());
    }

    private static Item register(String name, Item.Properties props) {
        Identifier id = EndReborn.id(name);
        ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, id);
        Item item = new Item(props.setId(key));
        Registry.register(BuiltInRegistries.ITEM, key, item);
        TAB_ITEMS.add(item);
        return item;
    }

    /** Forces class-load so all static registrations run. */
    public static void register() {
        EndReborn.LOGGER.info("[EndReborn] Registered {} items.", TAB_ITEMS.size());
    }
}
