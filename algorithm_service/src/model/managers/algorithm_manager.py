import os
import cv2
import threading
import time
from queue import Queue, Empty
from typing import List, Dict

from globals.consts.consts import Consts
from infrastructure.interfaces.managers.ialgorithm_manager import IAlgorithmManager
from infrastructure.factories.handler_factory import HandlerFactory
from infrastructure.factories.algorithm_factory import AlgorithmFactory
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages


class AlgorithmManager(IAlgorithmManager):

    def __init__(self, videos_config: List[Dict]) -> None:
        self._videos_config = videos_config
        self._num_videos = len(videos_config)

        self._readers = []
        self._algorithms = []
        self._process_threads = []
        self._running = True

        self._logger = LoggerFactory.get_logger_manager()
        self._logger.log(ConstStrings.LOG_NAME_DEBUG, LoggerMessages.MOTION_STARTING)

        self._enable_imshow = self._require_env(ConstStrings.ENABLE_IMSHOW_ENV) == "1"
        self._display = self._require_env(ConstStrings.DISPLAY_ENV)

        self._queue_size = int(self._require_env("ALGO_QUEUE_SIZE"))
        self._max_none_count = int(self._require_env("ALGO_MAX_NONE_COUNT"))
        self._none_sleep_sec = float(self._require_env("ALGO_NONE_SLEEP_SEC"))
        self._render_sleep_sec = float(self._require_env("ALGO_RENDER_SLEEP_SEC"))
        self._render_fps = int(self._require_env("ALGO_RENDER_FPS"))
        self._window_prefix = self._require_env("ALGO_WINDOW_PREFIX")

        self._output_dir = self._require_env("ALGO_OUTPUT_DIR")
        self._save_jpeg = self._require_env("ALGO_SAVE_JPEG") == "1"
        self._jpeg_quality = int(self._require_env("ALGO_JPEG_QUALITY"))
        self._jpeg_name_pattern = self._require_env("ALGO_JPEG_NAME_PATTERN")

        if self._save_jpeg:
            os.makedirs(self._output_dir)

        self._frame_queues = [
            Queue(maxsize=self._queue_size)
            for _ in range(self._num_videos)
        ]

        self._init_readers()
        self._init_algorithms()

    def _require_env(self, key: str) -> str:
        value = os.environ.get(key)
        if value is None:
            raise RuntimeError(f"Missing required ENV variable: {key}")
        return value

    def start(self) -> None:
        for i in range(self._num_videos):
            thread = threading.Thread(
                target=self._process_frames_worker,
                args=(i,),
                daemon=True
            )
            self._process_threads.append(thread)
            thread.start()

        while self._running:
            if self._enable_imshow:
                self._render_frames_main_thread()
            else:
                time.sleep(self._render_sleep_sec)

    def stop(self) -> None:
        self._running = False

        for reader in self._readers:
            reader.release()

        for algo in self._algorithms:
            if algo:
                algo.release()

        for thread in self._process_threads:
            thread.join()

        self._logger.log(ConstStrings.LOG_NAME_DEBUG, LoggerMessages.ALGORITHM_MANAGER_STOPPED)

    def _init_readers(self) -> None:
        for video in self._videos_config:
            reader = HandlerFactory.create_shm_reader_handler(
                video["video_id"],
                video["width"],
                video["height"]
            )
            self._readers.append(reader)
            reader.start()

    def _init_algorithms(self) -> None:
        for video in self._videos_config:
            algo = AlgorithmFactory.create(
                video["algorithm"],
                video["algorithm_config"]
            )
            self._algorithms.append(algo)

    def _process_frames_worker(self, video_index: int) -> None:
        reader = self._readers[video_index]
        algo = self._algorithms[video_index]
        q = self._frame_queues[video_index]

        frame_count = 0
        consecutive_none_count = 0

        while self._running:
            frame = reader.read_frame()

            if frame is None:
                consecutive_none_count += 1
                if consecutive_none_count >= self._max_none_count:
                    self._running = False
                    break
                time.sleep(self._none_sleep_sec)
                continue

            consecutive_none_count = 0
            frame_count += 1

            if algo:
                frame = algo.process(frame)

            if self._save_jpeg:
                filename = self._jpeg_name_pattern.format(index=video_index + 1)
                output_path = os.path.join(self._output_dir, filename)
                cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, self._jpeg_quality])

            if q.full():
                try:
                    q.get_nowait()
                except Empty:
                    pass

            try:
                q.put_nowait(frame)
            except Exception:
                pass

    def _render_frames_main_thread(self) -> None:
        for i in range(self._num_videos):
            q = self._frame_queues[i]
            frame = None

            try:
                while True:
                    frame = q.get_nowait()
            except Empty:
                pass

            if frame is not None:
                cv2.imshow(f"{self._window_prefix} {i + 1}", frame)

        if self._enable_imshow:
            cv2.waitKey(int(1000 / self._render_fps))
