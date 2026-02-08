import os
import cv2
from globals.consts.consts import Consts
import threading
import time
from queue import Queue, Empty
from typing import List, Dict

from infrastructure.interfaces.managers.ialgorithm_manager import IAlgorithmManager
from infrastructure.factories.handler_factory import HandlerFactory
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.const_strings import ConstStrings
from globals.consts.logger_messages import LoggerMessages


class AlgorithmManager(IAlgorithmManager):
    def __init__(self, videos_config: List[Dict]) -> None:
        self._videos_config = videos_config
        self._readers = []
        self._num_videos = len(videos_config)

        self._process_threads = []
        self._running = True
        self._logger = LoggerFactory.get_logger_manager()
        self._bg_subtractors = [
                cv2.createBackgroundSubtractorMOG2(
                    history=Consts.MOTION_BG_HISTORY,
                    varThreshold=Consts.MOTION_BG_VAR_THRESHOLD,
                    detectShadows=Consts.MOTION_DETECT_SHADOWS
            )
            for _ in range(self._num_videos)
        ]
        
        self._logger.log(ConstStrings.LOG_NAME_DEBUG, LoggerMessages.MOTION_STARTING)
        
        # UI settings
        self._enable_imshow = os.environ.get(ConstStrings.ENABLE_IMSHOW_ENV, "0") == "1"
        self._display = os.environ.get(ConstStrings.DISPLAY_ENV, "")
        if self._enable_imshow and not self._display:
            self._logger.log(
                ConstStrings.LOG_NAME_DEBUG,
                "ENABLE_IMSHOW=1 but DISPLAY is empty. Disabling imshow to avoid crash."
            )
            self._enable_imshow = False

        # One queue per video - holds latest frames
        self._frame_queues: List[Queue] = [Queue(maxsize=2) for _ in range(self._num_videos)]

        # Initialize readers
        self._init_readers()

    def start(self) -> None:
        # Start worker threads (read frames)
        for i in range(self._num_videos):
            thread = threading.Thread(
                target=self._process_frames_worker, args=(i,), daemon=True
            )
            self._process_threads.append(thread)
            thread.start()

        self._logger.log(
            ConstStrings.LOG_NAME_DEBUG,
            f"Started {self._num_videos} shared memory readers"
        )

        # Main loop (render from main thread)
        try:
            while self._running:
                if self._enable_imshow:
                    self._render_frames_main_thread()
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
        finally:
            if self._enable_imshow:
                cv2.destroyAllWindows()

    def stop(self) -> None:
        self._running = False

        for reader in self._readers:
            try:
                reader.release()
            except Exception:
                pass

        for thread in self._process_threads:
            thread.join(timeout=1)

        self._logger.log(ConstStrings.LOG_NAME_DEBUG, LoggerMessages.ALGORITHM_MANAGER_STOPPED)

    def _init_readers(self) -> None:
        for video in self._videos_config:
            video_id = video.get("video_id")
            width = video.get("width", 1280)
            height = video.get("height", 720)

            reader = HandlerFactory.create_shm_reader_handler(video_id, width, height)
            self._readers.append(reader)
            reader.start()

    def _process_frames_worker(self, video_index: int) -> None:
        reader = self._readers[video_index]
        frame_count = 0
        consecutive_none_count = 0
        max_none_count = 10

        while self._running:
            frame = reader.read_frame()
            if frame is None:
                consecutive_none_count += 1
                if consecutive_none_count >= max_none_count:
                    self._logger.log(
                        ConstStrings.LOG_NAME_DEBUG,
                        f"Video {video_index}: No more frames available. Total frames read: {frame_count}"
                    )
                    self._running = False
                    break
                time.sleep(0.1)
                continue
            try:
                
                subtractor = self._bg_subtractors[video_index]
                fg = subtractor.apply(frame)
                _, mask = cv2.threshold(fg, 244, 255, cv2.THRESH_BINARY)
                kernel = cv2.getStructuringElement(
                    cv2.MORPH_RECT,
                    (Consts.MOTION_KERNEL_SIZE, Consts.MOTION_KERNEL_SIZE)
                )
                mask = cv2.dilate(mask, kernel, iterations=Consts.MOTION_DILATE_ITER)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                regions = 0
                for c in contours:
                    if cv2.contourArea(c) < Consts.MOTION_MIN_AREA:
                        continue
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    regions += 1

                if regions and frame_count % Consts.ALGO_FRAME_RATE == 0:
                    self._logger.log(
                        ConstStrings.LOG_NAME_DEBUG,
                        LoggerMessages.MOTION_REGION_COUNT.format(video_index, regions)
                    )
            except Exception as e:
                self._logger.log(ConstStrings.LOG_NAME_ERROR, LoggerMessages.MOTION_ERROR.format(e))
            
            consecutive_none_count = 0
            frame_count += 1

            if frame_count % 30 == 0:
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    f"Video {video_index}: Read {frame_count} frames from shared memory, shape: {frame.shape}"
                )

            q = self._frame_queues[video_index]
            if q.full():
                try:
                    q.get_nowait()
                except Empty:
                    pass
            q.put_nowait(frame)

    def _render_frames_main_thread(self) -> None:
        for i in range(self._num_videos):
            q = self._frame_queues[i]
            frame = None

            # drain to latest
            try:
                while True:
                    frame = q.get_nowait()
            except Empty:
                pass

            if frame is not None:
                try:
                    cv2.imshow(f"Video {i}", frame)
                except cv2.error as e:
                    self._logger.log(
                        ConstStrings.LOG_NAME_DEBUG,
                        f"cv2.imshow failed: {e}. Disabling imshow."
                    )
                    self._enable_imshow = False
                    cv2.destroyAllWindows()
                    break

        if self._enable_imshow:
            cv2.waitKey(max(1, int(1000 / max(1, Consts.ALGO_FRAME_RATE))))
