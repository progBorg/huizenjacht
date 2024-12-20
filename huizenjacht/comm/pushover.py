from huizenjacht.comm import Comm
from huizenjacht.config import Config

import time
import logging
import chump
import requests

class Pushover(Comm):
    # Public class attributes
    logger: logging.Logger
    conf: dict

    # Private class attributes
    _pushover: chump.Application
    _rcpt: chump.User

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conf = Config().config['comm']['pushover']
        self._sanity_check_conf()

        self._pushover = chump.Application(token=self.conf['api_key'])
        self._rcpt = self._pushover.get_user(self.rcpt)

    def send(self, msg: str) -> chump.Message | None:
        if len(str(msg)) == 0:
            return None

        message = self._rcpt.create_message(msg)
        message.send()
        return message

    """Check whether app and recipient are authenticated"""
    def is_ready(self) -> bool:
        return self._pushover.is_authenticated and self._rcpt.is_authenticated

    """Get recipient string
    Returns the string containing one or more user or group keys"""
    @property
    def rcpt(self) -> str:
        return self.conf['user_key']

    """Perform a simple sanity check on the configuration keys"""
    def _sanity_check_conf(self):
        entries = {
            "api_key": None,
            "user_key": None,
        }

        for name in entries.keys():
            try:
                value = self.conf[name]
            except KeyError as e:
                logging.error(f"{name} not found in Pushover configuration")
                raise e

            entries[name] = value
            if value is not None:
                self.logger.debug(f"{name}: {value}")

        logger.info("Configuration sanity check successful")

if __name__ == "__main__":
    # Quick functionality tests for this class
    conf_text = """
---
comm:
  pushover:
    active: true
    api_key: API_KEY
    user_key: USER_KEY
    """

    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    Config().load_text(conf_text)
    po = Pushover()

    while not po.is_ready():
        time.sleep(1)

    po.send(input(": "))
