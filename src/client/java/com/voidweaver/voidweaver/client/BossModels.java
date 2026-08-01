package com.voidweaver.voidweaver.client;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.util.Mth;

/** Boss models — animate on idle plus attack/phase state from {@link BossRenderState}.
 *
 * Chorus Guardian — a floating crystal core with four radiating shard-arms. */
class ChorusGuardianModel extends EntityModel<BossRenderState> {
    private final ModelPart core;
    private final ModelPart[] arms;

    ChorusGuardianModel(ModelPart root) {
        super(root);
        this.core = root.getChild("core");
        this.arms = new ModelPart[]{root.getChild("arm0"), root.getChild("arm1"),
                root.getChild("arm2"), root.getChild("arm3")};
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("core", CubeListBuilder.create().texOffs(0, 0).addBox(-4, -8, -4, 8, 14, 8), PartPose.offset(0, 10, 0));
        CubeListBuilder ax = CubeListBuilder.create().texOffs(0, 24).addBox(0, -1, -1, 9, 2, 2);
        CubeListBuilder az = CubeListBuilder.create().texOffs(0, 24).addBox(-1, -1, 0, 2, 2, 9);
        r.addOrReplaceChild("arm0", ax, PartPose.offset(4, 8, 0));
        r.addOrReplaceChild("arm1", CubeListBuilder.create().mirror().texOffs(0, 24).addBox(-9, -1, -1, 9, 2, 2), PartPose.offset(-4, 8, 0));
        r.addOrReplaceChild("arm2", az, PartPose.offset(0, 8, 4));
        r.addOrReplaceChild("arm3", CubeListBuilder.create().texOffs(0, 24).addBox(-1, -1, -9, 2, 2, 9), PartPose.offset(0, 8, -4));
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(BossRenderState s) {
        super.setupAnim(s);
        this.core.yRot = s.ageInTicks * 0.03F;
        this.core.y = 10 + Mth.sin(s.ageInTicks * 0.1F) * 0.5F;
        float flare = s.attackState > 0 ? 0.7F : 0.15F + Mth.sin(s.ageInTicks * 0.15F) * 0.1F;
        this.arms[0].zRot = -flare;
        this.arms[1].zRot = flare;
        this.arms[2].xRot = flare;
        this.arms[3].xRot = -flare;
    }
}

/** The Voidbringer — towering void being; raises arms to attack, spreads them when enraged. */
class VoidbringerModel extends EntityModel<BossRenderState> {
    private final ModelPart body, head, leftArm, rightArm;

    VoidbringerModel(ModelPart root) {
        super(root);
        this.body = root.getChild("body");
        this.head = root.getChild("head");
        this.leftArm = root.getChild("left_arm");
        this.rightArm = root.getChild("right_arm");
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0).addBox(-5, -18, -3, 10, 18, 6), PartPose.offset(0, 20, 0));
        r.addOrReplaceChild("head", CubeListBuilder.create().texOffs(32, 0).addBox(-3, -5, -3, 6, 5, 6), PartPose.offset(0, 2, 0));
        r.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(0, 24).addBox(0, -1, -2, 4, 16, 4), PartPose.offset(5, 4, 0));
        r.addOrReplaceChild("right_arm", CubeListBuilder.create().mirror().texOffs(0, 24).addBox(-4, -1, -2, 4, 16, 4), PartPose.offset(-5, 4, 0));
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(BossRenderState s) {
        super.setupAnim(s);
        this.body.zRot = Mth.sin(s.ageInTicks * 0.08F) * 0.05F;
        this.head.yRot = Mth.sin(s.ageInTicks * 0.12F) * 0.3F;
        float raise = s.attackState > 0 ? -1.3F : -0.2F + Mth.sin(s.ageInTicks * 0.1F) * 0.1F;
        this.leftArm.xRot = raise;
        this.rightArm.xRot = raise;
        float spread = s.phase >= 3 ? 0.6F : 0.15F;
        this.leftArm.zRot = -spread;
        this.rightArm.zRot = spread;
    }
}

/** The Prismarch — crystal-armoured colossus with a rune crown and four floating
 * hands that orbit its body, spinning faster while attacking. */
class PrismarchModel extends EntityModel<BossRenderState> {
    private final ModelPart body;
    private final ModelPart head;
    private final ModelPart crown;
    private final ModelPart[] hands = new ModelPart[4];

    PrismarchModel(ModelPart root) {
        super(root);
        this.body = root.getChild("body");
        this.head = root.getChild("head");
        this.crown = root.getChild("crown");
        for (int i = 0; i < 4; i++) {
            this.hands[i] = root.getChild("hand" + i);
        }
    }

    static LayerDefinition createBodyLayer() {
        MeshDefinition m = new MeshDefinition();
        PartDefinition r = m.getRoot();
        r.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0).addBox(-6, -14, -4, 12, 16, 8), PartPose.offset(0, 18, 0));
        r.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 24).addBox(-4, -6, -4, 8, 6, 8), PartPose.offset(0, 4, 0));
        r.addOrReplaceChild("crown", CubeListBuilder.create().texOffs(0, 40).addBox(-1.5F, -13, -1.5F, 3, 7, 3), PartPose.offset(0, 2, 0));
        r.addOrReplaceChild("leg0", CubeListBuilder.create().texOffs(32, 0).addBox(-2.5F, 0, -2.5F, 5, 10, 5), PartPose.offset(3, 20, 0));
        r.addOrReplaceChild("leg1", CubeListBuilder.create().mirror().texOffs(32, 0).addBox(-2.5F, 0, -2.5F, 5, 10, 5), PartPose.offset(-3, 20, 0));
        for (int i = 0; i < 4; i++) {
            r.addOrReplaceChild("hand" + i, CubeListBuilder.create().texOffs(48, 0).addBox(9, -3, -3, 4, 6, 5), PartPose.offset(0, 12, 0));
        }
        return LayerDefinition.create(m, 64, 64);
    }

    @Override
    public void setupAnim(BossRenderState s) {
        super.setupAnim(s);
        float age = s.ageInTicks;
        float spin = s.attackState > 0 ? 0.12F : 0.05F;
        for (int i = 0; i < 4; i++) {
            this.hands[i].yRot = age * spin + i * (Mth.PI / 2F);
            this.hands[i].zRot = Mth.sin(age * 0.1F + i) * 0.25F;
            this.hands[i].y = 12 + Mth.sin(age * 0.12F + i * 1.5F) * 1.5F;
        }
        this.body.zRot = Mth.sin(age * 0.06F) * 0.04F;
        this.head.y = 4 + Mth.sin(age * 0.08F) * 0.5F;
        this.crown.y = 2 + Mth.sin(age * 0.08F) * 0.5F;
    }
}
