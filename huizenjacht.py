#!/usr/bin/env python3
# huizenjacht.py
# author: Tom Veldman
# (c) 2024
# MIT license

import argparse
import logging

from huizenjacht.config import Config

# Some constants
PROGRAM_VERSION: str = "0.1"

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



def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="Huizenjacht housing website scraper",
        description="Scrape housing websites and push new results to the user",
        epilog="(C) Tom Veldman 2024"
    )
    parser.add_argument("--configfile", "-c", type=str, default="/etc/huizenjacht.yaml", help='Configuration file')
    parser.add_argument("-v", "--verbose", action="store_true", help="Log debug information")
    parser.add_argument("--version", action="version", version=f"%(prog)s v{PROGRAM_VERSION}")
    return parser.parse_args()


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
