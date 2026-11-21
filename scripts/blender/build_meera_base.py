"""
MEERA Stage 1 builder.
Creates a clearly adult, non-sexualized anatomical base using MPFB2/MakeHuman,
adds a game-engine humanoid rig and four named motion clips, then exports GLB
and editable BLEND source. The Indian outfit is a later layer on this same rig.
Run:
  blender --background --python scripts/blender/build_meera_base.py -- <mpfb2.zip> <output_dir>
"""
import bpy
import sys
import os
import importlib
import math

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) < 2:
    raise SystemExit("Expected: <mpfb2.zip> <output_dir>")
addon_zip, out_dir = args[0], os.path.abspath(args[1])
os.makedirs(out_dir, exist_ok=True)

# Clean scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Install and load MPFB2.
try:
    bpy.ops.extensions.package_install_files(
        filepath=os.path.abspath(addon_zip),
        enable_on_install=True,
        repo="user_default",
    )
except Exception as exc:
    print("MPFB install note:", repr(exc))

module_name = next(
    (name for name in sys.modules if name.endswith(".mpfb") or name == "mpfb"),
    None,
)
if not module_name:
    raise RuntimeError("MPFB2 did not load; check Blender/add-on compatibility.")

HumanService = importlib.import_module(
    module_name + ".services.humanservice"
).HumanService
TargetService = importlib.import_module(
    module_name + ".services.targetservice"
).TargetService

# MPFB macro values: female, clearly adult, Asian phenotype. Never use child settings.
macro = TargetService.get_default_macro_info_dict()
macro["gender"] = 0.0
macro["age"] = 0.38
macro["height"] = 0.55
macro["weight"] = 0.48
macro["muscle"] = 0.36
macro["race"] = {"asian": 1.0, "caucasian": 0.0, "african": 0.0}
human = HumanService.create_human(macro_detail_dict=macro)
HumanService.add_builtin_rig(human, "game_engine")

arm = next((obj for obj in bpy.data.objects if obj.type == "ARMATURE"), None)
if arm is None:
    raise RuntimeError("MPFB did not create the expected humanoid armature.")

# Bake the chosen body shape into the base mesh so the GLB has a stable silhouette.
if human.data.shape_keys:
    mixed = human.shape_key_add(name="_meera_bake", from_mix=True)
    coordinates = [vertex.co.copy() for vertex in mixed.data]
    bpy.context.view_layer.objects.active = human
    bpy.ops.object.shape_key_remove(all=True)
    for index, vertex in enumerate(human.data.vertices):
        vertex.co = coordinates[index]

# Make sure the canonical base has no garments/accessories from a default preset.
# MPFB create_human() creates the body only; clothing is deliberately a later stage.

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
pose_bones = arm.pose.bones
for bone in pose_bones:
    bone.rotation_mode = "XYZ"

def find_bone(*names):
    for name in names:
        if name in pose_bones:
            return name
    return None

root = find_bone("root", "pelvis", "hips")
spine = find_bone("spine_02", "spine_01", "spine")
chest = find_bone("spine_03", "chest")
head = find_bone("head")
upper_arm_l = find_bone("upperarm_l")
upper_arm_r = find_bone("upperarm_r")
forearm_l = find_bone("lowerarm_l")
forearm_r = find_bone("lowerarm_r")
thigh_l = find_bone("thigh_l", "upperleg_l")
thigh_r = find_bone("thigh_r", "upperleg_r")
calf_l = find_bone("calf_l", "lowerleg_l")
calf_r = find_bone("calf_r", "lowerleg_r")

animation_data = arm.animation_data_create()

def author_clip(name, frames):
    for bone in pose_bones:
        bone.rotation_euler = (0.0, 0.0, 0.0)
    action = bpy.data.actions.new(name=name)
    animation_data.action = action
    for frame, values in frames:
        for bone_name, rotation in values.items():
            if bone_name and bone_name in pose_bones:
                pose_bones[bone_name].rotation_euler = rotation
                pose_bones[bone_name].keyframe_insert(
                    data_path="rotation_euler", frame=frame
                )
    track = animation_data.nla_tracks.new()
    track.name = name
    track.strips.new(name, 1, action)
    animation_data.action = None

