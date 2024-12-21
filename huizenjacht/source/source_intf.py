from typing import Any
from abc import ABC, abstractmethod


class Source(ABC):
    """
    Interface for information sources.
    """

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