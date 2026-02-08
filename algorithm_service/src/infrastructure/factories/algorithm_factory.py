from typing import Any, Dict

from ..interfaces.algorithms.ialgorithm import IAlgorithm
from model.algorithms.motion_detection import MotionDetectionAlgorithm


class AlgorithmFactory:
    @staticmethod
    def create(algorithm_type: str, config: Dict[str, Any]) -> IAlgorithm:
        if algorithm_type == "motion_detection":
            algo = MotionDetectionAlgorithm()
            algo.setup(config)
            return algo
        raise ValueError(f"Unknown algorithm type: {algorithm_type}")