def pose(**values):
    return {key: value for key, value in values.items() if key}

# Relaxed idle: subtle spine/chest/head motion.
author_clip("idle", [
    (1, pose(**{spine: (0, 0, 0), chest: (0, 0, 0), head: (0, 0, 0)})),
    (30, pose(**{spine: (0.025, 0, 0), chest: (-0.035, 0, 0),
                 head: (0, 0.025, 0)})),
    (60, pose(**{spine: (0, 0, 0), chest: (0, 0, 0), head: (0, 0, 0)})),
])

# Gentle dance: coordinated arm and torso sway.
author_clip("dance_gentle", [
    (1, pose(**{upper_arm_l: (0, 0, -0.25), upper_arm_r: (0, 0, 0.25),
                spine: (0, 0, -0.08)})),
    (16, pose(**{upper_arm_l: (0, 0, -0.65), upper_arm_r: (0, 0, 0.65),
                 spine: (0, 0, 0.10), head: (0, 0, -0.06)})),
    (32, pose(**{upper_arm_l: (0, 0, -0.25), upper_arm_r: (0, 0, 0.25),
                 spine: (0, 0, -0.08)})),
    (48, pose(**{upper_arm_l: (0, 0, -0.65), upper_arm_r: (0, 0, 0.65),
                 spine: (0, 0, 0.10), head: (0, 0, 0.06)})),
    (64, pose(**{upper_arm_l: (0, 0, -0.25), upper_arm_r: (0, 0, 0.25),
                 spine: (0, 0, -0.08)})),
])

# Fuller in-place dance with alternating knee bends and arm sweeps.
author_clip("dance_full", [
    (1, pose(**{upper_arm_l: (0, 0, -1.0), upper_arm_r: (0, 0, 0.3),
                thigh_l: (0.18, 0, 0), calf_l: (-0.12, 0, 0), spine: (0, 0, -0.12)})),
    (12, pose(**{upper_arm_l: (0, 0, -0.25), upper_arm_r: (0, 0, 1.0),
                 thigh_r: (0.18, 0, 0), calf_r: (-0.12, 0, 0), spine: (0, 0, 0.12)})),
    (24, pose(**{upper_arm_l: (0, 0, 0.3), upper_arm_r: (0, 0, -1.0),
                 thigh_l: (-0.12, 0, 0), spine: (0, 0, 0.12)})),
    (36, pose(**{upper_arm_l: (0, 0, 1.0), upper_arm_r: (0, 0, -0.25),
                 thigh_r: (-0.12, 0, 0), spine: (0, 0, -0.12)})),
    (48, pose(**{upper_arm_l: (0, 0, -1.0), upper_arm_r: (0, 0, 0.3),
                 thigh_l: (0.18, 0, 0), calf_l: (-0.12, 0, 0), spine: (0, 0, -0.12)})),
])

# Inspection turn: rotate the root/pelvis through a full revolution.
turn_bone = root or spine
author_clip("turn_360", [
    (1, pose(**{turn_bone: (0, 0, 0)})),
    (31, pose(**{turn_bone: (0, 0, math.pi)})),
    (61, pose(**{turn_bone: (0, 0, 2 * math.pi)})),
])

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 64
bpy.ops.object.mode_set(mode="OBJECT")

# Select only the character meshes and armature for a clean GLB export.
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj == arm or obj == human or (obj.type == "MESH" and arm in obj.parent.children if obj.parent else False):
        obj.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

blend_path = os.path.join(out_dir, "meera_base.blend")
glb_path = os.path.join(out_dir, "meera_base.glb")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format="GLB",
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_yup=True,
)
print("MEERA_BASE_EXPORTED", glb_path)
