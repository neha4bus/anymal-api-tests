# Import all modules without having to list them explicitly.

import pkgutil
from google.protobuf import reflection
from google.protobuf.internal import enum_type_wrapper

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    for name in dir(module):
        obj = getattr(module, name)
        if type(obj) in [reflection.GeneratedProtocolMessageType, enum_type_wrapper.EnumTypeWrapper]:
            globals()[name] = obj
