# secure-config-manager

## Description
Secure ConfigManager offers splitting your JSON config files into two parts.

We suggest one main `config.json` file that can be safely checked out to version control system. This can contain default values or a sample config structure for reference. The second one would be `config_override.json`, containing secret tokens or environment-dependent values.

Data in `config_override.json` is assumed to be more relevant, hence if the value is present in both configs, we choose config_override.

## Usage example
```
>>> from secure_config_manager import ConfigManager
>>> config_manager = ConfigManager(config_path="tests/test_config.json", config_override_path="tests/test_config_override.json", redacted_keys=("secret", "key"))
>>> config_manager.load_config_with_override()
{'key_a': {'attr1': 'value1', 'attr2': 'new_value', 'attr_secret': 'secret_value'}, 'key_b': {'attr1': 1}, 'key_c': {'app_key': 'sensitive_value'}}
>>> config_manager.redact(config_manager.get_key_a_config())
{'attr1': 'value1', 'attr2': 'new_value', 'attr_secret': '*****'}
```

## Notes:
* ConfigManager is a singleton class
* ConfigManager is application-agnostic and can be used in any Python 3.x project of your choice