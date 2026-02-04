from abc import ABC


class IVideoManager(ABC):
    
    def start(self) -> None:    
        pass    

    def stop(self) -> None:   
        pass