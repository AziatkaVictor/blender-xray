from tests import utils

import bpy


class TestIOMotions(utils.XRayTestCase):
    def test_io_taked(self):
        # Arrange
        obj = _prepare_animation()

        # Act
        bpy.ops.xray_export.object(
            objects=obj.name, directory=self.outpath(),
            texture_name_from_image_path=False,
            export_motions=True,
        )

        # Assert
        bpy.ops.xray_import.object(
            directory=self.outpath(),
            files=[{'name': 'test.object'}],
        )
        imp_act = bpy.data.actions[1]
        self.assertEqual(len(imp_act.fcurves[0].keyframe_points), 5)  # for now
        self.assertEqual(imp_act.frame_range[1], 4)

    def test_io_baked(self):
        # Arrange
        obj = _prepare_animation()
        bpy.data.actions[0].xray.autobake = 'on'

        # Act
        bpy.ops.xray_export.object(
            objects=obj.name, directory=self.outpath(),
            texture_name_from_image_path=False,
            export_motions=True,
        )

        # Assert
        bpy.ops.xray_import.object(
            directory=self.outpath(),
            files=[{'name': 'test.object'}],
        )
        imp_act = bpy.data.actions[1]
        self.assertEqual(len(imp_act.fcurves[0].keyframe_points), 5)
        self.assertEqual(imp_act.frame_range[1], 4)


def _prepare_animation():
    arm = bpy.data.armatures.new('test')
    obj = bpy.data.objects.new('test', arm)
    utils.link_object(obj)
    utils.set_active_object(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    try:
        bone = arm.edit_bones.new('bone')
        bone.head.z = 0.5
        cbone = arm.edit_bones.new('cbone')
        cbone.parent = bone
        cbone.head.z = 0.5
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')

    pbone = obj.pose.bones['bone']
    pbone.keyframe_insert('location', frame=1, group='bone')
    pbone.location = (1, 2, 3)
    pbone.keyframe_insert('location', frame=5, group='bone')

    motion = obj.xray.motions_collection.add()
    motion.name = bpy.data.actions[0].name

    bmesh = utils.create_bmesh((
        (0, 0, 0),
        (-1, -1, 0), (+1, -1, 0), (+1, +1, 0), (-1, +1, 0),
    ), ((0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1)), True)
    obj_me = utils.create_object(bmesh, True)
    group = obj_me.vertex_groups.new(name='bone')
    group.add(range(len(obj_me.data.vertices)), 1, 'REPLACE')
    obj_me.parent = obj
    obj_me.xray.isroot = False

    return obj
