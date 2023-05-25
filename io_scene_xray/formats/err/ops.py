# blender modules
import bpy
import bpy_extras

# addon modules
from . import imp
from .. import ie
from .. import contexts
from ... import log
from ... import utils


op_text = 'Error List'
filename_ext = '.err'

import_props = {
    'directory': bpy.props.StringProperty(subtype='DIR_PATH'),
    'files': bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement
    ),
    'filter_glob': bpy.props.StringProperty(
        default='*.err',
        options={'HIDDEN'}
    ),
    'processed': bpy.props.BoolProperty(default=False, options={'HIDDEN'})
}


class XRAY_OT_import_err(
        utils.ie.BaseOperator,
        bpy_extras.io_utils.ImportHelper
    ):
    bl_idname = 'xray_import.err'
    bl_label = 'Import .err'
    bl_description = 'Imports X-Ray Error List (.err)'
    bl_options = {'REGISTER', 'UNDO'}

    text = op_text
    ext = filename_ext
    filename_ext = filename_ext
    props = import_props

    if not utils.version.IS_28:
        for prop_name, prop_value in props.items():
            exec('{0} = props.get("{0}")'.format(prop_name))

    @log.execute_with_logger
    @utils.ie.set_initial_state
    def execute(self, context):
        imp_ctx = contexts.ImportContext()

        # import files
        utils.ie.import_files(
            self.directory,
            self.files,
            imp.import_file,
            imp_ctx
        )

        return {'FINISHED'}

    @utils.ie.run_imp_exp_operator
    def invoke(self, context, event):    # pragma: no cover
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    utils.version.register_operators(XRAY_OT_import_err)


def unregister():
    bpy.utils.unregister_class(XRAY_OT_import_err)
