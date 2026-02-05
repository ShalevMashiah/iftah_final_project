
import zmq

from globals.enums.response_status import ResponseStatus
from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.izmq_client_manager import IZmqClientManager
from model.data_classes.zmq_request import Request
from model.data_classes.zmq_response import Response


class ZmqClientManager(IZmqClientManager):
    def __init__(self, host: str, port: int):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._address = f"{ConstStrings.BASE_TCP_CONNECTION_STRINGS}{host}:{port}"

    def start(self) -> None:
        self._socket.connect(self._address)

    def stop(self) -> None:
        self._socket.close()

    def send_request(self, request: Request) -> Response:
        try:
            self._socket.send_json(request.to_json())
            response = self._socket.recv_json()
            return Response.from_json(response)
        except Exception as e:
            return Response(
                status=ResponseStatus.ERROR,
                data={ConstStrings.ERROR_MESSAGE: str(e)}
            )
