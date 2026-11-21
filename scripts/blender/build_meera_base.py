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
import mathutils

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
    (1, pose(**{str(spine): (0, 0, 0), str(chest): (0, 0, 0), str(head): (0, 0, 0)})),
    (30, pose(**{str(spine): (0.025, 0, 0), str(chest): (-0.035, 0, 0),
                 head: (0, 0.025, 0)})),
    (60, pose(**{str(spine): (0, 0, 0), str(chest): (0, 0, 0), str(head): (0, 0, 0)})),
])

# Gentle dance: coordinated arm and torso sway.
author_clip("dance_gentle", [
    (1, pose(**{str(upper_arm_l): (0, 0, -0.25), str(upper_arm_r): (0, 0, 0.25),
                spine: (0, 0, -0.08)})),
    (16, pose(**{str(upper_arm_l): (0, 0, -0.65), str(upper_arm_r): (0, 0, 0.65),
                 spine: (0, 0, 0.10), str(head): (0, 0, -0.06)})),
    (32, pose(**{str(upper_arm_l): (0, 0, -0.25), str(upper_arm_r): (0, 0, 0.25),
                 spine: (0, 0, -0.08)})),
    (48, pose(**{str(upper_arm_l): (0, 0, -0.65), str(upper_arm_r): (0, 0, 0.65),
                 spine: (0, 0, 0.10), str(head): (0, 0, 0.06)})),
    (64, pose(**{str(upper_arm_l): (0, 0, -0.25), str(upper_arm_r): (0, 0, 0.25),
                 spine: (0, 0, -0.08)})),
])

# Fuller in-place dance with alternating knee bends and arm sweeps.
author_clip("dance_full", [
    (1, pose(**{str(upper_arm_l): (0, 0, -1.0), str(upper_arm_r): (0, 0, 0.3),
                thigh_l: (0.18, 0, 0), str(calf_l): (-0.12, 0, 0), str(spine): (0, 0, -0.12)})),
    (12, pose(**{str(upper_arm_l): (0, 0, -0.25), str(upper_arm_r): (0, 0, 1.0),
                 thigh_r: (0.18, 0, 0), str(calf_r): (-0.12, 0, 0), str(spine): (0, 0, 0.12)})),
    (24, pose(**{str(upper_arm_l): (0, 0, 0.3), str(upper_arm_r): (0, 0, -1.0),
                 thigh_l: (-0.12, 0, 0), str(spine): (0, 0, 0.12)})),
    (36, pose(**{str(upper_arm_l): (0, 0, 1.0), str(upper_arm_r): (0, 0, -0.25),
                 thigh_r: (-0.12, 0, 0), str(spine): (0, 0, -0.12)})),
    (48, pose(**{str(upper_arm_l): (0, 0, -1.0), str(upper_arm_r): (0, 0, 0.3),
                 thigh_l: (0.18, 0, 0), str(calf_l): (-0.12, 0, 0), str(spine): (0, 0, -0.12)})),
])

