# standart modules
import os

# blender modules
import bmesh, bpy

# addon modules
from .. import xray_io, utils, plugin_prefs, prefs
from . import fmt, create


def get_cform_material(gamemtl_name, mat_name, suppress_shadows, suppress_wm):
    for bpy_mat in bpy.data.materials:
        if bpy_mat.name.startswith(mat_name):
            if bpy_mat.xray.gamemtl == gamemtl_name:
                if bpy_mat.xray.suppress_shadows == suppress_shadows:
                    if bpy_mat.xray.suppress_wm == suppress_wm:
                        return bpy_mat


def import_cform(context, data, level):
    packed_reader = xray_io.PackedReader(data)
    version = packed_reader.getf('<I')[0]
    if not version in fmt.CFORM_SUPPORT_VERSIONS:
        raise utils.AppError('Unsupported cform version: {}'.format(version))
    verts_count = packed_reader.getf('<I')[0]
    tris_count = packed_reader.getf('<I')[0]
    bbox_min = packed_reader.getf('<3f')
    bbox_max = packed_reader.getf('<3f')
    verts = []
    for vert_index in range(verts_count):
        vert_co_x, vert_co_y, vert_co_z = packed_reader.getf('<3f')
        verts.append((vert_co_x, vert_co_z, vert_co_y))
    preferences = prefs.utils.get_preferences()
    gamemtl_file_path = preferences.gamemtl_file_auto
    if os.path.exists(gamemtl_file_path):
        with open(gamemtl_file_path, 'rb') as gamemtl_file:
            gamemtl_data = gamemtl_file.read()
    else:
        gamemtl_data = b''
    game_mtl_names = {}
    for game_mtl_name, _, game_mtl_id in utils.parse_gamemtl(gamemtl_data):
        game_mtl_names[game_mtl_id] = game_mtl_name
    if version == fmt.CFORM_VERSION_4:
        read_code = ''
        read_code += 'material, sector_index = packed_reader.getf("<2H")\n'
        read_code += 'globals()["sector_index"] = sector_index\n'
        read_code += 'globals()["material_id"] = material & 0x3fff\n'    # 14 bit
        read_code += 'globals()["suppress_shadows"] = bool((material & 0x4000) >> 14)\n'    # 15 bit
        read_code += 'globals()["suppress_wm"] = bool((material & 0x8000) >> 15)\n'    # 16 bit
    elif version in (fmt.CFORM_VERSION_3, fmt.CFORM_VERSION_2):
        read_code = ''
        read_code += 'packed_reader.skip(12 + 2)\n'    # ?
        read_code += 'globals()["sector_index"] = packed_reader.getf("<H")[0]\n'
        read_code += 'globals()["material_id"] = packed_reader.getf("<I")[0]\n'
        read_code += 'globals()["suppress_shadows"] = False\n'
        read_code += 'globals()["suppress_wm"] = False\n'
    sectors = {}
    sectors_verts = {}
    tris = []
    unique_sectors_materials = {}
    unique_materials = set()
    for tris_index in range(tris_count):
        vert_1, vert_2, vert_3 = packed_reader.getf('<3I')
        exec(read_code)
        global material_id, sector_index, suppress_shadows, suppress_wm
        tris.append((vert_1, vert_2, vert_3, material_id, suppress_shadows, suppress_wm))
        unique_materials.add((material_id, suppress_shadows, suppress_wm))
        if sectors.get(sector_index):
            sectors[sector_index].append(tris_index)
            sectors_verts[sector_index].update((vert_1, vert_2, vert_3))
            unique_sectors_materials[sector_index].add((material_id, suppress_shadows, suppress_wm))
        else:
            sectors[sector_index] = [tris_index, ]
            sectors_verts[sector_index] = set((vert_1, vert_2, vert_3))
            unique_sectors_materials[sector_index] = set(((material_id, suppress_shadows, suppress_wm), ))
    for sector_index, sector_materials in unique_sectors_materials.items():
        sector_materials = list(sector_materials)
        sector_materials.sort()
        unique_sectors_materials[sector_index] = sector_materials
    bpy_materials = {}
    for material_id, suppress_shadows, suppress_wm in unique_materials:
        game_mtl = game_mtl_names.get(material_id, str(material_id))
        material_name = '{0}_{1}_{2}'.format(game_mtl, int(suppress_shadows), int(suppress_wm))
        material = get_cform_material(game_mtl, material_name, suppress_shadows, suppress_wm)
        if not material:
            material = bpy.data.materials.new(material_name)
            material.xray.version = context.version
            material.xray.eshader = 'default'
            material.xray.cshader = 'default'
            material.xray.gamemtl = game_mtl
            material.xray.suppress_shadows = suppress_shadows
            material.xray.suppress_wm = suppress_wm
        bpy_materials[material_id] = material
    for sector_index, triangles in sectors.items():
        sector_verts = sectors_verts[sector_index]
        sector_verts = list(sector_verts)
        sector_verts.sort()
        bm = bmesh.new()
        current_vertex_index = 0
        remap_verts = {}
        for vert_index in sector_verts:
            vert_co = verts[vert_index]
            bm.verts.new(vert_co)
            remap_verts[vert_index] = current_vertex_index
            current_vertex_index += 1
        vertices_count = current_vertex_index
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        obj_name = 'cform_{:0>3}'.format(sector_index)
        bpy_mesh = bpy.data.meshes.new(obj_name)
        for material_id, suppress_shadows, suppress_wm in unique_sectors_materials[sector_index]:
            bpy_material = bpy_materials[material_id]
            bpy_mesh.materials.append(bpy_material)
        two_sided_tris = []
        two_sided_verts = set()
        for tris_index in triangles:
            vert_1, vert_2, vert_3, material_id, suppress_shadows, suppress_wm = tris[tris_index]
            try:
                face = bm.faces.new((
                    bm.verts[remap_verts[vert_1]],
                    bm.verts[remap_verts[vert_3]],
                    bm.verts[remap_verts[vert_2]]
                ))
                face.smooth = True
                material = unique_sectors_materials[sector_index].index((material_id, suppress_shadows, suppress_wm))
                face.material_index = material
            except ValueError:
                face = None
                two_sided_tris.append((vert_1, vert_2, vert_3, material_id, suppress_shadows, suppress_wm))
                two_sided_verts.update((vert_1, vert_2, vert_3))
        current_vertex_index = vertices_count
        remap_vertices = {}
        for vertex_index in sorted(list(two_sided_verts)):
            vert_co = verts[vertex_index]
            bm.verts.new(vert_co)
            remap_vertices[vertex_index] = current_vertex_index
            current_vertex_index += 1
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        for vert_1, vert_2, vert_3, material_id, suppress_shadows, suppress_wm in two_sided_tris:
            try:
                face = bm.faces.new((
                    bm.verts[remap_vertices[vert_1]],
                    bm.verts[remap_vertices[vert_3]],
                    bm.verts[remap_vertices[vert_2]]
                ))
                face.smooth = True
                material = unique_sectors_materials[sector_index].index((material_id, suppress_shadows, suppress_wm))
                face.material_index = material
            except ValueError:    # face already exists
                pass
        bm.faces.ensure_lookup_table()
        bm.faces.index_update()
        bm.normal_update()
        bm.to_mesh(bpy_mesh)
        bpy_obj = bpy.data.objects.new(obj_name, bpy_mesh)
        bpy_obj.parent = level.sectors_objects[sector_index]
        bpy_obj.xray.is_level = True
        bpy_obj.xray.level.object_type = 'CFORM'
        level.collections[create.LEVEL_CFORM_COLLECTION_NAME].objects.link(bpy_obj)


def import_main(context, level, data=None):
    if level.xrlc_version >= fmt.VERSION_10:
        cform_path = os.path.join(level.path, 'level.cform')
        with open(cform_path, 'rb') as file:
            data = file.read()
    import_cform(context, data, level)
