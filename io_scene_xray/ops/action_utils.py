# blender modules
import bpy

# addon modules
from .. import xray_ltx
from .. import version_utils


SECTION_NAME = 'action_xray_settings'


def get_xray_settings():
    obj = bpy.context.object
    if not obj:
        return
    anim_data = obj.animation_data
    if anim_data:
        action = anim_data.action
        xray = action.xray
        return xray


def write_buffer_data():
    xray = get_xray_settings()
    buffer_text = ''
    if xray:
        buffer_text += '[{}]\n'.format(SECTION_NAME)
        buffer_text += 'fps = {}\n'.format(xray.fps)
        buffer_text += 'flags = {}\n'.format(xray.flags)
        buffer_text += 'speed = {}\n'.format(xray.speed)
        buffer_text += 'accrue = {}\n'.format(xray.accrue)
        buffer_text += 'falloff = {}\n'.format(xray.falloff)
        buffer_text += 'power = {}\n'.format(xray.power)
        buffer_text += 'bonepart_name = "{}"\n'.format(xray.bonepart_name)
        buffer_text += 'bonestart_name = "{}"\n'.format(xray.bonestart_name)
    bpy.context.window_manager.clipboard = buffer_text


def read_buffer_data():
    xray = get_xray_settings()
    if xray:
        buffer_text = bpy.context.window_manager.clipboard
        ltx = xray_ltx.StalkerLtxParser(None, data=buffer_text)
        section = ltx.sections.get(SECTION_NAME, None)
        if not section:
            return
        params = section.params
        xray.fps = float(params.get('fps'))
        xray.flags = int(params.get('flags'))
        xray.speed = float(params.get('speed'))
        xray.accrue = float(params.get('accrue'))
        xray.falloff = float(params.get('falloff'))
        xray.power = float(params.get('power'))
        xray.bonepart_name = params.get('bonepart_name')
        xray.bonestart_name = params.get('bonestart_name')


class XRAY_OT_copy_action_settings(bpy.types.Operator):
    bl_idname = 'io_scene_xray.copy_action_settings'
    bl_label = 'Copy'

    def execute(self, context):
        write_buffer_data()
        return {'FINISHED'}


class XRAY_OT_paste_action_settings(bpy.types.Operator):
    bl_idname = 'io_scene_xray.paste_action_settings'
    bl_label = 'Paste'

    def execute(self, context):
        read_buffer_data()
        return {'FINISHED'}


change_action_bake_settings_props = {
    'change_mode': bpy.props.EnumProperty(
        name='Mode',
        items=(
            ('active', 'Active', ''),
            ('selected', 'Selected', ''),
            ('all', 'All', '')
        ),
        default='active'
    ),
    'change_auto_bake_mode': bpy.props.BoolProperty(
        name='Change Auto Bake Mode', default=True
    ),
    'auto_bake_mode': bpy.props.EnumProperty(
        name='Auto Bake Mode',
        items=(
            ('auto', 'Auto', ''),
            ('on', 'On', ''),
            ('off', 'Off', '')
        ),
        default='auto'
    ),
    'change_use_custom_thresholds': bpy.props.BoolProperty(
        name='Change Use Custom Thresholds', default=True
    ),
    'use_custom_threshold': bpy.props.BoolProperty(
        name='Use Custom Thresholds', default=True
    ),
    'change_location_threshold': bpy.props.BoolProperty(
        name='Change Location Threshold', default=True
    ),
    'change_rotation_threshold': bpy.props.BoolProperty(
        name='Change Rotation Threshold', default=True
    ),
    'value_location_threshold': bpy.props.FloatProperty(
        name='Location Threshold', default=0.00001, precision=6
    ),
    'value_rotation_threshold': bpy.props.FloatProperty(
        name='Rotation Threshold', default=0.00001, precision=6,
        subtype='ANGLE'
    )
}


class XRAY_OT_change_action_bake_settings(bpy.types.Operator):
    bl_idname = 'io_scene_xray.change_action_bake_settings'
    bl_label = 'Change Action Bake Settings'

    if not version_utils.IS_28:
        for prop_name, prop_value in change_action_bake_settings_props.items():
            exec('{0} = change_action_bake_settings_props.get("{0}")'.format(prop_name))

    def draw(self, context):
        layout = self.layout
        layout.label(text='Mode:')
        layout.prop(self, 'change_mode', expand=True)
        # auto bake mode
        layout.prop(self, 'change_auto_bake_mode')
        row = layout.row()
        row.active = self.change_auto_bake_mode
        row.prop(self, 'auto_bake_mode', expand=True)
        # custom thresholds
        layout.prop(self, 'change_use_custom_thresholds')
        row = layout.row()
        row.active = self.change_use_custom_thresholds
        row.prop(self, 'use_custom_threshold', toggle=True)
        # location
        layout.prop(self, 'change_location_threshold')
        row = layout.row()
        row.active = self.change_location_threshold
        row.prop(self, 'value_location_threshold')
        # rotation
        layout.prop(self, 'change_rotation_threshold')
        row = layout.row()
        row.active = self.change_rotation_threshold
        row.prop(self, 'value_rotation_threshold')

    def execute(self, context):
        actions = set()
        if self.change_mode == 'active':
            obj = context.object
            if obj:
                for motion in obj.xray.motions_collection:
                    action = bpy.data.actions.get(motion.name)
                    if action:
                        actions.add(action)
        elif self.change_mode == 'selected':
            for obj in context.selected_objects:
                for motion in obj.xray.motions_collection:
                    action = bpy.data.actions.get(motion.name)
                    if action:
                        actions.add(action)
        elif self.change_mode == 'all':
            for action in bpy.data.actions:
                actions.add(action)
        for action in actions:
            xray = action.xray
            # mode
            if self.change_auto_bake_mode:
                xray.autobake = self.auto_bake_mode
            # custom thresholds
            if self.change_use_custom_thresholds:
                xray.autobake_custom_refine = self.use_custom_threshold
            # location
            if self.change_location_threshold:
                xray.autobake_refine_location = self.value_location_threshold
            # rotation
            if self.change_rotation_threshold:
                xray.autobake_refine_rotation = self.value_rotation_threshold
        self.report({'INFO'}, 'Changed {} action(s)'.format(len(actions)))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


classes = (
    XRAY_OT_copy_action_settings,
    XRAY_OT_paste_action_settings,
    XRAY_OT_change_action_bake_settings
)


def register():
    version_utils.assign_props([
        (change_action_bake_settings_props, XRAY_OT_change_action_bake_settings),
    ])
    for operator in classes:
        bpy.utils.register_class(operator)


def unregister():
    for operator in reversed(classes):
        bpy.utils.unregister_class(operator)
