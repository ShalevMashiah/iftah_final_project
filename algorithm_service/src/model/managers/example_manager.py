import time
import threading
import json

from infrastructure.interfaces.iexample_manager import IExampleManager
from infrastructure.interfaces.iconfig_manager import IConfigManager
from infrastructure.interfaces.ikafka_manager import IKafkaManager
from globals.consts.const_strings import ConstStrings
from globals.consts.consts import Consts
from globals.consts.logger_messages import LoggerMessages
from infrastructure.factories.logger_factory import LoggerFactory


class ExampleManager(IExampleManager):
    def __init__(self, config_manager: IConfigManager, kafka_manager: IKafkaManager) -> None:
        super().__init__()
        self._config_manager = config_manager
        self._kafka_manager = kafka_manager
        self._example_topic_consumer = ConstStrings.EXAMPLE_TOPIC
        self._logger = LoggerFactory.get_logger_manager()
        self._init_threading()
        self._init_consumers()

    def do_something(self) -> None:
        pass

    def _init_threading(self) -> None:
        self._message_produce_threading = threading.Thread(
            target=self._produce_kafka_message
        )
        self._message_produce_threading.start()

    def _init_consumers(self) -> None:
        self._kafka_manager.start_consuming(
            self._example_topic_consumer, self._print_consumer)

    def _produce_kafka_message(self) -> None:
        while (True):
            time.sleep(Consts.SEND_MESSAGE_DURATION)
            self._kafka_manager.send_message(
                ConstStrings.EXAMPLE_TOPIC, ConstStrings.EXAMPLE_MESSAGE)

    def _print_consumer(self, msg: str) -> None:
        self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                         LoggerMessages.EXAMPLE_PRINT_CONSUMER_MSG.format(str(msg)))
