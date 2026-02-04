import os
import threading
import time
from typing import List, Dict

class VideoManager:
    def __init__(self, videos_congig: List[Dict]):
        self.videos_config = videos_congig
        self.video_handlers = []
        self.threads = []
        self.running = True
        self._cleanup_shared_memory()

    def start(self) -> None:
        for video_config in self.videos_config:
            video_id = video_config["video_id"]
            video_path = video_config["video_path"]
            
            # Create handler
            handler = VideoStreamHandler(video_id, video_path)
            handler.start()
            self.handlers.append(handler)
            
            # Start processing thread
            thread = threading.Thread(
                target=self._process_video,
                args=(handler,),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        print(f"Started {len(self.handlers)} video streams")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    

    def _process_video(self, handler):
        while self.running:
            frame = handler.read_frame()
            if frame is not None:
                handler.write_frame(frame)
            else:
                time.sleep(0.01)  # Brief pause if read fails

    def _cleanup_shared_memory(self):
        shm_path = "/dev/shm/"
        prefixes = ["video", "shmpipe"]
        
        if not os.path.exists(shm_path):
            return
            
        files = [f for f in os.listdir(shm_path) 
                 if any(f.startswith(p) for p in prefixes)]
        
        for file in files:
            try:
                os.remove(os.path.join(shm_path, file))
                print(f"Removed old shared memory file: {file}")
            except Exception as e:
                print(f"Warning: Could not remove {file}: {e}")
    
    def stop(self):
        print("Stopping video manager...")
        self.running = False
        
        for handler in self.handlers:
            handler.release()
        
        for thread in self.threads:
            thread.join(timeout=2)
        
        print("Video manager stopped")