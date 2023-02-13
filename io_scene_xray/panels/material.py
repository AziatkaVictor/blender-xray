# blender modules
import bpy
import bl_operators

# addon modules
from .. import ui
from .. import utils
from .. import formats


class XRAY_MT_shader(ui.dynamic_menu.XRAY_MT_xr_template):
    bl_idname = 'XRAY_MT_shader'
    prop_name = 'eshader'
    cached = ui.dynamic_menu.XRAY_MT_xr_template.create_cached(
        'eshader_file_auto',
        formats.xr.parse_shaders
    )


class XRAY_MT_compile(ui.dynamic_menu.XRAY_MT_xr_template):
    bl_idname = 'XRAY_MT_compile'
    prop_name = 'cshader'
    cached = ui.dynamic_menu.XRAY_MT_xr_template.create_cached(
        'cshader_file_auto',
        formats.xr.parse_shaders_xrlc
    )


class XRAY_MT_material(ui.dynamic_menu.XRAY_MT_xr_template):
    bl_idname = 'XRAY_MT_material'
    prop_name = 'gamemtl'
    cached = ui.dynamic_menu.XRAY_MT_xr_template.create_cached(
        'gamemtl_file_auto',
        formats.xr.parse_gamemtl
    )


def gen_xr_selector(layout, data, name, text):
    row = layout.row(align=True)
    row.prop(data, name, text=text)
    ui.dynamic_menu.DynamicMenu.set_layout_context_data(row, data)
    row.menu('XRAY_MT_' + text.lower(), icon='TRIA_DOWN')


def draw_level_prop(lay, data, prop_name, prop_text, prop_type):
    row = utils.version.layout_split(lay, 0.45)
    row.label(text=prop_text+':')

    if prop_type == 'UV':
        row.prop_search(
            data,
            prop_name,
            bpy.context.active_object.data,
            'uv_layers',
            text=''
        )

    elif prop_type == 'VERTEX':
        row.prop_search(
            data,
            prop_name,
            bpy.context.active_object.data,
            'vertex_colors',
            text=''
        )

    elif prop_type == 'IMAGE':
        row.prop_search(
            data,
            prop_name,
            bpy.data,
            'images',
            text=''
        )


class XRAY_PT_material(ui.base.XRayPanel):
    bl_context = 'material'
    bl_label = ui.base.build_label('Material')

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material

    def draw(self, context):
        layout = self.layout
        material = context.active_object.active_material
        data = material.xray

        box = layout.box()
        box.label(text='Surface:')
        utils.draw.draw_presets(
            box,
            XRAY_MT_surface_presets,
            XRAY_OT_add_surface_preset
        )
        gen_xr_selector(box, data, 'eshader', 'Shader')
        gen_xr_selector(box, data, 'cshader', 'Compile')
        gen_xr_selector(box, data, 'gamemtl', 'Material')
        box.prop(data, 'flags_twosided', text='Two Sided', toggle=True)

        pref = utils.version.get_preferences()
        panel_used = (
            # import formats
            pref.enable_level_import or
            # export formats
            pref.enable_level_export
        )
        if not panel_used:
            return

        box = layout.box()
        box.label(text='Level Visual:')
        draw_level_prop(box, data, 'uv_texture', 'Texture UV', 'UV')
        draw_level_prop(box, data, 'uv_light_map', 'Light Map UV', 'UV')
        draw_level_prop(box, data, 'lmap_0', 'Light Map 1', 'IMAGE')
        draw_level_prop(box, data, 'lmap_1', 'Light Map 2', 'IMAGE')
        draw_level_prop(box, data, 'light_vert_color', 'Light', 'VERTEX')
        draw_level_prop(box, data, 'sun_vert_color', 'Sun', 'VERTEX')
        draw_level_prop(box, data, 'hemi_vert_color', 'Hemi', 'VERTEX')

        box = layout.box()
        box.label(text='Level CForm:')
        box.prop(data, 'suppress_shadows', text='Suppress Shadows')
        box.prop(data, 'suppress_wm', text='Suppress Wallmarks')


class XRAY_MT_surface_presets(bpy.types.Menu):
    bl_label = 'Surface Presets'
    preset_subdir = 'io_scene_xray/surfaces'
    preset_operator = 'script.execute_preset'
    draw = bpy.types.Menu.draw_preset


class XRAY_OT_add_surface_preset(
        bl_operators.presets.AddPresetBase,
        bpy.types.Operator
    ):
    bl_idname = 'xray.surface_preset_add'
    bl_label = 'Add Surface Preset'
    preset_menu = 'XRAY_MT_surface_presets'

    preset_defines = ['xray = bpy.context.material.xray', ]
    preset_subdir = 'io_scene_xray/surfaces'

    preset_values = [
        'xray.' + prop
        for prop in ('eshader', 'cshader', 'gamemtl', 'flags_twosided')
    ]


classes = (
    XRAY_MT_surface_presets,
    XRAY_OT_add_surface_preset,
    XRAY_MT_shader,
    XRAY_MT_compile,
    XRAY_MT_material,
    XRAY_PT_material
)


def register():
    for clas in classes:
        bpy.utils.register_class(clas)


def unregister():
    for clas in reversed(classes):
        bpy.utils.unregister_class(clas)
