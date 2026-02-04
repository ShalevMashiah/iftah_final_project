import threading
import time
from typing import List
import zmq

from globals.enums.response_status import ResponseStatus
from globals.consts.consts import Consts
from globals.consts.const_strings import ConstStrings
from model.data_classes.zmq_request import Request
from infrastructure.interfaces.izmq_server_manager import IZmqServerManager
from model.data_classes.zmq_response import Response
from infrastructure.api.routers.base_router import BaseRouter
from infrastructure.interfaces.iapi_router import IApiRouter
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.logger_messages import LoggerMessages


class ZmqServerManager(IZmqServerManager):
    def __init__(self, host: str, port: int, routers: List[IApiRouter]):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._address = f"{ConstStrings.BASE_TCP_CONNECTION_STRINGS}{host}:{port}"
        self._is_running = False
        self._server_working_thread = None
        self._routers_dict = dict[str, IApiRouter]()
        self._logger = LoggerFactory.get_logger_manager()
        self._include_routers(routers)

    def start(self) -> None:
        self._socket.bind(self._address)
        self._is_running = True
        self._server_working_thread = threading.Thread(
            target=self._server_working_handle, daemon=True)
        self._server_working_thread.start()
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.ZMQ_SERVER_BOUND_TO_ADDRESS.format(self._address))

    def stop(self) -> None:
        self._is_running = False
        if self._server_working_thread:
            self._server_working_thread.join()
        self._socket.close()
        self._context.term()
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.ZMQ_SERVER_STOPPED)

    def _server_working_handle(self) -> None:
        while self._is_running:
            try:
                request_json = self._socket.recv_json()
                request = Request.from_json(request_json)
            except zmq.Again:
                time.sleep(Consts.ZMQ_SERVER_LOOP_DURATION)
                continue

            response = self._handle_request(request)
            self._socket.send_json(response.to_json())

    def _handle_request(self, request: Request) -> Response:
        resource = request.resource
        operation = request.operation
        data = request.data
        if resource in self._routers_dict:
            route = self._routers_dict[resource]
            return route.handle_operation(operation, data)
        else:
            return Response(
                status=ResponseStatus.ERROR,
                data={
                    ConstStrings.ERROR_MESSAGE: ConstStrings.UNKNOWN_RESOURCE_ERROR_MESSAGE}
            )

    def _include_routers(self, routers: List[IApiRouter]) -> None:
        for router in routers:
            self._routers_dict[router.resource] = router