# Inspection turn: rotate the root/pelvis through a full revolution.
turn_bone = root or spine
author_clip("turn_360", [
    (1, pose(**{str(turn_bone): (0, 0, 0)})),
    (31, pose(**{str(turn_bone): (0, 0, math.pi)})),
    (61, pose(**{str(turn_bone): (0, 0, 2 * math.pi)})),
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

# Stage 2: dress the SAME adult base as Meera. All garments are separate,
# non-transparent meshes and remain attached to the existing humanoid rig.
def make_mat(name, color, metallic=0.0, roughness=0.62):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

ivory = make_mat("Saree | warm ivory", (0.88, 0.82, 0.69))
pink = make_mat("Saree border | vivid magenta", (0.82, 0.015, 0.20))
lime = make_mat("Blouse | lime green", (0.42, 0.68, 0.08))
black = make_mat("Hair | natural black", (0.018, 0.012, 0.01))
silver = make_mat("Jewellery | silver", (0.65, 0.68, 0.72), 0.78, 0.24)
skin_accent = make_mat("Bindi | deep maroon", (0.22, 0.008, 0.025))

def mesh_object(name, verts, faces, material, bone_name=None):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if bone_name and bone_name in arm.data.bones:
        mod = obj.modifiers.new("Meera rig", "ARMATURE")
        mod.object = arm
        group = obj.vertex_groups.new(name=bone_name)
        group.add(list(range(len(verts))), 1.0, "REPLACE")
    return obj

# Saree lower drape: a continuous modest wrap from waist to ankles.
sv, sf = [], []
rows, segs = 18, 96
for j in range(rows + 1):
    t = j / rows
    y = 0.12 + 0.72 * t
    radius = 0.205 + 0.018 * (1.0 - t)
    for i in range(segs):
        a = 2.0 * math.pi * i / segs
        pleat = 0.008 * math.cos(12.0 * a)
        r = radius + pleat
        sv.append((math.cos(a) * r, y, 0.075 + math.sin(a) * r * 0.78))
for j in range(rows):
    for i in range(segs):
        a = j * segs + i
        b = j * segs + (i + 1) % segs
        sf.append((a, b, b + segs, a + segs))
skirt = mesh_object("Saree | wrapped lower drape", sv, sf, ivory, root or spine)
skirt.modifiers.new("Soft cloth surface", "SOLIDIFY").thickness = 0.006

# Pink hem and waist borders, generated as closed bands.
def ring_band(name, y0, y1, radius, material):
    v, f = [], []
    n = 96
    for y in (y0, y1):
        for i in range(n):
            a = 2 * math.pi * i / n
            v.append((math.cos(a) * radius, y, 0.075 + math.sin(a) * radius * 0.78))
    for i in range(n):
        f.append((i, (i+1)%n, (i+1)%n+n, i+n))
    ob = mesh_object(name, v, f, material, root or spine)
    ob.modifiers.new("Band thickness", "SOLIDIFY").thickness = 0.009
    return ob
ring_band("Saree | magenta hem", 0.105, 0.135, 0.222, pink)
ring_band("Saree | magenta waist trim", 0.815, 0.838, 0.207, pink)

# Fitted lime blouse shell, with a modest neckline and short sleeves.
bv, bf = [], []
br, bn = 10, 64
for j in range(br + 1):
    t = j / br
    y = 0.91 + 0.255 * t
    rx = 0.145 - 0.018 * t
    rz = 0.112 - 0.014 * t
    for i in range(bn):
        a = 2 * math.pi * i / bn
        bv.append((math.cos(a) * rx, y, 0.075 + math.sin(a) * rz))
for j in range(br):
    for i in range(bn):
        a = j*bn+i; b=j*bn+(i+1)%bn
        bf.append((a,b,b+bn,a+bn))
blouse = mesh_object("Blouse | lime green fitted shell", bv, bf, lime, spine or root)
blouse.modifiers.new("Blouse fabric", "SOLIDIFY").thickness = 0.008

# Saree pallu: a broad folded panel over the shoulder and diagonally across
# the front torso. Front of the character is the negative-Z side.
pv, pf = [], []
pr, pc = 28, 16
for j in range(pr + 1):
    t = j / pr
    cx = -0.095 + 0.20 * t
    cy = 1.205 - 0.59 * t
    cz = -0.115 - 0.045 * math.sin(math.pi*t)
    width = 0.255 * (0.88 + 0.12 * math.sin(math.pi*t))
    for i in range(pc + 1):
        u = i / pc - 0.5
        pv.append((cx + u*width, cy + 0.025*math.sin(u*math.pi*2),
                   cz - 0.018*(1.0-4.0*u*u)))
for j in range(pr):
    for i in range(pc):
        a=j*(pc+1)+i; b=a+1
        pf.append((a,b,b+pc+1,a+pc+1))
pallu = mesh_object("Saree | draped shoulder pallu", pv, pf, ivory, spine or root)
pallu.modifiers.new("Pallu fabric thickness", "SOLIDIFY").thickness = 0.008
pallu.modifiers.new("Pallu soft folds", "SUBSURF").levels = 1

# Magenta edging along both long edges of the pallu.
for side in (-0.5, 0.5):
    curve = bpy.data.curves.new("Pallu border curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.008
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(pr)
    for j in range(pr + 1):
        t=j/pr; cx=-0.095+0.20*t; cy=1.205-0.59*t
        cz=-0.115-0.045*math.sin(math.pi*t)
        spline.points[j].co=(cx+side*0.255*(0.88+0.12*math.sin(math.pi*t)),
                             cy+0.025*math.sin(side*math.pi*2),cz-0.018,1)
    edge=bpy.data.objects.new("Saree | pallu magenta edge",curve)
    bpy.context.collection.objects.link(edge); edge.data.materials.append(pink)
    # Keep trim curves in world space; they are decorative, not skinned.

# Hair bun and centre-parted cap; restrained jewellery and bindi.
def uv_sphere(name, location, scale, material, bone_name=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=location)
    ob=bpy.context.object; ob.name=name; ob.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    if bone_name and bone_name in arm.data.bones:
        mod=ob.modifiers.new("Follow head rig","ARMATURE"); mod.object=arm
        vg=ob.vertex_groups.new(name=bone_name); vg.add(list(range(len(ob.data.vertices))),1.0,"REPLACE")
    return ob
uv_sphere("Hair | gathered bun", (0,1.355,0.205), (0.105,0.105,0.085), black, head)
uv_sphere("Bindi", (0,1.245,-0.148), (0.018,0.025,0.009), skin_accent, head)

def torus_accessory(name, location, major, minor, material, bone_name=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                    major_segments=48, minor_segments=10, location=location)
    ob=bpy.context.object; ob.name=name; ob.data.materials.append(material)
    if bone_name and bone_name in arm.data.bones:
        mod=ob.modifiers.new("Follow rig","ARMATURE"); mod.object=arm
        vg=ob.vertex_groups.new(name=bone_name); vg.add(list(range(len(ob.data.vertices))),1.0,"REPLACE")
    return ob
torus_accessory("Necklace | silver chain", (0,1.155,-0.135), 0.105, 0.006, silver, head)
uv_sphere("Necklace | pendant", (0,1.045,-0.145), (0.026,0.038,0.012), silver, spine or head)
torus_accessory("Bangle | left", (-0.265,0.84,-0.015), 0.043, 0.006, silver, upper_arm_l)
torus_accessory("Bangle | right", (0.265,0.84,-0.015), 0.043, 0.006, silver, upper_arm_r)

# Keep all new costume objects in the final export selection.
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj == arm or obj == human or obj.name.startswith((
        "Saree", "Blouse", "Hair", "Bindi", "Necklace", "Bangle"
    )):
        obj.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

final_blend = os.path.join(out_dir, "meera_final.blend")
final_glb = os.path.join(out_dir, "meera_final.glb")
bpy.ops.wm.save_as_mainfile(filepath=final_blend)
bpy.ops.export_scene.gltf(
    filepath=final_glb, export_format="GLB", export_animations=True,
    export_animation_mode="ACTIONS", export_yup=True,
)
# Render a front orthographic preview (the rig uses Y-up coordinates).
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=640; scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
bpy.ops.object.camera_add(location=(0.0,0.72,-4.0))
cam=bpy.context.object; cam.name="Meera preview camera"
cam.rotation_euler=(0.0, math.pi, 0.0)
cam.data.type="ORTHO"; cam.data.ortho_scale=1.65
scene.camera=cam
scene.render.filepath=os.path.join(out_dir,"meera_preview.png")
bpy.ops.render.render(write_still=True)
print("MEERA_FINAL_EXPORTED", final_glb)

print("MEERA_BASE_EXPORTED", glb_path)
