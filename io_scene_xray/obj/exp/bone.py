# addon modules
from . import main
from .. import fmt
from ... import xray_io
from ... import log
from ... import utils
from ... import xray_motions


def export_bone(
        bpy_arm_obj, bpy_bone, writers, bonemap, edit_mode_matrices, multiply
    ):
    real_parent = utils.find_bone_exportable_parent(bpy_bone)
    if real_parent:
        if bonemap.get(real_parent) is None:
            export_bone(
                bpy_arm_obj, real_parent, writers, bonemap,
                edit_mode_matrices, multiply
            )

    xray = bpy_bone.xray
    writer = xray_io.ChunkedWriter()
    writers.append(writer)
    bonemap[bpy_bone] = writer
    writer.put(
        fmt.Chunks.Bone.VERSION, xray_io.PackedWriter().putf('H', 0x02)
    )
    bone_name = bpy_bone.name.lower()
    if bone_name != bpy_bone.name:
        log.warn(
            'the bone name has been saved without uppercase characters',
            old=bpy_bone.name,
            new=bone_name
        )
    writer.put(
        fmt.Chunks.Bone.DEF, xray_io.PackedWriter()
        .puts(bone_name)
        .puts(real_parent.name if real_parent else '')
        .puts(bone_name)    # vmap
    )
    mat = edit_mode_matrices[bpy_bone.name]
    if real_parent:
        pm = edit_mode_matrices[real_parent.name]
        mat = multiply(multiply(pm, xray_motions.MATRIX_BONE_INVERTED).inverted(), mat)
    mat = multiply(mat, xray_motions.MATRIX_BONE_INVERTED)
    eul = mat.to_euler('YXZ')
    writer.put(fmt.Chunks.Bone.BIND_POSE, xray_io.PackedWriter()
               .putv3f(mat.to_translation())
               .putf('fff', -eul.x, -eul.z, -eul.y)
               .putf('f', xray.length))
    writer.put(
        fmt.Chunks.Bone.MATERIAL, xray_io.PackedWriter().puts(xray.gamemtl)
    )
    verdif = xray.shape.check_version_different()
    if verdif != 0:
        log.warn(
            'bone edited with a different version of this plugin',
            bone=bpy_bone.name,
            version=xray.shape.fmt_version_different(verdif)
        )
    writer.put(fmt.Chunks.Bone.SHAPE, xray_io.PackedWriter()
               .putf('H', int(xray.shape.type))
               .putf('H', xray.shape.flags)
               .putf('fffffffff', *xray.shape.box_rot)
               .putf('fff', *xray.shape.box_trn)
               .putf('fff', *xray.shape.box_hsz)
               .putf('fff', *xray.shape.sph_pos)
               .putf('f', xray.shape.sph_rad)
               .putf('fff', *xray.shape.cyl_pos)
               .putf('fff', *xray.shape.cyl_dir)
               .putf('f', xray.shape.cyl_hgh)
               .putf('f', xray.shape.cyl_rad))
    pose_bone = bpy_arm_obj.pose.bones[bpy_bone.name]
    ik = xray.ikjoint
    if bpy_arm_obj.data.xray.joint_limits_type == 'XRAY':
        writer.put(fmt.Chunks.Bone.IK_JOINT, xray_io.PackedWriter()
                .putf('I', int(ik.type))
                .putf('ff', ik.lim_x_min, ik.lim_x_max)
                .putf('ff', ik.lim_x_spr, ik.lim_x_dmp)
                .putf('ff', ik.lim_y_min, ik.lim_y_max)
                .putf('ff', ik.lim_y_spr, ik.lim_y_dmp)
                .putf('ff', ik.lim_z_min, ik.lim_z_max)
                .putf('ff', ik.lim_z_spr, ik.lim_z_dmp)
                .putf('ff', ik.spring, ik.damping))
    else:
        writer.put(fmt.Chunks.Bone.IK_JOINT, xray_io.PackedWriter()
                .putf('I', int(ik.type))
                .putf('ff', pose_bone.ik_min_x, pose_bone.ik_max_x)
                .putf('ff', ik.lim_x_spr, ik.lim_x_dmp)
                .putf('ff', pose_bone.ik_min_y, pose_bone.ik_max_y)
                .putf('ff', ik.lim_y_spr, ik.lim_y_dmp)
                .putf('ff', pose_bone.ik_min_z, pose_bone.ik_max_z)
                .putf('ff', ik.lim_z_spr, ik.lim_z_dmp)
                .putf('ff', ik.spring, ik.damping))
    if xray.ikflags:
        writer.put(
            fmt.Chunks.Bone.IK_FLAGS,
            xray_io.PackedWriter().putf('I', xray.ikflags)
        )
        if xray.ikflags_breakable:
            writer.put(fmt.Chunks.Bone.BREAK_PARAMS, xray_io.PackedWriter()
                       .putf('f', xray.breakf.force)
                       .putf('f', xray.breakf.torque))
    if int(ik.type) and xray.friction:
        writer.put(fmt.Chunks.Bone.FRICTION, xray_io.PackedWriter()
                   .putf('f', xray.friction))
    if xray.mass.value:
        writer.put(fmt.Chunks.Bone.MASS_PARAMS, xray_io.PackedWriter()
                   .putf('f', xray.mass.value)
                   .putv3f(xray.mass.center))
