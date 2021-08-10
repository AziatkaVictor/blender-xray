# standart modules
import math
import os

# blender modules
import bpy

# addon modules
from .. import context as xray_context, utils
from ..xray_io import ChunkedReader, PackedReader
from .fmt import Chunks
from ..xray_envelope import import_envelope
from ..version_utils import link_object, IS_28
from ..log import warn, with_context


DISPLAY_SIZE = 0.5


class ImportAnmContext(xray_context.ImportContext):
    def __init__(self):
        xray_context.ImportContext.__init__(self)
        self.camera_animation = None


@with_context('import-anm-path')
def _import(fpath, creader, context):
    warn_list = []
    for cid, data in creader:
        if cid == Chunks.MAIN:
            preader = PackedReader(data)
            name = preader.gets()
            _fr = preader.getf('<2I')
            fps, ver = preader.getf('<fH')
            if ver != 5:
                raise utils.AppError(
                    'File "{}" has unsupported format version: {}'.format(
                        fpath, ver
                    )
                )
            if not name:
                name = os.path.basename(fpath)
            bpy_obj = bpy.data.objects.new(name, None)
            bpy_obj.rotation_mode = 'YXZ'
            if context.camera_animation:
                bpy_cam = bpy.data.objects.new(
                    name + '.camera',
                    bpy.data.cameras.new(name)
                )
                bpy_cam.parent = bpy_obj
                bpy_cam.rotation_euler = (math.pi / 2, 0, 0)
                link_object(bpy_cam)
            else:
                display_type = 'SPHERE'
                if IS_28:
                    bpy_obj.empty_display_type = display_type
                else:
                    bpy_obj.empty_draw_type = display_type
            if IS_28:
                bpy_obj.empty_display_size = DISPLAY_SIZE
            else:
                bpy_obj.empty_draw_size = DISPLAY_SIZE
            link_object(bpy_obj)
            action = bpy.data.actions.new(name=name)
            action.xray.fps = fps
            bpy_obj.animation_data_create().action = action
            fcs = (
                action.fcurves.new('location', index=0, action_group=name),
                action.fcurves.new('location', index=1, action_group=name),
                action.fcurves.new('location', index=2, action_group=name),
                action.fcurves.new('rotation_euler', index=0, action_group=name),
                action.fcurves.new('rotation_euler', index=1, action_group=name),
                action.fcurves.new('rotation_euler', index=2, action_group=name)
            )
            converted_warrning = False
            unique_shapes = set()
            for i in range(6):
                fcurve = fcs[(0, 2, 1, 5, 3, 4)[i]]
                koef = (1, 1, 1, -1, -1, -1)[i]
                use_interpolate = import_envelope(
                    preader, fcurve, fps, koef, name, warn_list, unique_shapes
                )
                if use_interpolate:
                    converted_warrning = True
            if converted_warrning:
                warn(
                    'motion shapes converted to LINEAR',
                    anm_name=name, shapes=unique_shapes
                )
    for (shapes, replacement, name) in set(warn_list):
        keys_count = warn_list.count((shapes, replacement, name))
        warn(
            'unsupported shapes are found, and will be replaced',
            shapes=shapes,
            replacement=replacement,
            filename=name,
            keys_count=keys_count
        )


def import_file(fpath, context):
    data = utils.read_file(fpath)
    chunked_reader = ChunkedReader(data)
    _import(fpath, chunked_reader, context)
