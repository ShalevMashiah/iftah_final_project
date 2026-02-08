import time
import os
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
        pipeline = (
            f"shmsrc socket-path={self._shm_path} is-live=true do-timestamp=true ! "
            f"video/x-raw,format=I420,width={self._width},height={self._height},framerate=30/1 ! "
            f"videoconvert ! video/x-raw,format=BGR ! "
            f"appsink drop=true sync=false"
        )

        max_wait_seconds = 5
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
        max_wait_seconds = 10
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
