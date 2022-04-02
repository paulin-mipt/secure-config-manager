import datetime
import json
import logging
import re
from typing import Iterable

from .singleton import Singleton

logger = logging.getLogger(__name__)


class ConfigManager(Singleton):
    """
    ConfigManager is a singleton class, offering joining json configs.

    We assume that there is a main config, possibly checked out to version control,
    and the "override" config, containing secrets and keys.

    In this approach we suggest checking out default values and the general structure of the config,
    while all the tokens and environment-dependent values should go to config_override.

    Data in config_override is assumed to be more correct. If the value is present in both configs,
    we choose config_override.
    """
    def __init__(
            self,
            config_path: str = 'config.json',
            config_override_path: str = 'config_override.json',
            redacted_keys: Iterable[str] = set(),
            redaction_stub: str = '*****'
    ):
        if self.was_initialized():
            return

        self.config_path = config_path
        self.config_override_path = config_override_path
        self._redacted_keys = redacted_keys
        self._redaction_stub = redaction_stub
        self._latest_config = {}
        self._latest_config_override = {}
        self._latest_config_ts = None

    def load_config_with_override(self) -> dict:
        main_config = self._load_config(self.config_path) or {}
        override_config = self._load_config(self.config_override_path) or {}
        ConfigManager.join_configs(main_config, override_config)
        self._latest_config = main_config
        self._latest_config_override = override_config
        self._latest_config_ts = datetime.datetime.now()
        return main_config

    def get_latest_config(self):
        """
        Recommended way to access config without re-reading from disk.
        Freshness of the config depends on jobs.config_checker_job
        """
        logger.debug(f'Got config, last updated: {self._latest_config_ts}')
        return self._latest_config

    def __getattr__(self, item):
        """
        Given that top-level config is a dict, this allows to access config['param']
        as config_manager.get_param_config()
        """
        match = re.fullmatch(r'get_([\w_-]+)_config', item)
        if match:
            subconfig_name = match.group(1)
            logger.debug(f'Trying to find subconfig {subconfig_name}')
            subconfig = self.get_latest_config().get(subconfig_name)
            if subconfig is not None:
                return lambda: subconfig
        raise AttributeError

    def set_value_to_config_override(self, config_path: str, new_value):
        """
        Sets a new value to config_override and writes it to the disk.
        config_path example: jobs.sample_job.chats
        Note: no sanity checks performed inside the method!
        """
        new_config_piece = new_value
        for config_item in config_path.split('.')[::-1]:
            new_config_piece = {config_item: new_config_piece}
        config_override = self._latest_config_override
        ConfigManager.join_configs(config_override, new_config_piece)
        self._write_config_override(config_override)

    @staticmethod
    def join_configs(main_config: dict, override_config: dict):
        """Recursively override values from the main config (in place)"""
        for key in override_config:
            if key in main_config and isinstance(main_config[key], dict):
                # recursively do the same
                ConfigManager.join_configs(
                    main_config[key], override_config[key]
                )
            else:
                # rewrite if key is absent, or is list/str/int/bool
                main_config[key] = override_config[key]

    def redact(self, config: dict) -> dict:
        """Returns redacted config copy"""
        if not isinstance(config, dict):
            return config

        redacted_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                redacted_config[key] = self.redact(value)
            else:
                redacted_config[key] = value
                for redacted_key in self._redacted_keys:
                    if redacted_key in key:
                        redacted_config[key] = self._redaction_stub
                        break
        return redacted_config

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path) as fin:
                try:
                    return json.loads(fin.read())
                except json.JSONDecodeError as e:
                    logger.error(e)
        except IOError:
            logger.warning(f'Config file at {config_path} not found')

    def _write_config_override(self, config_override: dict):
        with open(self.config_override_path, 'w') as fout:
            fout.write(json.dumps(config_override, indent=4))
