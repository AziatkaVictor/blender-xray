# addon modules
from . import connect_bones
from . import create_ik
from . import remove_rig


modules = (
    connect_bones,
    create_ik,
    remove_rig
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
