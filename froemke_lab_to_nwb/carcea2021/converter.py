from neuroconv.datainterfaces import BlackrockRecordingInterface, BlackrockSortingInterface
from neuroconv import NWBConverter
#from neuroconv.datainterfaces.behavior.audio.audiointerface import AudioInterface

from .behavior_interface import PhotometryBehaviorDataInterface, EcephysBehaviorDataInterface
from .photometry_interface import PhotometryInterface


class Carcea2021EphysConverter(NWBConverter):
    data_interface_classes = dict(
        recording=BlackrockRecordingInterface,
        sorting=BlackrockSortingInterface,
        #audio=AudioInterface,
        behavior=EcephysBehaviorDataInterface,
    )


class Carcea2021OphysConverter(NWBConverter):
    data_interface_classes = dict(
        photometry=PhotometryInterface,
        behavior=PhotometryBehaviorDataInterface,
    )


