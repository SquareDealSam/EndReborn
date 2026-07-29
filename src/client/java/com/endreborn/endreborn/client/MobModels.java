package com.caranci.endreborn.client;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.util.Mth;

// All EndReborn mob models live here (package-private) to keep the tree tidy.
// Each declares a static createBodyLayer() and animates via the render state.

/** Chorus Sprite — tiny body + two flapping wings. */
class ChorusSpriteModel extends EntityModel<LivingEntityRenderState> {
    private final ModelPart body, leftWing, rightWing;

    ChorusSpriteModel(ModelPart root) {
        super(root);
        this.body = root.getChild("body");
        this.leftWing = root.getChild("left_wing");
        this.rightWing = root.getChild("right_wing");
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0).addBox(-1.5F, -1.5F, -1.5F, 3, 3, 3), PartPose.offset(0, 21, 0));
        r.addOrReplaceChild("left_wing", CubeListBuilder.create().texOffs(0, 8).addBox(0, -0.5F, -1.5F, 4, 1, 3), PartPose.offset(1.5F, 21, 0));
        r.addOrReplaceChild("right_wing", CubeListBuilder.create().mirror().texOffs(0, 8).addBox(-4, -0.5F, -1.5F, 4, 1, 3), PartPose.offset(-1.5F, 21, 0));
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(LivingEntityRenderState s) {
        super.setupAnim(s);
        float flap = Mth.cos(s.ageInTicks * 1.6F) * 1.0F;
        this.leftWing.zRot = flap;
        this.rightWing.zRot = -flap;
        this.body.y = 21 + Mth.sin(s.ageInTicks * 0.3F) * 0.5F;
    }
}

/** Crystal Strider — raised body on four legs. */
class CrystalStriderModel extends EntityModel<LivingEntityRenderState> {
    private final ModelPart[] legs;

    CrystalStriderModel(ModelPart root) {
        super(root);
        this.legs = new ModelPart[]{root.getChild("leg0"), root.getChild("leg1"), root.getChild("leg2"), root.getChild("leg3")};
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0).addBox(-3, -4, -5, 6, 6, 10), PartPose.offset(0, 12, 0));
        CubeListBuilder leg = CubeListBuilder.create().texOffs(0, 18).addBox(-1, 0, -1, 2, 8, 2);
        r.addOrReplaceChild("leg0", leg, PartPose.offset(2, 16, -3));
        r.addOrReplaceChild("leg1", leg, PartPose.offset(-2, 16, -3));
        r.addOrReplaceChild("leg2", leg, PartPose.offset(2, 16, 3));
        r.addOrReplaceChild("leg3", leg, PartPose.offset(-2, 16, 3));
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(LivingEntityRenderState s) {
        super.setupAnim(s);
        float sw = Mth.cos(s.walkAnimationPos * 0.6F) * 1.2F * s.walkAnimationSpeed;
        this.legs[0].xRot = sw;
        this.legs[3].xRot = sw;
        this.legs[1].xRot = -sw;
        this.legs[2].xRot = -sw;
    }
}

/** Void Wraith — floating cloak with swaying arms. */
class VoidWraithModel extends EntityModel<LivingEntityRenderState> {
    private final ModelPart body, leftArm, rightArm;

    VoidWraithModel(ModelPart root) {
        super(root);
        this.body = root.getChild("body");
        this.leftArm = root.getChild("left_arm");
        this.rightArm = root.getChild("right_arm");
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0).addBox(-3, -10, -2, 6, 14, 4), PartPose.offset(0, 16, 0));
        r.addOrReplaceChild("head", CubeListBuilder.create().texOffs(24, 0).addBox(-2.5F, -4, -2.5F, 5, 5, 5), PartPose.offset(0, 6, 0));
        r.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(20, 20).addBox(0, -1, -1, 7, 2, 2), PartPose.offset(3, 8, 0));
        r.addOrReplaceChild("right_arm", CubeListBuilder.create().mirror().texOffs(20, 20).addBox(-7, -1, -1, 7, 2, 2), PartPose.offset(-3, 8, 0));
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(LivingEntityRenderState s) {
        super.setupAnim(s);
        float sway = Mth.sin(s.ageInTicks * 0.12F);
        this.leftArm.zRot = -0.4F + sway * 0.3F;
        this.rightArm.zRot = 0.4F - sway * 0.3F;
        this.body.zRot = sway * 0.06F;
    }
}

/** Obsidian Golem — heavy body, head, two arms, two legs. */
class ObsidianGolemModel extends EntityModel<LivingEntityRenderState> {
    private final ModelPart leftArm, rightArm, leftLeg, rightLeg;

