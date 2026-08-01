package com.voidweaver.voidweaver.client;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.util.Mth;

/** Void Moth model: a small body with two flapping wings. */
public class VoidMothModel extends EntityModel<LivingEntityRenderState> {
    private final ModelPart body;
    private final ModelPart leftWing;
    private final ModelPart rightWing;

    public VoidMothModel(ModelPart root) {
        super(root);
        this.body = root.getChild("body");
        this.leftWing = root.getChild("left_wing");
        this.rightWing = root.getChild("right_wing");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        root.addOrReplaceChild("body",
                CubeListBuilder.create().texOffs(0, 0).addBox(-2.0F, -2.0F, -3.0F, 4.0F, 4.0F, 6.0F),
                PartPose.offset(0.0F, 19.0F, 0.0F));
        root.addOrReplaceChild("left_wing",
                CubeListBuilder.create().texOffs(0, 10).addBox(0.0F, -0.5F, -3.0F, 6.0F, 1.0F, 6.0F),
                PartPose.offset(2.0F, 19.0F, 0.0F));
        root.addOrReplaceChild("right_wing",
                CubeListBuilder.create().mirror().texOffs(0, 10).addBox(-6.0F, -0.5F, -3.0F, 6.0F, 1.0F, 6.0F),
                PartPose.offset(-2.0F, 19.0F, 0.0F));
        return LayerDefinition.create(mesh, 32, 32);
    }

    @Override
    public void setupAnim(LivingEntityRenderState state) {
        super.setupAnim(state);
        float flap = Mth.cos(state.ageInTicks * 1.3F) * 0.9F;
        this.leftWing.zRot = flap;
        this.rightWing.zRot = -flap;
        this.body.xRot = 0.15F;
    }
}
