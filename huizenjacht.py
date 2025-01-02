#!/usr/bin/env python3
# huizenjacht.py
# author: Tom Veldman
# (c) 2024
# MIT license

import argparse
import logging
import importlib
import sqlite3
import inflection

from huizenjacht.source import Source
from huizenjacht.comm import Comm
from huizenjacht.config import Config

# Some constants
PROGRAM_VERSION: str = "0.1"

SOURCES_KEY = "sources"
COMMS_KEY = "comm"

SERVER_COMM_MSG_TITLE = "Systeemmelding"
STARTUP_COMM_MSG_TEXT = "De huizenjager is (opnieuw) opgestart"

def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Set up logging, include systemd Journal support
    logging.basicConfig()
    logger = logging.getLogger()

    # set up global configuration
    conf = Config(config_file=args.configfile).config

    # Parse verbosity
    if args.verbose or conf['server']['debug']:
        logger.setLevel(logging.DEBUG)
        logger.debug("Running in verbose mode")
    else:
        logger.setLevel(logging.INFO)

    # Load database
    db = sqlite3.connect(conf["server"]["db"])

    sources = load_sources([key for key in conf[SOURCES_KEY].keys() if conf[SOURCES_KEY][key]["active"]], db)
    comms = load_comms([key for key in conf[COMMS_KEY].keys() if conf[COMMS_KEY][key]["active"]])

    # Handle seeding of database
    if args.reseed:
        seed(db)

    # Send a startup message
    for comm in comms:
        comm.send(STARTUP_COMM_MSG_TEXT, title=SERVER_COMM_MSG_TITLE)
    return 0

"""Load all source objects into a list and return that list"""
def load_sources(sources: list, db: sqlite3.Connection) -> list[Source]:
    return _load_classes_from_module(db, module_list=sources, module_location="huizenjacht.source")

"""Load all comm objects into a list and return that list"""
def load_comms(comms: list) -> list[Comm]:
    return _load_classes_from_module(module_list=comms, module_location="huizenjacht.comm")

def _load_classes_from_module(*args, module_list: list, module_location: str):
    # Collect file names and object names of modules
    file_names, object_names = _str_to_file_and_object_names(module_list)

    # Iterate through module strings and attempt to load corresponding objects
    # The class name must be CamelCased, the filename must be snake_cased
    objects = []
    for module_file, object_name in zip(file_names, object_names):
        objects.append(
            getattr(
                importlib.import_module(f".{module_file}", module_location),  # Module
                object_name
            )(*args)
        )

    return objects

"""From a list of strings, generate a list of filenames and object names for Sources and Comms """
def _str_to_file_and_object_names(stringlist: list[str]) -> (list[str], list[str]):
    # Make a copy of input with all inputs cast to a string and anything not alphanumeric or underscore removed
    _stringlist = [''.join(c for c in str(s) if c.isalnum() or c == '_') for s in stringlist]

    # Convert to snake_case
    file_names: list[str] = [inflection.underscore(s) for s in _stringlist]

    # Convert to CamelCase
    object_names: list[str] = [inflection.camelize(s, uppercase_first_letter=True) for s in _stringlist]

    return file_names, object_names

def seed(db: sqlite3.Connection):
    raise NotImplementedError("Database seeding is not yet implemented. Instead, start program once in simulation mode to mimic this behaviour.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="Huizenjacht housing website scraper",
        description="Scrape housing websites and push new results to the user",
        epilog="(C) Tom Veldman 2024"
    )
    parser.add_argument("--configfile", "-c", type=str, default="/etc/huizenjacht.yaml", help='Configuration file')
    parser.add_argument("-v", "--verbose", action="store_true", help="Log debug information")
    parser.add_argument("--version", action="version", version=f"%(prog)s v{PROGRAM_VERSION}")
    parser.add_argument("--reseed", action="store_true", help="Pull all currently available houses into database without notifying user")
    return parser.parse_args()


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
