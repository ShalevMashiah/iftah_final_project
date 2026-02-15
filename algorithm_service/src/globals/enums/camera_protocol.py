from enum import Enum

class CameraProtocol(str, Enum):
    ONVIF = "onvif"
    AXIS = "axis"