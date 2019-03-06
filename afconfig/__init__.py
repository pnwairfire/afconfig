"""afconfig

TODO: create ConfigDict class with method 'merge' (which, as the name
  implies, merges another config dict in place)
"""

__author__ = "Joel Dubowy"

__version_info__ = (1,0,0)
__version__ = '.'.join([str(n) for n in __version_info__])


import argparse
import configparser
import json
import os
import re

__all__ = [
    'config_parser_to_dict',
    'get_config_value',
    'set_config_value',
    'merge_configs',
    'ImmutableConfigDict',
    'ConfigurationError'
]

class ConfigurationError(ValueError):
    pass

##
## Converting from ConfigParser objects
##

def config_parser_to_dict(config):
    d = {}
    if config:
        return {s:{k:v for k,v in config.items(s)} for s in config.sections()}
    return d

##
## Utility mehtods
##

GET_CONFIG_VALUE_ERR_MSG_NO_KEYS = "No config key(s) specified"
GET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG = "Invalid config"
GET_CONFIG_VALUE_ERR_MSG_MISSING_KEYS = "Missing config key {}"
def get_config_value(config, *keys, **kwargs):
    """Returns value from arbitrary nesting in config dict

    Recognized kwargs:
     - default -- if not specified, None is used as the default
     - fail_on_missing_key -- raise exception if key isn't in config
     - fail_on_invalid_config -- raise exception if any of the keys up to
          but not includeing the last point to something other than
          None or a dict

    TODO:
     - should we raise exception if config is None or empty but keys are defined
       and fail_on_missing_key is true ?
    """
    if not keys:
        # This will never happen on recursive call
        raise ConfigurationError(GET_CONFIG_VALUE_ERR_MSG_NO_KEYS)

    default = kwargs.get('default', None)

    if config is None:
        if kwargs.get('fail_on_missing_key'):
            raise KeyError("Missing config key {}".format(keys[0]))

    elif not isinstance(config, dict):
        if kwargs.get('fail_on_invalid_config'):
            raise ConfigurationError(GET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG)
        elif kwargs.get('fail_on_missing_key'):
            raise KeyError("Missing config key {}".format(keys[0]))

    else:  # config is a dict
        if len(keys) == 1:
            if keys[0] in config:
                return config[keys[0]]
            elif not kwargs.get('fail_on_missing_key'):
                return default
            raise KeyError(GET_CONFIG_VALUE_ERR_MSG_MISSING_KEYS.format(keys[0]))

        elif keys[0] in config:
            return get_config_value(config[keys[0]], *keys[1:], **kwargs)

    return default

SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG = "Expecting dict to hold config"
SET_CONFIG_VALUE_ERR_MSG_MISSING_KEYS = "Specify config keys to set value"

def set_config_value(config, value, *keys):
    if not isinstance(config, dict):
        raise ConfigurationError(SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG)
    if not keys:
        raise ConfigurationError(SET_CONFIG_VALUE_ERR_MSG_MISSING_KEYS)

    # TODO: prevent overriding of existing value ?
    if len(keys) == 1:
        config[keys[0]] = value
    else:
        if not isinstance(config.get(keys[0]), dict):
            config[keys[0]] = dict()
        set_config_value(config[keys[0]], value, *keys[1:])

MERGE_CONFIGS_ERR_MSG_CONFIG_CONFLICT = "Conflicting config dicts. Can't be merged."

def merge_configs(config, to_be_merged_config):
    if not isinstance(config, dict) or not isinstance(to_be_merged_config, dict):
        raise ConfigurationError(SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG)

    # Merge in place
    for k, v in to_be_merged_config.items():
        if k not in config or (
                not isinstance(config[k], dict) and not isinstance(v, dict)):
            config[k] = v
        elif isinstance(config[k], dict) and isinstance(v, dict):
            merge_configs(config[k], v)
        else:
            raise ConfigurationError(MERGE_CONFIGS_ERR_MSG_CONFIG_CONFLICT)

    # return reference to config, even though it was merged in place
    return config

##
## Config dict immutability
##

# TODO: move ImmutableConfigDict to pyairfire?

class ImmutableConfigDict(dict):
    # from https://www.python.org/dev/peps/pep-0351/

    def __hash__(self):
        return id(self)

    def _immutable(self, *args, **kws):
        raise TypeError('object is immutable')

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear       = _immutable
    update      = _immutable
    setdefault  = _immutable
    pop         = _immutable
    popitem     = _immutable


