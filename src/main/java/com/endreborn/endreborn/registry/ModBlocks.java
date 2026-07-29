package com.endreborn.endreborn.registry;

import com.endreborn.endreborn.EndReborn;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.ButtonBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.PressurePlateBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.block.state.properties.WoodType;

import java.util.ArrayList;
import java.util.List;

/**
 * Block registration for EndReborn. Every block also registers a matching
 * {@link BlockItem}; item-bearing blocks are collected for the creative tab.
 */
public final class ModBlocks {
    private ModBlocks() {}

    /** Blocks that have an item form, in creative-tab display order. */
    public static final List<Block> ITEM_BLOCKS = new ArrayList<>();

    static {
        // --- Ores ---
        register("chorus_ore", stone(3.0F, 3.0F));
        register("void_crystal_ore", stone(4.0F, 9.0F));

        // --- Chorus wood set ---
        register("chorus_log", wood(2.0F, 3.0F), true);
        register("stripped_chorus_log", wood(2.0F, 3.0F), true);
        register("chorus_wood", wood(2.0F, 3.0F), true);
        register("stripped_chorus_wood", wood(2.0F, 3.0F), true);
        Block chorusPlanks = register("chorus_planks", wood(2.0F, 3.0F));
        registerStairs("chorus_stairs", chorusPlanks, wood(2.0F, 3.0F));
        registerSlab("chorus_slab", wood(2.0F, 3.0F));
        registerFence("chorus_fence", wood(2.0F, 3.0F));
        registerFenceGate("chorus_fence_gate", wood(2.0F, 3.0F));
        registerDoor("chorus_door", woodThin(3.0F));
        registerTrapdoor("chorus_trapdoor", woodThin(3.0F));
        registerPressurePlate("chorus_pressure_plate", wood(2.0F, 3.0F));
        registerButton("chorus_button", wood(2.0F, 3.0F));
        register("chorus_leaves", leaves());

        // --- Stone families (base + stairs/slab/wall + polished + chiseled + bricks) ---
        stoneFamily("void_stone", 1.5F, 6.0F, ModSounds.VOID_STONE_SOUNDS);
        stoneFamily("crystal_stone", 1.5F, 6.0F, ModSounds.CRYSTAL_SOUNDS);
        stoneFamily("obsidian", 3.0F, 1200.0F, ModSounds.OBSIDIAN_SOUNDS);

        // --- Storage blocks ---
        register("chorus_alloy_block", BlockBehaviour.Properties.of()
                .strength(5.0F, 6.0F).requiresCorrectToolForDrops().sound(SoundType.METAL));
        register("void_crystal_block", BlockBehaviour.Properties.of()
                .strength(5.0F, 6.0F).requiresCorrectToolForDrops().sound(SoundType.AMETHYST));

        // --- Biome flora ---
        register("void_bloom", plant(9));
        register("crystal_bloom", plant(0));

        // --- Lush alien vegetation + ground cover (biome overhaul) ---
        register("alien_grass_block", BlockBehaviour.Properties.of()
                .strength(0.6F).sound(SoundType.GRASS));
        register("void_moss_block", BlockBehaviour.Properties.of()
                .strength(0.6F).sound(SoundType.MOSS));
        register("glowstalk", plant(13));
        register("glow_fungus", plant(12));
        register("giant_bloom", plant(6));
        register("crystal_flower", plant(9));
        register("void_fern", plant(0));
    }

    private static BlockBehaviour.Properties plant(int light) {
        BlockBehaviour.Properties p = BlockBehaviour.Properties.of()
                .noCollision().instabreak().noOcclusion().sound(SoundType.GRASS);
        return light > 0 ? p.lightLevel(state -> light) : p;
    }

    // ---- property presets ----
    private static BlockBehaviour.Properties stone(float hardness, float resistance) {
        return stone(hardness, resistance, SoundType.STONE);
    }

    private static BlockBehaviour.Properties stone(float hardness, float resistance, SoundType sound) {
        return BlockBehaviour.Properties.of()
                .strength(hardness, resistance)
                .requiresCorrectToolForDrops()
                .sound(sound);
    }

