from .actx_slice import convert_all_actx
from .in_vivo import convert_all_in_vivo
from .whole_cell_oxt import convert_all_oxt_and_control
from .convert_ophys import convert_all_ophys
from .convert_behavior import convert_all_behavior


def convert_all():
    convert_all_ophys()
    convert_all_actx()
    convert_all_in_vivo()
    convert_all_oxt_and_control()
    convert_all_behavior()

