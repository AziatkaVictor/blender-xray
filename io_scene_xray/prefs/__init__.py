from . import ops, props, utils


modules = (ops, props)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()