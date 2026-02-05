import os
from typing import List

from infrastructure.interfaces.ikafka_manager import IKafkaManager
from infrastructure.events.kafka_manager import KafkaManager
from infrastructure.interfaces.ievent_manager import IEventManager
from infrastructure.events.event_manager import EventManager
from infrastructure.config.xml_config_manager import XMLConfigManager
from infrastructure.interfaces.iconfig_manager import IConfigManager
from globals.consts.const_strings import ConstStrings
from infrastructure.factories.api_factory import ApiFactory
from infrastructure.interfaces.izmq_server_manager import IZmqServerManager
from infrastructure.events.zmq_server_manager import ZmqServerManager
from infrastructure.interfaces.ilogger_manager import ILoggerManager
from infrastructure.logger.logger_manager import LoggerManager


class InfrastructureFactory:
    event_manager: IEventManager = None

    @staticmethod
    def create_config_manager(config_path: str) -> IConfigManager:
        return XMLConfigManager(config_path)

    @staticmethod
    def create_kafka_manager(config_manager: IConfigManager) -> IKafkaManager:
        return KafkaManager(config_manager)

    @staticmethod
    def create_event_manager() -> IEventManager:
        if InfrastructureFactory.event_manager is None:
            InfrastructureFactory.event_manager = EventManager()
        return InfrastructureFactory.event_manager

    @staticmethod
    def create_zmq_server_manager() -> IZmqServerManager:
        host = os.getenv(ConstStrings.ZMQ_SERVER_HOST)
        port = os.getenv(ConstStrings.ZMQ_SERVER_PORT)
        routers = ApiFactory.create_routers()
        return ZmqServerManager(host, port, routers).start()
