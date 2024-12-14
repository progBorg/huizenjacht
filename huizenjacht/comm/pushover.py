from .comm_intf import Comm
import logging

class Pushover(Comm):
    logger = logging.getLogger(__name__)

    def __init__(self):
        pass

    def send(self, msg: str) -> int:
        pass

    def is_ready(self) -> bool:
        pass
