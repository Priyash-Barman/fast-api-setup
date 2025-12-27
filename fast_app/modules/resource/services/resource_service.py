from fast_app.defaults.permission_enums import Action, Resource
from fast_app.utils.common_utils import enum_to_dict


def get_resources():
    return enum_to_dict(Resource)

def get_actions():
    return enum_to_dict(Action)