import bpy

from .. import registry, plugin_prefs
from ..obj.exp import props as obj_exp_props
from ..version_utils import assign_props, IS_28


import_motion_props = {
    'motion_index': bpy.props.IntProperty(),
}


class ImportSkls(bpy.types.PropertyGroup):
    if not IS_28:
        for prop_name, prop_value in import_motion_props.items():
            exec('{0} = import_motion_props.get("{0}")'.format(prop_name))


class ImportOmf(bpy.types.PropertyGroup):
    if not IS_28:
        for prop_name, prop_value in import_motion_props.items():
            exec('{0} = import_motion_props.get("{0}")'.format(prop_name))


convert_materials_mode_items = (
    ('ACTIVE_MATERIAL', 'Active Material', ''),
    ('ACTIVE_OBJECT', 'Active Object', ''),
    ('SELECTED_OBJECTS', 'Selected Objects', ''),
    ('ALL_MATERIALS', 'All Materials', '')
)
convert_materials_shader_type_items = (
    ('PRINCIPLED', 'Principled', ''),
    ('DIFFUSE', 'Diffuse', ''),
    ('EMISSION', 'Emission', '')
)
custom_properties_edit_data_items = (
    ('ALL', 'All', ''),
    ('OBJECT', 'Object', ''),
    ('MESH', 'Mesh', ''),
    ('MATERIAL', 'Material', ''),
    ('ARMATURE', 'Armature', ''),
    ('ACTION', 'Action', '')
)
custom_properties_edit_mode_items = (
    ('ALL', 'All', ''),
    ('SELECTED', 'Selected', ''),
    ('ACTIVE', 'Active', '')
)

xray_scene_properties = {
    'export_root': bpy.props.StringProperty(
        name='Export Root',
        description='The root folder for export',
        subtype='DIR_PATH',
    ),
    'fmt_version': plugin_prefs.PropSDKVersion(),
    'object_export_motions': obj_exp_props.PropObjectMotionsExport(),
    'object_texture_name_from_image_path': obj_exp_props.PropObjectTextureNamesFromPath(),
    'materials_colorize_random_seed': bpy.props.IntProperty(min=0, max=255, options={'SKIP_SAVE'}),
    'materials_colorize_color_power': bpy.props.FloatProperty(
        default=0.5, min=0.0, max=1.0,
        options={'SKIP_SAVE'},
    ),
    'import_skls': bpy.props.PointerProperty(type=ImportSkls),
    'import_omf': bpy.props.PointerProperty(type=ImportOmf),
    # material utils parameters
    'convert_materials_mode': bpy.props.EnumProperty(
        name='Mode', items=convert_materials_mode_items, default='ACTIVE_MATERIAL'
    ),
    'convert_materials_shader_type': bpy.props.EnumProperty(
        name='Shader', items=convert_materials_shader_type_items, default='PRINCIPLED'
    ),
    'materials_set_alpha_mode': bpy.props.BoolProperty(name='Use Alpha', default=True),
    'change_materials_alpha': bpy.props.BoolProperty(name='Change Alpha', default=True),
    'shader_specular_value': bpy.props.FloatProperty(
        name='Specular', default=0.0
    ),
    'change_specular': bpy.props.BoolProperty(name='Change Specular', default=True),
    'shader_roughness_value': bpy.props.FloatProperty(
        name='Roughness', default=0.0
    ),
    'change_roughness': bpy.props.BoolProperty(name='Change Roughness', default=True),
    # custom properties utils
    'custom_properties_edit_data': bpy.props.EnumProperty(
        name='Edit Data', items=custom_properties_edit_data_items, default='ALL'
    ),
    'custom_properties_edit_mode': bpy.props.EnumProperty(
        name='Edit Mode', items=custom_properties_edit_mode_items, default='ALL'
    ),
}


@registry.requires(ImportSkls)
@registry.requires(ImportOmf)
class XRaySceneProperties(bpy.types.PropertyGroup):
    b_type = bpy.types.Scene

    if not IS_28:
        for prop_name, prop_value in xray_scene_properties.items():
            exec('{0} = xray_scene_properties.get("{0}")'.format(prop_name))


assign_props([
    (import_motion_props, ImportSkls),
    (import_motion_props, ImportOmf),
    (xray_scene_properties, XRaySceneProperties)
])
