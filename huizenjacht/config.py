import yaml
import logging
from pathlib import Path
from singleton import SingletonMeta

class Config(metaclass=SingletonMeta):
    logger = logging.getLogger(__name__)

    config_file: str = None  # Location of default config file
    _loaded_config_file: str = None  # Location of currently loaded config file
    _config: dict = None  # Loaded configuration

    def __init__(self, config_file: str = None):
        if config_file is not None:
            self.config_file = config_file

    def load(self, config_file: str = None):
        # Get desired config file location
        if config_file is None:
            config_file = self.config_file

        # Set up the configuration file parser
        with open(config_file, 'r') as stream:
            try:
                self._config = yaml.safe_load(stream)
            except yaml.YAMLError:
                self.logger.error("An error occured when attempting to parse the configuration file %s", self.config_file)
                return None

        self._loaded_config_file = config_file

    @property
    def config(self) -> type(_config):
        # Don't load config if it already exists
        if self._config is not None:
            return self._config

        # Sanity check
        if self.config_file is None:
            raise ValueError("No config file was specified")

        # Load config and return
        self.load()
        return self._config

    @property
    def loaded_config_file(self) -> str:
        return str(Path(self._loaded_config_file).resolve())
