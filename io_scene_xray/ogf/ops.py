import bpy
from bpy_extras import io_utils

from ..utils import (
    execute_with_logger,
    execute_require_filepath,
    set_cursor_state
)
from ..version_utils import assign_props, IS_28
from .. import ui, context, prefs
from ..obj.exp import props as obj_exp_props
from . import exp


model_export_helper_props = {
    'selection_only': bpy.props.BoolProperty(
        name='Selection Only',
        description='Export only selected objects'
    ),
}


class ExportOgfContext(context.ExportMeshContext):
    def __init__(self):
        context.ExportMeshContext.__init__(self)


class ModelExportHelper:
    if not IS_28:
        for prop_name, prop_value in model_export_helper_props.items():
            exec('{0} = model_export_helper_props.get("{0}")'.format(prop_name))

    def export(self, bpy_obj, context):
        pass

    @execute_with_logger
    @execute_require_filepath
    @set_cursor_state
    def execute(self, context):
        objs = context.selected_objects if self.selection_only else context.scene.objects
        roots = [obj for obj in objs if obj.xray.isroot]
        if not roots:
            self.report({'ERROR'}, 'Cannot find object root')
            return {'CANCELLED'}
        if len(roots) > 1:
            self.report({'ERROR'}, 'Too many object roots found')
            return {'CANCELLED'}
        return self.export(roots[0], context)


filename_ext = '.ogf'
op_export_ogf_props = {
    'filter_glob': bpy.props.StringProperty(default='*'+filename_ext, options={'HIDDEN'}),
    'texture_name_from_image_path': obj_exp_props.PropObjectTextureNamesFromPath()
}


class OpExportOgf(bpy.types.Operator, io_utils.ExportHelper, ModelExportHelper):
    bl_idname = 'xray_export.ogf'
    bl_label = 'Export .ogf'

    filename_ext = '.ogf'

    if not IS_28:
        for prop_name, prop_value in op_export_ogf_props.items():
            exec('{0} = op_export_ogf_props.get("{0}")'.format(prop_name))

    def export(self, bpy_obj, context):
        export_context = ExportOgfContext()
        export_context.texname_from_path = self.texture_name_from_image_path
        exp.export_file(bpy_obj, self.filepath, export_context)
        return {'FINISHED'}

    def invoke(self, context, event):
        preferences = prefs.utils.get_preferences()
        self.texture_name_from_image_path = preferences.object_texture_names_from_path
        return super().invoke(context, event)


def menu_func_export(self, _context):
    icon = ui.icons.get_stalker_icon()
    self.layout.operator(
        OpExportOgf.bl_idname,
        text='X-Ray game object (.ogf)',
        icon_value=icon
    )


def register():
    assign_props([
        (model_export_helper_props, ModelExportHelper),
        (op_export_ogf_props, OpExportOgf)
    ])
    bpy.utils.register_class(OpExportOgf)


def unregister():
    bpy.utils.unregister_class(OpExportOgf)
