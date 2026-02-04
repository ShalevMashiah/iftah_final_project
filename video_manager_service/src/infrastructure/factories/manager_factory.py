from infrastructure.factories.infrastructure_factory import InfrastructureFactory
from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.iexample_manager import IExampleManager
from infrastructure.interfaces.izmq_server_manager import IZmqServerManager
from model.managers.example_manager import ExampleManager
from infrastructure.interfaces.ilogger_manager import ILoggerManager


class ManagerFactory:
    @staticmethod
    def create_example_manager() -> IExampleManager:
        config_manager = InfrastructureFactory.create_config_manager(
            ConstStrings.GLOBAL_CONFIG_PATH)
        return ExampleManager(config_manager, InfrastructureFactory.create_kafka_manager(config_manager))

    @staticmethod
    def create_example_zmq_manager() -> IZmqServerManager:
        return InfrastructureFactory.create_zmq_server_manager()

    @staticmethod
    def create_all():
        ManagerFactory.create_example_manager()
        ManagerFactory.create_example_zmq_manager()