    ObsidianGolemModel(ModelPart root) {
        super(root);
        this.leftArm = root.getChild("left_arm");
        this.rightArm = root.getChild("right_arm");
        this.leftLeg = root.getChild("leg0");
        this.rightLeg = root.getChild("leg1");
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0).addBox(-6, -16, -4, 12, 16, 8), PartPose.offset(0, 16, 0));
        r.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 24).addBox(-3, -4, -3, 6, 4, 6), PartPose.offset(0, 0, 0));
        r.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(40, 0).addBox(0, -1, -2, 4, 16, 4), PartPose.offset(6, 2, 0));
        r.addOrReplaceChild("right_arm", CubeListBuilder.create().mirror().texOffs(40, 0).addBox(-4, -1, -2, 4, 16, 4), PartPose.offset(-6, 2, 0));
        r.addOrReplaceChild("leg0", CubeListBuilder.create().texOffs(0, 40).addBox(-2, 0, -2, 4, 8, 4), PartPose.offset(3, 16, 0));
        r.addOrReplaceChild("leg1", CubeListBuilder.create().mirror().texOffs(0, 40).addBox(-2, 0, -2, 4, 8, 4), PartPose.offset(-3, 16, 0));
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(LivingEntityRenderState s) {
        super.setupAnim(s);
        float sw = Mth.cos(s.walkAnimationPos * 0.5F) * 1.0F * s.walkAnimationSpeed;
        this.leftLeg.xRot = sw;
        this.rightLeg.xRot = -sw;
        this.leftArm.xRot = -sw * 0.6F;
        this.rightArm.xRot = sw * 0.6F;
    }
}

/** Abyss Stalker — low body on four splayed legs. */
class AbyssStalkerModel extends EntityModel<LivingEntityRenderState> {
    private final ModelPart[] legs;

    AbyssStalkerModel(ModelPart root) {
        super(root);
        this.legs = new ModelPart[]{root.getChild("leg0"), root.getChild("leg1"), root.getChild("leg2"), root.getChild("leg3")};
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0).addBox(-3, -2, -6, 6, 4, 12), PartPose.offset(0, 18, 0));
        CubeListBuilder leg = CubeListBuilder.create().texOffs(0, 16).addBox(-0.5F, 0, -0.5F, 1, 5, 1);
        r.addOrReplaceChild("leg0", leg, PartPose.offset(3, 19, -4));
        r.addOrReplaceChild("leg1", leg, PartPose.offset(-3, 19, -4));
        r.addOrReplaceChild("leg2", leg, PartPose.offset(3, 19, 4));
        r.addOrReplaceChild("leg3", leg, PartPose.offset(-3, 19, 4));
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(LivingEntityRenderState s) {
        super.setupAnim(s);
        float sw = Mth.cos(s.walkAnimationPos * 0.8F) * 0.8F * s.walkAnimationSpeed;
        this.legs[0].zRot = 0.6F + sw;
        this.legs[1].zRot = -0.6F - sw;
        this.legs[2].zRot = 0.6F - sw;
        this.legs[3].zRot = -0.6F + sw;
    }
}

/** Crystal Sentinel — floating core ringed by spinning shards. */
class CrystalSentinelModel extends EntityModel<LivingEntityRenderState> {
    private final ModelPart core, shards;

    CrystalSentinelModel(ModelPart root) {
        super(root);
        this.core = root.getChild("core");
        this.shards = root.getChild("shards");
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("core", CubeListBuilder.create().texOffs(0, 0).addBox(-3, -3, -3, 6, 6, 6), PartPose.offset(0, 14, 0));
        PartDefinition shards = r.addOrReplaceChild("shards", CubeListBuilder.create(), PartPose.offset(0, 14, 0));
        shards.addOrReplaceChild("s0", CubeListBuilder.create().texOffs(24, 0).addBox(-0.5F, -2, 4, 1, 4, 1), PartPose.ZERO);
        shards.addOrReplaceChild("s1", CubeListBuilder.create().texOffs(24, 0).addBox(-0.5F, -2, -5, 1, 4, 1), PartPose.ZERO);
        shards.addOrReplaceChild("s2", CubeListBuilder.create().texOffs(24, 0).addBox(4, -2, -0.5F, 1, 4, 1), PartPose.ZERO);
        shards.addOrReplaceChild("s3", CubeListBuilder.create().texOffs(24, 0).addBox(-5, -2, -0.5F, 1, 4, 1), PartPose.ZERO);
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(LivingEntityRenderState s) {
        super.setupAnim(s);
        this.shards.yRot = s.ageInTicks * 0.08F;
        this.core.y = 14 + Mth.sin(s.ageInTicks * 0.15F) * 0.6F;
    }
}
