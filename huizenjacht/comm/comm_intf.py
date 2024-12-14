from abc import ABC, abstractmethod

class Comm(ABC):
    """
    Communication interface to update user.
    """

    """
    Send a message to the user
    """
    @abstractmethod
    def send(self, msg: str) -> int:
        pass

    """
    Retrieve the readiness of this communication channel
    """
    @abstractmethod
    def is_ready(self) -> bool:
        pass
    