from infrastructure.factories.infrastructure_factory import InfrastructureFactory
from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.iexample_manager import IExampleManager
from infrastructure.interfaces.izmq_server_manager import IZmqServerManager
from model.managers.example_manager import ExampleManager
from infrastructure.interfaces.ilogger_manager import ILoggerManager
from infrastructure.interfaces.managers.ialgorithm_manager import IAlgorithmManager
from model.managers.algorithm_manager import AlgorithmManager
from globals.consts.consts import Consts

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
    def create_algorithm_manager() -> IAlgorithmManager:
        # Configure video sources to read from shared memory
        videos_config = [
            {
                "video_id": 1,
                "width": Consts.ALGO_FRAME_WIDTH,
                "height": Consts.ALGO_FRAME_HEIGHT,
                "algorithm": "motion_detection",
                "algorithm_config": {
                    "min_contour_area": Consts.MOTION_MIN_AREA,
                    "threshold": Consts.MOTION_BG_VAR_THRESHOLD,
                    "history": Consts.MOTION_BG_HISTORY,
                    "detect_shadows": Consts.MOTION_DETECT_SHADOWS,
                    "dilate_iterations": Consts.MOTION_DILATE_ITER,
                    "erode_iterations": 0,
                    "draw_bbox": True
                }
            },
            {
                "video_id": 2,
                "width": Consts.ALGO_FRAME_WIDTH,
                "height": Consts.ALGO_FRAME_HEIGHT,
                "algorithm": "motion_detection",
                "algorithm_config": {
                    "min_contour_area": Consts.MOTION_MIN_AREA,
                    "threshold": Consts.MOTION_BG_VAR_THRESHOLD,
                    "history": Consts.MOTION_BG_HISTORY,
                    "detect_shadows": Consts.MOTION_DETECT_SHADOWS,
                    "dilate_iterations": Consts.MOTION_DILATE_ITER,
                    "erode_iterations": 0,
                    "draw_bbox": True
                }
            },
                        {
                "video_id": 3,
                "width": Consts.ALGO_FRAME_WIDTH,
                "height": Consts.ALGO_FRAME_HEIGHT,
                "algorithm": "motion_detection",
                "algorithm_config": {
                    "min_contour_area": Consts.MOTION_MIN_AREA,
                    "threshold": Consts.MOTION_BG_VAR_THRESHOLD,
                    "history": Consts.MOTION_BG_HISTORY,
                    "detect_shadows": Consts.MOTION_DETECT_SHADOWS,
                    "dilate_iterations": Consts.MOTION_DILATE_ITER,
                    "erode_iterations": 0,
                    "draw_bbox": True
                }
            }
        ]
        
        algorithm_manager = AlgorithmManager(videos_config)
        return algorithm_manager

    @staticmethod
    def create_all():
        ManagerFactory.create_algorithm_manager().start()
