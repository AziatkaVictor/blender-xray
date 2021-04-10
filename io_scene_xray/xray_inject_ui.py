from .ops import (
    fake_bones, verify_uv, verify_uv_ui, joint_limits, action_utils,
    armature_utils, transform_utils, xray_camera
)
from . import registry
from .ui import (
    obj, mesh, material, armature, bone, action,
    scene, view3d, collapsible, edit_helper
)


registry.module_requires(__name__, [
    collapsible,
    fake_bones,
    armature_utils,
    joint_limits,
    transform_utils,
    xray_camera,
    verify_uv.XRayVerifyUVOperator,
    verify_uv_ui.XRAY_PT_VerifyToolsPanel,
    action_utils.XRayCopyActionSettingsOperator,
    action_utils.XRayPasteActionSettingsOperator,
    obj,
    mesh,
    material,
    armature,
    bone,
    action, 
    scene,
    view3d,
    edit_helper
])
