import json
import threading
from typing import Callable
from kafka import KafkaProducer, KafkaConsumer
from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.ikafka_manager import IKafkaManager
from infrastructure.interfaces.iconfig_manager import IConfigManager
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.logger_messages import LoggerMessages


class KafkaManager(IKafkaManager):
    def __init__(self, config_manager: IConfigManager) -> None:
        self._topic = None
        self._producer = None
        self._consumers = {}
        self._bootstrap_servers = None
        self._config_manager = config_manager
        self._logger = LoggerFactory.get_logger_manager()
        self._init_data_from_configuration()
        self._init_kafka_producer()

    def send_message(self, topic: str, msg: str) -> None:
        if self._config_manager.exists(topic):
            self._producer.send(topic, value=msg)
            self._producer.flush()

    def start_consuming(self, topic: str, callback: Callable) -> None:
        if topic in self._consumers:
            self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                             LoggerMessages.KAFKA_TOPIC_ALREADY_CONSUMING.format(topic))
            return

        consumer = self._init_kafka_consumer(topic)
        if consumer:
            self._consumers[topic] = consumer
            thread = threading.Thread(
                target=self._consume, args=(consumer, callback))
            thread.daemon = True
            thread.start()

    def _init_data_from_configuration(self) -> None:
        self._bootstrap_servers = self._config_manager.get(
            ConstStrings.KAFKA_ROOT_CONFIGURATION_NAME,
            ConstStrings.BOOTSTRAP_SERVERS_ROOT
        )

    def _init_kafka_producer(self) -> None:
        self._producer = KafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(
                v).encode(ConstStrings.ENCODE_FORMAT)
        )

    def _init_kafka_consumer(self, topic: str):
        if not self._config_manager.exists(topic):
            self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                             LoggerMessages.KAFKA_TOPIC_NOT_EXIST)
            return None
        return KafkaConsumer(
            topic,
            bootstrap_servers=self._bootstrap_servers,
            auto_offset_reset=ConstStrings.AUTO_OFFSET_RESET,
            enable_auto_commit=True,
            group_id=ConstStrings.GROUP_ID,
            value_deserializer=lambda m: json.loads(
                m.decode(ConstStrings.DECODE_FORMAT))
        )

    def _consume(self, consumer: KafkaConsumer, callback: Callable) -> None:
        for message in consumer:
            consumer.commit()
            callback(message.value)
