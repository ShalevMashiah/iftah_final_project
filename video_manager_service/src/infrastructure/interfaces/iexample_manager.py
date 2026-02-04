from abc import ABC, abstractmethod


class IExampleManager(ABC):

    @abstractmethod
    def do_something(self):
        pass
