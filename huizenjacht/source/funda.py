import json
import logging
import requests
import sqlite3
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from huizenjacht.source import Source
from huizenjacht.config import Config

class Funda(Source):

    # Constants
    BASE_URL = "https://www.funda.nl/zoeken/"
    _db_table_create_stmt = '''
CREATE TABLE IF NOT EXISTS "Funda" (
	"id"	INTEGER NOT NULL UNIQUE,
	"URL"	TEXT UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
)'''

    # Public attributes
    logger: logging.Logger = logging.getLogger(__name__)
    conf: dict = None
    db: sqlite3.Cursor

    # Private attributes
    _required_conf_entries: set = {
        "area",
        "buy_or_rent",
    }
    _req_url: str
    _req_url_params: dict
    _req_url_headers: dict
    _ua: UserAgent
    _conn: sqlite3.Connection


    def __init__(self, db: sqlite3.Connection):
        self.conf = Config().config['sources']['funda']

        self._sanity_check_conf()

        self._setup_from_conf()

        self._ua = UserAgent()

        self._conn = db
        self.db = db.cursor()

        self.db.execute(self._db_table_create_stmt)

    def get(self) -> list[str] | None:
        soup = self._do_request()

        if soup is None:
            return []

        url_list = self._parse_response(soup)

        if url_list is None:
            return []

        return url_list

    def _do_request(self) -> BeautifulSoup | None:
        # Randomize User-Agent
        headers = self._req_url_headers
        headers["User-Agent"] = self._ua.random

        # Do request
        res = requests.get(
            url=self._req_url,
            params=self._req_url_params,
            headers=headers,
        )

        if res.status_code != 200:
            self.logger.warning("Could not reach Funda page successfully, http status code %i", res.status_code)
            return None

        return BeautifulSoup(res.text, features="html.parser")

    def _parse_response(self, soup: BeautifulSoup) -> list:
        # Get urls
        urls_json = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents[0]))
        urls = [item["url"] for item in urls_json["itemListElement"]]

        return urls

    def is_new(self, house: str) -> bool:
        try:
            self.db.execute("insert into Funda (url) values (?)", [house])
        except sqlite3.IntegrityError:
            return False

        self._conn.commit()

        return True

    def _sanity_check_conf(self):
        super()

        buy_or_rent = self.conf_value("buy_or_rent")
        if not buy_or_rent in ("buy", "koop", "rent", "huur"):
            raise ValueError(f'Config entry buy_or_rent must be one of [buy, rent, koop, huur], is now "{buy_or_rent}"')

        self.logger.info("Configuration sanity check successful")

    def _setup_from_conf(self):
        # Build base url
        buy_or_rent = self.conf_value("buy_or_rent")
        url = urljoin(self.BASE_URL, "koop" if buy_or_rent in ("koop", "buy") else "huur")

        # Get values and build url parameters
        url_params = {
            "selected_area": self.conf_value("area"),
            "min_price": self.conf_value("min_price", None),
            "max_price": self.conf_value("max_price", None),
            "min_rooms": self.conf_value("min_rooms", None),
            "max_rooms": self.conf_value("max_rooms", None),
            "property_type": self.conf_value("property_type", "woonhuis"),
            "sort_by": self.conf_value("sort_by", "date-down"),
        }

        if isinstance(url_params["selected_area"], str):
            url_params["selected_area"] = f'["{url_params["selected_area"]}"]'
        elif isinstance(url_params["selected_area"], list):
            url_params["selected_area"] = '[' + ','.join(f'"{city}"' for city in url_params["selected_area"]) + ']'

        # Filter out keys with None value
        url_params = {k: v for k, v in url_params.items() if v is not None}

        self._req_url = url
        self._req_url_params = url_params
        self._req_url_headers = {}


if __name__ == "__main__":
    # Quick functionality tests for this class
    conf_text = """
---
server:
  debug: true
  db: "huizenjacht.db"
  message_defaults:
    title: "Nieuw huis gevonden"

sources:
  funda:
    active: true
    area: "gorinchem"
    buy_or_rent: "rent"
"""

    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    Config().load_text(conf_text)
    conf = Config().config
    db = sqlite3.connect(conf["server"]["db"])
    f = Funda(db)

    houses = f.get()

    for h in houses:
        print(f"{h}: {'new' if f.is_new(h) else 'old'}")

    f._conn.commit()
