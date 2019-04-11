import bpy
import math
from bpy.props import *
from mathutils import (
            Vector,Matrix
            )

bl_info = {
    "name": "PoseGround",
    "author": "Aki Miyazaki",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "",
    "description": "move min-y bone to 0",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": ""
}
def armature_items(self, context):
    obs = []
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            obs.append((ob.name, ob.name, ""))
            
    if len(obs)==0:
        obs.append(("None","None", ""))
          
    return obs
def bone_items(self, context):
    arma = context.scene.objects.get(self.armature)
    if arma is None:
        return
    obs= [(bone.name, bone.name, "") for bone in arma.pose.bones]
    if len(obs)==0:
        obs.append(("None","None", ""))
    return obs

class POSEGROUNDPropertyGroup(bpy.types.PropertyGroup):
    groundHeight : bpy.props.FloatProperty(name="ground",default=0.03)
    armature : bpy.props.EnumProperty(name="armature",items=armature_items)
    targetBone : bpy.props.EnumProperty(name="targetBone",items=bone_items)
    

class POSEGROUND_PT_RootPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "posemode"
    bl_category="PG"
    #bl_context = "objectmode"
    
    #bl_space_type = "PROPERTIES"
    #bl_region_type = "WINDOW"
    #bl_context = "object"
    
    bl_label = "Pose to Ground"
    



    def draw(self, context):
        poseground=bpy.context.scene.poseground
        layout=self.layout
        column=layout.column()
        arma = context.scene.objects.get(poseground.armature)
        if arma == "None":
            column.label(text="No Armature(Bone)")
            return
        
        column.prop(poseground,"groundHeight")
        
        column=layout.column(align=True)
        column.operator(POSEGROUND_OT_GroundOn.bl_idname).groundHeight=poseground.groundHeight
        row=layout.row(align=True)
        row.operator(POSEGROUND_OT_GroundOn.bl_idname,text="Zero").groundHeight=0
        row.operator(POSEGROUND_OT_GroundOn.bl_idname,text="Half").groundHeight=poseground.groundHeight/2
        row.operator(POSEGROUND_OT_GroundOn.bl_idname,text="Double").groundHeight=poseground.groundHeight*2
        
        column=layout.column(align=True)
        column.prop(poseground,"armature")
        column.prop(poseground,"targetBone")
        column.label(text="Don't rotate target&parent")
        
        
class POSEGROUND_OT_GroundOn(bpy.types.Operator):
    bl_idname = "poseground.groundon"
    bl_label = "Ground On"
    bl_description = "test"
    bl_options = {'REGISTER', 'UNDO'}

    groundHeight:bpy.props.FloatProperty()

    def execute(self, context):
        
        ignores=["Root","Global","Position"] #TODO add manually
        
        scene=bpy.context.scene
        poseground=bpy.context.scene.poseground
        arma =scene.objects.get(poseground.armature)
         
        minName=None
        minY=float('inf')
        for bone in arma.pose.bones:
            if bone.name.startswith("ik_"):
                continue
            match=False
            for ignore in ignores:
                if ignore==bone.name:
                    match=True
                    break
            
            if match:
                continue
            
            #location= bone.head
            location=(arma.matrix_world @ bone.matrix).to_translation()
            #print(bone.name,location[2])
            y=location[2]
            if y<minY:
                minY=y
                minName=bone.name
        
        print("min",minName,"value",minY)
        ground = self.groundHeight
        target=arma.pose.bones.get(poseground.targetBone)
        
        diff=Vector((0,0,ground-minY))
        
        matrixLoc=target.matrix.to_quaternion()@diff
        print("diff",diff)
        print("mdiff",matrixLoc)
        #target.location+=matrixLoc
        target.location[1]+=diff[2]

        return {'FINISHED'}    
classes = (
    POSEGROUND_PT_RootPanel,POSEGROUND_OT_GroundOn
    )
def register():
    #do first
    bpy.utils.register_class(POSEGROUNDPropertyGroup)
    bpy.types.Scene.poseground = bpy.props.PointerProperty( type = POSEGROUNDPropertyGroup )
    
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.utils.unregister_class(POSEGROUNDPropertyGroup)
    del bpy.types.Scene.poseground

if __name__ == "__main__":
    register()