    private static BlockBehaviour.Properties wood(float hardness, float resistance) {
        return BlockBehaviour.Properties.of()
                .strength(hardness, resistance)
                .sound(ModSounds.CHORUS_WOOD_SOUNDS);
    }

    private static BlockBehaviour.Properties woodThin(float hardness) {
        return wood(hardness, hardness).noOcclusion();
    }

    private static BlockBehaviour.Properties leaves() {
        return BlockBehaviour.Properties.of()
                .strength(0.2F)
                .sound(SoundType.GRASS)
                .noOcclusion();
    }

    // ---- full stone family ----
    private static void stoneFamily(String base, float h, float r, SoundType snd) {
        String bricks = base + "_bricks";

        Block baseBlock = register(base, stone(h, r, snd));
        registerStairs(base + "_stairs", baseBlock, stone(h, r, snd));
        registerSlab(base + "_slab", stone(h, r, snd));
        registerWall(base + "_wall", stone(h, r, snd));

        Block polished = register("polished_" + base, stone(h, r, snd));
        registerStairs("polished_" + base + "_stairs", polished, stone(h, r, snd));
        registerSlab("polished_" + base + "_slab", stone(h, r, snd));
        registerWall("polished_" + base + "_wall", stone(h, r, snd));

        register("chiseled_" + base, stone(h, r, snd));

        Block brickBlock = register(bricks, stone(h, r, snd));
        registerStairs(bricks + "_stairs", brickBlock, stone(h, r, snd));
        registerSlab(bricks + "_slab", stone(h, r, snd));
        registerWall(bricks + "_wall", stone(h, r, snd));
    }

    // ---- registration helpers ----
    private static ResourceKey<Block> blockKey(String name) {
        return ResourceKey.create(Registries.BLOCK, EndReborn.id(name));
    }

    private static Block finish(String name, ResourceKey<Block> key, Block block) {
        Registry.register(BuiltInRegistries.BLOCK, key, block);
        ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, EndReborn.id(name));
        Registry.register(BuiltInRegistries.ITEM, itemKey,
                new BlockItem(block, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix()));
        ITEM_BLOCKS.add(block);
        return block;
    }

    private static Block register(String name, BlockBehaviour.Properties props) {
        return register(name, props, false);
    }

    private static Block register(String name, BlockBehaviour.Properties props, boolean pillar) {
        ResourceKey<Block> key = blockKey(name);
        Block block = pillar ? new RotatedPillarBlock(props.setId(key)) : new Block(props.setId(key));
        return finish(name, key, block);
    }

    private static Block registerStairs(String name, Block base, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        // StairBlock's constructor is protected; anonymous subclass grants access.
        Block block = new StairBlock(base.defaultBlockState(), props.setId(key)) {};
        return finish(name, key, block);
    }

    private static Block registerSlab(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new SlabBlock(props.setId(key)));
    }

    private static Block registerWall(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new WallBlock(props.setId(key)));
    }

    private static Block registerFence(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new FenceBlock(props.setId(key)));
    }

    private static Block registerFenceGate(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new FenceGateBlock(WoodType.OAK, props.setId(key)));
    }

    // Door/TrapDoor/PressurePlate/Button constructors are protected -> anonymous subclass.
    private static Block registerDoor(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new DoorBlock(BlockSetType.OAK, props.setId(key)) {});
    }

    private static Block registerTrapdoor(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new TrapDoorBlock(BlockSetType.OAK, props.setId(key)) {});
    }

    private static Block registerPressurePlate(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new PressurePlateBlock(BlockSetType.OAK, props.setId(key)) {});
    }

    private static Block registerButton(String name, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(name);
        return finish(name, key, new ButtonBlock(BlockSetType.OAK, 30, props.setId(key)) {});
    }

    /** Forces class-load so the static block runs. */
    public static void register() {
        EndReborn.LOGGER.info("[EndReborn] Registered {} block items.", ITEM_BLOCKS.size());
    }
}
