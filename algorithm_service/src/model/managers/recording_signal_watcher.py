import os
from model.managers.recording_manager import RecordingManager


class RecordingSignalWatcher:
    def __init__(self, num_videos: int, recorder: RecordingManager) -> None:
        self._num_videos = num_videos
        self._recorder = recorder

    def tick(self) -> None:
        for i in range(self._num_videos):
            stream_id = i + 1
            start_signal = f"/app/logs/record_start_{stream_id}.signal"
            stop_signal = f"/app/logs/record_stop_{stream_id}.signal"

            if os.path.exists(start_signal):
                self._recorder.start_recording(i)
                try:
                    os.remove(start_signal)
                except:
                    pass

            if os.path.exists(stop_signal):
                self._recorder.stop_recording(i)
                try:
                    os.remove(stop_signal)
                except:
                    pass
