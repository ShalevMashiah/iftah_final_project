import os
import cv2
import threading
from typing import List, Optional, Dict
from datetime import datetime

from globals.consts.consts import Consts
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages
from infrastructure.factories.logger_factory import LoggerFactory


class RecordingManager:
    def __init__(self, videos_config: List[Dict]) -> None:
        self._videos_config = videos_config
        self._num_videos = len(videos_config)

        self._recording: List[bool] = [False] * self._num_videos
        self._writers: List[Optional[cv2.VideoWriter]] = [None] * self._num_videos
        self._lock = threading.Lock()

        self._logger = LoggerFactory.get_logger_manager()
        os.makedirs("/app/records", exist_ok=True)

    def is_recording(self, video_index: int) -> bool:
        return self._recording[video_index]

    def start_recording(self, video_index: int) -> str:
        with self._lock:
            if self._recording[video_index]:
                return "Already recording"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/app/records/Camera_name{video_index + 1}_{timestamp}.avi"

            cfg = self._videos_config[video_index]
            width = cfg.get("width", 1280)
            height = cfg.get("height", 720)

            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            writer = cv2.VideoWriter(filename, fourcc, Consts.ALGO_FRAME_RATE, (width, height))

            if not writer.isOpened():
                self._logger.log(ConstStrings.LOG_NAME_ERROR,
                                 f"Failed to start recording for stream {video_index + 1}")
                return "Failed to start recording"

            self._writers[video_index] = writer
            self._recording[video_index] = True

            self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                             f"Recording started for stream {video_index + 1}: {filename}")
            return "Recording started"

    def stop_recording(self, video_index: int) -> str:
        with self._lock:
            if not self._recording[video_index]:
                return "Not recording"

            writer = self._writers[video_index]
            self._writers[video_index] = None
            self._recording[video_index] = False

            try:
                if writer is not None:
                    writer.release()
            except Exception as e:
                self._logger.log(ConstStrings.LOG_NAME_ERROR, f"Error stopping recording: {e}")

            self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                             f"Recording stopped for stream {video_index + 1}")
            return "Recording stopped"

    def write_frame_if_recording(self, video_index: int, frame) -> None:
        with self._lock:
            if not self._recording[video_index]:
                return
            writer = self._writers[video_index]
            if writer is None:
                return

            try:
                writer.write(frame)
            except Exception as e:
                self._logger.log(ConstStrings.LOG_NAME_ERROR, f"Error writing frame: {e}")
