import os
import cv2
from globals.consts.consts import Consts
import threading
import time
from queue import Queue, Empty
from typing import List, Dict, Optional
from datetime import datetime

from infrastructure.interfaces.managers.ialgorithm_manager import IAlgorithmManager
from infrastructure.factories.handler_factory import HandlerFactory
from infrastructure.factories.algorithm_factory import AlgorithmFactory
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
        self._logger.log(ConstStrings.LOG_NAME_DEBUG, LoggerMessages.MOTION_STARTING)
        
        # Recording state
        self._recording: List[bool] = [False] * self._num_videos
        self._video_writers: List[Optional[cv2.VideoWriter]] = [None] * self._num_videos
        self._recording_lock = threading.Lock()
        
        # Create records directory
        os.makedirs("/app/records", exist_ok=True)
        
        # Initialize algorithms per video
        self._algorithms = []
        for video in self._videos_config:
            algo_type = video.get("algorithm", "motion_detection")
            algo_cfg = video.get("algorithm_config", {})
            try:
                algo = AlgorithmFactory.create(algo_type, algo_cfg)
                self._algorithms.append(algo)
            except Exception as e:
                self._logger.log(ConstStrings.LOG_NAME_ERROR, LoggerMessages.MOTION_ERROR.format(e))
                self._algorithms.append(None)
        
        # Motion starting already logged above
        
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

    def start_recording(self, video_index: int) -> str:
        with self._recording_lock:
            if self._recording[video_index]:
                return "Already recording"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H:%M:%S")
            filename = f"/app/records/Camera_name{video_index + 1}_{timestamp}.avi"
            
            video_config = self._videos_config[video_index]
            width = video_config.get("width", 1280)
            height = video_config.get("height", 720)
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            writer = cv2.VideoWriter(filename, fourcc, Consts.ALGO_FRAME_RATE, (width, height))
            
            if not writer.isOpened():
                self._logger.log(ConstStrings.LOG_NAME_ERROR, f"Failed to start recording for stream {video_index + 1}")
                return "Failed to start recording"
            
            self._video_writers[video_index] = writer
            self._recording[video_index] = True
            self._logger.log(ConstStrings.LOG_NAME_DEBUG, f"Started recording stream {video_index + 1} to {filename}")
            return filename

    def stop_recording(self, video_index: int) -> bool:
        with self._recording_lock:
            if not self._recording[video_index]:
                return False
            
            writer = self._video_writers[video_index]
            if writer:
                writer.release()
            
            self._video_writers[video_index] = None
            self._recording[video_index] = False
            self._logger.log(ConstStrings.LOG_NAME_DEBUG, f"Stopped recording stream {video_index + 1}")
            return True

    def is_recording(self, video_index: int) -> bool:
        return self._recording[video_index]

    def _check_recording_signals(self) -> None:
        for i in range(self._num_videos):
            stream_id = i + 1
            start_signal = f"/app/logs/record_start_{stream_id}.signal"
            stop_signal = f"/app/logs/record_stop_{stream_id}.signal"
            
            if os.path.exists(start_signal):
                self.start_recording(i)
                try:
                    os.remove(start_signal)
                except:
                    pass
            
            if os.path.exists(stop_signal):
                self.stop_recording(i)
                try:
                    os.remove(stop_signal)
                except:
                    pass

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
                # Check for recording signals
                self._check_recording_signals()
                
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

        # Stop all recordings
        for i in range(self._num_videos):
            if self._recording[i]:
                self.stop_recording(i)

        for reader in self._readers:
            try:
                reader.release()
            except Exception:
                pass

        for algo in getattr(self, "_algorithms", []):
            try:
                if algo:
                    algo.release()
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
                algo = self._algorithms[video_index]
                if algo:
                    frame = algo.process(frame)
            except Exception as e:
                self._logger.log(ConstStrings.LOG_NAME_ERROR, LoggerMessages.MOTION_ERROR.format(e))
            
            consecutive_none_count = 0
            frame_count += 1
                
            if frame_count % 30 == 0:
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    f"Video {video_index}: Read {frame_count} frames from shared memory, shape: {frame.shape}"
                )

            # Save latest frame as JPEG for GUI display
            try:
                output_path = f"/app/logs/stream_{video_index + 1}.jpg"
                cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            except Exception as e:
                self._logger.log(ConstStrings.LOG_NAME_DEBUG, f"Failed to save frame: {e}")

            # Write to recording if active
            if self._recording[video_index]:
                writer = self._video_writers[video_index]
                if writer and writer.isOpened():
                    try:
                        writer.write(frame)
                    except Exception as e:
                        self._logger.log(ConstStrings.LOG_NAME_ERROR, f"Failed to write frame to recording: {e}")

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
                    cv2.imshow(f"Video {i + 1}", frame)
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
