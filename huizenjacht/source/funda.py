from funda_scraper import FundaScraper
import logging

from huizenjacht.source import Source
from huizenjacht.config import Config

class Funda(Source):
    # Public attributes
    logger: logging.Logger
    conf: dict

    # Private attributes
    _FS: FundaScraper

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.conf = Config().config['source']['funda']
        self._sanity_check_conf()

    def get(self):
        pass

    def is_new(self, house) -> bool:
        pass

    def _sanity_check_conf(self):
        pass

if __name__ == "__main__":
    # Quick functionality tests for this class
    conf_text = """
---
server:
  debug: true
  message_defaults:
    title: "Nieuw huis gevonden"

sources:
  funda:
    active: true
    settings:
"""

    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    Config().load_text(conf_text)
    f = Funda()

    print(f.get())
