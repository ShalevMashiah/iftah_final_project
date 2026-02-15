from dataclasses import dataclass
from globals.enums.camera_protocol import CameraProtocol

@dataclass
class CameraConfiguration:
    camera_id: int
    camera_ip: str
    camera_port: str
    camera_username: str
    camera_password: str
    camera_protocol: CameraProtocol

    @property
    def camera_protocol(self) -> CameraProtocol:
        return self._camera_protocol

    @camera_protocol.setter
    def camera_protocol(self, value: str) -> None:
        self._camera_protocol = CameraProtocol(value)
