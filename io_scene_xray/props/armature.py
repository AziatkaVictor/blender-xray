import bpy

from ..version_utils import assign_props, IS_28


joint_limit_type_items = (
    ('IK', 'IK Limits', ''),
    ('XRAY', 'X-Ray Limits', '')
)
xray_armature_properties = {
    'display_bone_shapes': bpy.props.BoolProperty(
        name='Display Bone Shapes', default=False
    ),

    'joint_limits_type': bpy.props.EnumProperty(
        items=joint_limit_type_items, name='Export Limits From', default='IK'
    ),
    'display_bone_limits': bpy.props.BoolProperty(
        name='Display Bone Limits', default=False
    ),
    'display_bone_limits_radius': bpy.props.FloatProperty(
        name='Gizmo Radius', default=0.1, min=0.0
    ),
    'display_bone_limit_x': bpy.props.BoolProperty(name='Limit X', default=True),
    'display_bone_limit_y': bpy.props.BoolProperty(name='Limit Y', default=True),
    'display_bone_limit_z': bpy.props.BoolProperty(name='Limit Z', default=True),
    'link_to_armature': bpy.props.StringProperty(name='Link to Armature')
}


class XRayArmatureProperties(bpy.types.PropertyGroup):
    b_type = bpy.types.Armature

    if not IS_28:
        for prop_name, prop_value in xray_armature_properties.items():
            exec('{0} = xray_armature_properties.get("{0}")'.format(prop_name))

    def check_different_version_bones(self):
        from functools import reduce
        return reduce(
            lambda x, y: x | y,
            [b.xray.shape.check_version_different() for b in self.id_data.bones],
            0,
        )


prop_groups = (
    (XRayArmatureProperties, xray_armature_properties),
)


def register():
    for prop_group, props in prop_groups:
        assign_props([
            (props, prop_group),
        ])
    bpy.utils.register_class(prop_group)
    prop_group.b_type.xray = bpy.props.PointerProperty(type=prop_group)


def unregister():
    for prop_group, props in reversed(prop_groups):
        del prop_group.b_type.xray
        bpy.utils.unregister_class(prop_group)
