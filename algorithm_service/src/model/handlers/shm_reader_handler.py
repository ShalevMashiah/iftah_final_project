import time
import os
import logging
import cv2
import numpy as np
from infrastructure.interfaces.handlers.ishm_reader_handler import IShmReaderHandler
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.consts import Consts


class ShmReaderHandler(IShmReaderHandler):
    def __init__(self, video_id: int, width: int = Consts.ALGO_FRAME_WIDTH, height: int = Consts.ALGO_FRAME_HEIGHT):
        self._video_id = video_id
        self._width = width
        self._height = height
        self._shm_path = ConstStrings.SHARED_MEMORY_CAM_PATH.format(camera_id=video_id)
        self._cap = None
        self._logger = LoggerFactory.get_logger_manager()

    def start(self) -> None:
        # Try GStreamer shmsrc first (caps must match writer I420 size)
        pipeline = ConstStrings.SHARED_MEMORY_READER_PIPELINE.format(
            shared_memory_path=self._shm_path,
            frame_width=self._width,
            frame_height=self._height,
            frame_rate=Consts.ALGO_FRAME_RATE,
        )

        max_wait_seconds = Consts.SHM_OPEN_GST_WAIT_SECONDS
        for i in range(max_wait_seconds):
            self._cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            if self._cap.isOpened():
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    f"Opened shared memory reader for video {self._video_id} (GStreamer shmsrc)"
                )
                return

            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
            time.sleep(1)

        # Fallback: try reading from .avi file (when GStreamer pipeline fails)
        self._logger.log(
            ConstStrings.LOG_NAME_DEBUG,
            f"GStreamer shmsrc failed, trying file fallback: {self._shm_path}.avi"
        )
        
        avi_path = f"{self._shm_path}.avi"
        max_wait_seconds = Consts.SHM_OPEN_AVI_WAIT_SECONDS
        for i in range(max_wait_seconds):
            if os.path.exists(avi_path):
                self._cap = cv2.VideoCapture(avi_path)
                if self._cap.isOpened():
                    self._logger.log(
                        ConstStrings.LOG_NAME_DEBUG,
                        f"Opened shared memory reader for video {self._video_id} (file fallback)"
                    )
                    return
            time.sleep(1)

        self._logger.log(
            ConstStrings.LOG_NAME_ERROR,
            f"Cannot open shm stream or file after waiting: {self._shm_path}",
            level=logging.ERROR,
        )
        raise TimeoutError(f"Cannot open shm stream or file after waiting: {self._shm_path}")

    def read_frame(self) -> np.ndarray:
        if not self._cap or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        return frame if ret else None

    def release(self) -> None:
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
