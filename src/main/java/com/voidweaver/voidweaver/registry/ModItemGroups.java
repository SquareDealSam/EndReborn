package com.voidweaver.voidweaver.registry;

import com.voidweaver.voidweaver.VoidWeaver;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;

/** Creative-mode tab grouping all VoidWeaver content. */
public final class ModItemGroups {
    private ModItemGroups() {}

    public static final ResourceKey<CreativeModeTab> ENDREBORN =
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, VoidWeaver.id("voidweaver"));

    public static void register() {
        CreativeModeTab tab = CreativeModeTab.builder(CreativeModeTab.Row.TOP, 0)
                .title(Component.translatable("itemGroup.voidweaver"))
                .icon(() -> new ItemStack(ModItems.VOID_CRYSTAL))
                .displayItems((params, output) -> {
                    ModBlocks.ITEM_BLOCKS.forEach(output::accept);
                    ModItems.TAB_ITEMS.forEach(output::accept);
                })
                .build();
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, ENDREBORN, tab);
    }
}
