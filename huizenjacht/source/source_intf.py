import logging
from typing import Any
from abc import ABC, abstractmethod


class Source(ABC):
    """
    Interface for information sources.
    """

    # Public attributes
    @property
    @abstractmethod
    def logger(self) -> logging.Logger:
        pass

    @property
    @abstractmethod
    def conf(self) -> dict:
        pass

    # Private attributes
    @property
    @abstractmethod
    def _required_conf_entries(self) -> set:
        pass

    @abstractmethod
    def __init__(self):
        pass

    """
	Get a list of available houses
	"""
    @abstractmethod
    def get(self):
        pass

    """
    Check whether the provided house is newly found
    """
    @abstractmethod
    def is_new(self, house: Any) -> bool:
        pass

    """
    Get a value from the config
    """
    def conf_value(self, key: str | tuple, default = None):
        if self.conf is None:
            raise ValueError("Attempted to read config value, but config was not loaded")

        value = None
        try:
            if isinstance(key, str):
                value = self.conf.get(key, default)
            elif isinstance(key, tuple):
                for k in key:
                    value = self.conf.get(k, default)
        except KeyError as ex:
            self.logger.error("Key %s does not exist in config, no default value given", key)
            raise ex

        return value

    """
    Basic configuration sanity check to see if all required keys are present
    """
    def _sanity_check_conf(self):
        req_entries = dict.fromkeys(self._required_conf_entries)
        for name in req_entries.keys():
            try:
                value = self.conf[name]
            except KeyError as e:
                logging.error(f"Required entry \"{name}\" not found in configuration")
                raise e

            req_entries[name] = value

        self.logger.debug(req_entries)
