import bpy
import math
from bpy.props import *

bl_info = {
    "name": "Simple Bone Animation",
    "author": "Aki Miyazaki",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Make Simple Bone Animation",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": ""
}

def bone_items(self, context):
    arma = context.scene.objects.get(self.armature)

    if arma is None:
        return [("None","None", "")]
    
    obs= [(bone.name, bone.name, "") for bone in arma.pose.bones]
    
    if len(obs)==0:
        obs.append(("None","None", ""))
        
    return obs

def armature_items(self, context):
    obs = []
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            obs.append((ob.name, ob.name, ""))
            
    if len(obs)==0:
        obs.append(("None","None", ""))
          
    return obs

class SimpleBoneAnimationPropertyGroup(bpy.types.PropertyGroup):
    armature:EnumProperty(
            name="Armature",description="Target armature" ,items=armature_items
            )
    bone:EnumProperty(
            name="Bone",description="Target bone" ,items=bone_items
            )
    use_animation_xyz:BoolVectorProperty(name="Use Animation",subtype="XYZ",description="Use Animation Angle",size=3,default=[True,True,True])

    angle:IntProperty(
                    name="angle",description="animation angle",default=45,
                    min=0,max=180,step=10,soft_max=90
                    )
    
class SIMPLEBONEANIMATION_PT_RootPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "objectmode"
    bl_label = "Make Simple Animation"
    bl_category="SBAnimattion"
    
    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        scene=context.scene
        
        col.prop(scene.simple_bone_animation,"armature")
        armature=scene.simple_bone_animation.armature
        if armature == "None":
            col.label("No Armature(Bone)") #hide from pole
        else:
            mode=bpy.context.object.mode
            if mode !="POSE":
                col.label(text="Need Change Pose Mode")      
            else:      
                col.prop(scene.simple_bone_animation,"bone")
                row=col.row()
                row.prop(scene.simple_bone_animation,"use_animation_xyz")
                col.prop(scene.simple_bone_animation,"angle")
                col.label(text="Insert Key Frame")
                col.operator(SIMPLEBONEANIMATION_OT_MakeAnimation.bl_idname, icon='FILE_MOVIE')
        
        
class SIMPLEBONEANIMATION_OT_MakeAnimation(bpy.types.Operator):
    bl_idname = "makeanimation.simpleboneanimation"
    bl_label = "Make Animation"
    bl_description = "Make simple selected bone animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        simple_bone_animation=context.scene.simple_bone_animation
        armature=simple_bone_animation.armature
        bone=simple_bone_animation.bone
        useAnimationXyz=simple_bone_animation.use_animation_xyz
        animationAngle=simple_bone_animation.angle

        #same as context.object
        sk = bpy.data.objects.get("skelton")#TODO switch ar
        sk = context.scene.objects.get(armature)
       
        #bpy.ops.object.posemode_toggle()
        bpy.ops.object.mode_set(mode='POSE')
        animationBone=bone
        
        bpy.ops.pose.select_all(action='DESELECT')
        bone=bpy.context.object.pose.bones[animationBone]
        
        bpy.context.object.data.bones[animationBone].select=True
        #bpy.context.object.data.bones.active = bpy.context.object.data.bones[boneName]
        
        
        frame_end=context.scene.frame_end
        
        split=1
        for v in useAnimationXyz:
            if v == True:
                split+=2
        
        frame=int(frame_end/split)
        current=frame
        bone.rotation_mode='XYZ'
        bpy.context.scene.frame_set(1)
        bone.rotation_euler[0]=0
        bone.rotation_euler[1]=0
        bone.rotation_euler[2]=0
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        
        for v in range(3):
            if( useAnimationXyz[v]== True):
                bpy.context.scene.frame_set(current)
                bone.rotation_euler[0]=0
                bone.rotation_euler[1]=0
                bone.rotation_euler[2]=0
                bone.rotation_euler[v]=math.radians(animationAngle)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                current+=frame
               
                bpy.context.scene.frame_set(current)
                bone.rotation_euler[0]=0
                bone.rotation_euler[1]=0
                bone.rotation_euler[2]=0
                bone.rotation_euler[v]=math.radians(-animationAngle)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                current+=frame
        #last
        bpy.context.scene.frame_set(frame_end-1)
        bone.rotation_euler[0]=0
        bone.rotation_euler[1]=0
        bone.rotation_euler[2]=0
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        
        
        bpy.context.scene.frame_set(0)
        return {'FINISHED'}    
classes = (
        SIMPLEBONEANIMATION_PT_RootPanel,SIMPLEBONEANIMATION_OT_MakeAnimation
    )
def register():
    #do first
    bpy.utils.register_class(SimpleBoneAnimationPropertyGroup)
    bpy.types.Scene.simple_bone_animation = PointerProperty( type = SimpleBoneAnimationPropertyGroup )
    
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.utils.unregister_class(SimpleBoneAnimationPropertyGroup)
    del bpy.types.Scene.simple_bone_animation

if __name__ == "__main__":
    register()