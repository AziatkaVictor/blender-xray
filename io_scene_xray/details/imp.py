import os

import bpy

from . import fmt, read
from . import utils as det_utils
from .. import utils, xray_io
from ..version_utils import link_object


def _import(fpath, context, chunked_reader):

    has_header = False
    has_meshes = False
    has_slots = False

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == 0x0 and not chunk_data:    # bad file (build 1233)
            break

        if chunk_id == fmt.Chunks.HEADER:

            if len(chunk_data) != fmt.HEADER_SIZE:
                raise utils.AppError(
                    'bad details file. HEADER chunk size not equal 24'
                    )

            header = read.read_header(xray_io.PackedReader(chunk_data))

            if header.format_version not in fmt.SUPPORT_FORMAT_VERSIONS:
                raise utils.AppError(
                    'unssuported details format version: {}'.format(
                        header.format_version
                        )
                    )

            has_header = True

        elif chunk_id == fmt.Chunks.MESHES:
            cr_meshes = xray_io.ChunkedReader(chunk_data)
            has_meshes = True

        elif chunk_id == fmt.Chunks.SLOTS:
            if context.load_slots:
                pr_slots = xray_io.PackedReader(chunk_data)
            has_slots = True

    del chunked_reader

    if not has_header:
        raise utils.AppError('bad details file. Cannot find HEADER chunk')
    if not has_meshes:
        raise utils.AppError('bad details file. Cannot find MESHES chunk')
    if not has_slots:
        raise utils.AppError('bad details file. Cannot find SLOTS chunk')

    base_name = os.path.basename(fpath.lower())
    color_indices = det_utils.generate_color_indices()

    meshes_obj = read.read_details_meshes(
        fpath, base_name, context, cr_meshes, color_indices, header
        )

    del cr_meshes
    del has_header, has_meshes, has_slots

    if context.load_slots:

        root_obj = bpy.data.objects.new(base_name, None)
        root_obj.xray.is_details = True
        link_object(root_obj)

        meshes_obj.parent = root_obj

        slots_base_object, slots_top_object = read.read_details_slots(
            base_name, context, pr_slots, header, color_indices, root_obj
            )

        del pr_slots

        slots_base_object.parent = root_obj
        slots_top_object.parent = root_obj

        slots = root_obj.xray.detail.slots

        slots.meshes_object = meshes_obj.name
        slots.slots_base_object = slots_base_object.name
        slots.slots_top_object = slots_top_object.name


def import_file(fpath, context):
    data = utils.read_file(fpath)
    chunked_reader = xray_io.ChunkedReader(data)
    _import(fpath, context, chunked_reader)
