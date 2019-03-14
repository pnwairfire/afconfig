"""Unit tests for pyairfire.configuration"""

__author__ = "Joel Dubowy"

import configparser

from py.test import raises

from afconfig import (
    config_parser_to_dict,
    get_config_value,
    set_config_value,
    merge_configs,
    GET_CONFIG_VALUE_ERR_MSG_NO_KEYS,
    SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG,
    SET_CONFIG_VALUE_ERR_MSG_MISSING_KEYS,
    MERGE_CONFIGS_ERR_MSG_CONFIG_CONFLICT,
    ConfigurationError
)


class TestConfigParserToDict(object):

    def test_none(self):
        d = config_parser_to_dict(None)
        assert {} == d

    def test_empty(self):
        d = config_parser_to_dict(configparser.ConfigParser())
        assert {} == d

    def test_valid(self):
        c = configparser.ConfigParser()
        c.add_section('a')
        c.add_section('b')
        c.set('a', 'aa', 'sdf')
        c.set('a', 'ab', "343")
        c.set('b', 'ba', "123")
        c.set('b', 'bb', 'sdfs')
        d = {
            'a': { 'aa': 'sdf', 'ab': "343"},
            'b': { 'ba': "123", 'bb': 'sdfs'}
        }
        assert d == config_parser_to_dict(c)

##
## Tests for utilitu methods
##

class TestGetConfigValue(object):

    def test_fail_on_missing_key_option(self):
        # undefined config
        with raises(KeyError) as e:
            get_config_value(None, 's', fail_on_missing_key=True)

        # invalid config
        # fail_on_missing_key never comes into play if config is invalid
        with raises(KeyError) as e:
            get_config_value("SDF", 's', fail_on_missing_key=True)
        with raises(KeyError) as e:
            get_config_value("SDF", 's', fail_on_missing_key=True, default=1)

        # empty config
        with raises(KeyError) as e:
            get_config_value({}, 's', fail_on_missing_key=True)
        # fail even if default is specified
        with raises(KeyError) as e:
            get_config_value({}, 's', fail_on_missing_key=True, default=1)

        config = {
            'a': {
                'aa': 'sdf',
                'ab': 343
            },
            'b': {
                'ba': 123,
                'bb': 'sdfs',
                'cc': {
                    'ccc': "SDF"
                }
            },
            'c': 12
        }
        with raises(KeyError) as e:
            get_config_value({}, 's', fail_on_missing_key=True)
        # fail even if default is specified
        with raises(KeyError) as e:
            get_config_value({}, 's', fail_on_missing_key=True, default=1)

        # key before last not in config, so last one isn't as well
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'ac', 'foo', fail_on_missing_key=True)
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'ac', 'foo', fail_on_missing_key=True, default=1)

        # last key not in config
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'az', fail_on_missing_key=True)
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'az', fail_on_missing_key=True, default=1)

        # second to last key points to scalar, so last key not in config
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'aa', 'foo', fail_on_missing_key=True)
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'aa', 'foo', fail_on_missing_key=True, default=1)

        # fail_on_missing is ignored if value is there
        assert 12 == get_config_value(config, 'c',
            fail_on_missing_key=True)
        # and default doesn't do anything in this case
        assert 12 == get_config_value(config, 'c',
            fail_on_missing_key=True, default=1)

    def test_fail_on_invalid_config_option(self):
        # undefined config
        get_config_value(None, 's', fail_on_invalid_config=True)

        # invalid config
        with raises(ConfigurationError) as e:
            get_config_value("SDF", 's', fail_on_invalid_config=True)
        with raises(ConfigurationError) as e:
            get_config_value("SDF", 's', fail_on_invalid_config=True, default=1)

        # empty config
        assert None == get_config_value({}, 's', fail_on_invalid_config=True)
        assert 1 == get_config_value({}, 's', fail_on_invalid_config=True, default=1)

        config = {
            'a': {
                'aa': 'sdf',
                'ab': 343
            },
            'b': {
                'ba': 123,
                'bb': 'sdfs',
                'cc': {
                    'ccc': "SDF"
                }
            },
            'c': 12
        }
        assert None == get_config_value(config, 's', fail_on_invalid_config=True)
        assert 1 == get_config_value(config, 's', fail_on_invalid_config=True, default=1)

        # key before last not in config, so last one isn't as well
        assert None == get_config_value(config, 'a', 'ac', 'foo', fail_on_invalid_config=True)
        assert 1 == get_config_value(config, 'a', 'ac', 'foo', fail_on_invalid_config=True, default=1)

        # last key not in config
        assert None == get_config_value(config, 'a', 'az', fail_on_invalid_config=True)
        assert 1 == get_config_value(config, 'a', 'az', fail_on_invalid_config=True, default=1)

        # second to last key points to scalar, so last key not in config
        with raises(ConfigurationError) as e:
            get_config_value(config, 'a', 'aa', 'foo', fail_on_invalid_config=True)
        with raises(ConfigurationError) as e:
            get_config_value(config, 'a', 'aa', 'foo', fail_on_invalid_config=True, default=1)

        # fail_on_missing is ignored if value is there
        assert 12 == get_config_value(config, 'c', fail_on_invalid_config=True)
        # and default doesn't do anything in this case
        assert 12 == get_config_value(config, 'c', fail_on_invalid_config=True, default=1)

    def test_fail_on_missing_keys_and_invalid_config_options(self):
        # undefined config
        with raises(KeyError) as e:
            get_config_value(None, 's',
                fail_on_missing_key=True, fail_on_invalid_config=True)

        # invalid config
        with raises(ConfigurationError) as e:
            get_config_value("SDF", 's',
                fail_on_missing_key=True, fail_on_invalid_config=True)
        with raises(ConfigurationError) as e:
            get_config_value("SDF", 's',
                fail_on_missing_key=True, fail_on_invalid_config=True, default=1)

        # empty config
        with raises(KeyError) as e:
            get_config_value({}, 's', fail_on_missing_key=True,
                fail_on_invalid_config=True)
        with raises(KeyError) as e:
            get_config_value({}, 's', fail_on_missing_key=True,
                fail_on_invalid_config=True, default=1)

        config = {
            'a': {
                'aa': 'sdf',
                'ab': 343
            },
            'b': {
                'ba': 123,
                'bb': 'sdfs',
                'cc': {
                    'ccc': "SDF"
                }
            },
            'c': 12
        }
        with raises(KeyError) as e:
            get_config_value(config, 's', fail_on_missing_key=True,
                fail_on_invalid_config=True)
        with raises(KeyError) as e:
            get_config_value(config, 's', fail_on_missing_key=True,
                fail_on_invalid_config=True, default=1)

        # key before last not in config, so last one isn't as well
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'ac', 'foo', fail_on_missing_key=True)
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'ac', 'foo', fail_on_missing_key=True, default=1)

        # last key not in config
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'az', fail_on_missing_key=True)
        with raises(KeyError) as e:
            get_config_value(config, 'a', 'az', fail_on_missing_key=True, default=1)

        # second to last key points to scalar, so last key not in config
        with raises(ConfigurationError) as e:
            get_config_value(config, 'a', 'aa', 'foo',
                fail_on_missing_key=True, fail_on_invalid_config=True)
        with raises(ConfigurationError) as e:
            get_config_value(config, 'a', 'aa', 'foo',
                fail_on_missing_key=True, fail_on_invalid_config=True, default=1)

        # fail_on_missing and fail_on_invalid_config are ignored if value is there
        assert 12 == get_config_value(config, 'c',
            fail_on_missing_key=True, fail_on_invalid_config=True)
        # and default doesn't do anything in this case
        assert 12 == get_config_value(config, 'c',
            fail_on_missing_key=True, fail_on_invalid_config=True, default=1)


    def test_undefined_config(self):
        with raises(ConfigurationError) as e_info:
            get_config_value(None)
        assert e_info.value.args[0] == GET_CONFIG_VALUE_ERR_MSG_NO_KEYS

        assert None == get_config_value(None, 's')
        assert None == get_config_value(None, 's', 'sdf')
        assert 1 == get_config_value(None, 's', default=1)
        assert 1 == get_config_value(None, 's', 'sdf', default=1)

    def test_invalid_config(self):
        with raises(ConfigurationError) as e_info:
            get_config_value(123)
        assert e_info.value.args[0] == GET_CONFIG_VALUE_ERR_MSG_NO_KEYS

        assert None == get_config_value(123, 's')
        assert None == get_config_value(123, 's', 'sdf')
        assert 1 == get_config_value(123, 's', default=1)
        assert 1 == get_config_value(123, 's', 'sdf', default=1)

    def test_empty_config(self):
        with raises(ConfigurationError) as e_info:
            get_config_value({})
        assert e_info.value.args[0] == GET_CONFIG_VALUE_ERR_MSG_NO_KEYS

        assert None == get_config_value({}, 's')
        assert None == get_config_value({}, 's', 'sdf')
        assert 1 == get_config_value({}, 's', default=1)
        assert 1 == get_config_value({}, 's', 'sdf', default=1)

    def test_full(self):
        config = {
            'a': {
                'aa': 'sdf',
                'ab': 343
            },
            'b': {
                'ba': 123,
                'bb': 'sdfs',
                'cc': {
                    'ccc': "SDF"
                }
            },
            'c': 12
        }

        with raises(ConfigurationError) as e_info:
            get_config_value(config)
        assert e_info.value.args[0] == GET_CONFIG_VALUE_ERR_MSG_NO_KEYS

        assert None == get_config_value(config, 'z')
        assert None == get_config_value(config, 'z', 'b')
        assert None == get_config_value(config, 'a', 'b')
        assert None == get_config_value(config, 'b', 'cc', 'z')
        assert None == get_config_value(config, 'a', 'aa', 'z')
        assert 1 == get_config_value(config, 'z', default=1)
        assert 1 == get_config_value(config, 'z', 'b', default=1)
        assert 1 == get_config_value(config, 'a', 'b', default=1)
        assert 1 == get_config_value(config, 'b', 'cc', 'z', default=1)
        assert 1 == get_config_value(config, 'a', 'aa', 'z', default=1)

        assert 12 == get_config_value(config, 'c')
        assert 12 == get_config_value(config, 'c', default=1)
        assert {'aa': 'sdf','ab': 343} == get_config_value(config, 'a')
        assert {'aa': 'sdf','ab': 343} == get_config_value(config, 'a', default=1)
        assert 'sdf' == get_config_value(config, 'a', 'aa')
        assert 'sdf' == get_config_value(config, 'a', 'aa', default=1)
        assert 'sdf' == get_config_value(config['a'], 'aa')
        assert 'sdf' == get_config_value(config['a'], 'aa', default=1)
        assert 'SDF' == get_config_value(config, 'b', 'cc', 'ccc')
        assert 'SDF' == get_config_value(config, 'b', 'cc', 'ccc', default=1)

class TestSetConfigValue(object):

    def test_invalid_config(self):
        with raises(ConfigurationError) as e_info:
            set_config_value(12, 3, '123')
        assert e_info.value.args[0] == SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG

    def test_no_keys(self):
        with raises(ConfigurationError) as e_info:
            set_config_value({}, 32)
        assert e_info.value.args[0] == SET_CONFIG_VALUE_ERR_MSG_MISSING_KEYS

    def test_basic(self):
        config = {}
        set_config_value(config, 123, 'a')
        assert config == {'a': 123}
        set_config_value(config, 321, 'b', 'c', 'd')
        assert config == {'a': 123, 'b': {'c': {'d': 321}}}

    def test_override_existing_value(self):
        config = {'a': 123, 'b': {'c': {'d': 321}}}
        set_config_value(config, 34, 'a')
        assert config == {'a': 34, 'b': {'c': {'d': 321}}}
        set_config_value(config, 123123, 'b', 'c', 'd')
        assert config == {'a': 34, 'b': {'c': {'d': 123123}}}

    def test_override_existing_dict(self):
        config = {'a': 123, 'b': {'c': {'d': 321}}}
        set_config_value(config, 34, 'b', 'c')
        assert config == {'a': 123, 'b': {'c': 34}}

class TestMergeConfigs(object):

    def test_invalid_configs(self):
        with raises(ConfigurationError) as e_info:
            merge_configs(12, {'a': 1})
        assert e_info.value.args[0] == SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG

        with raises(ConfigurationError) as e_info:
            merge_configs({'a': 1}, 12)
        assert e_info.value.args[0] == SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG

        with raises(ConfigurationError) as e_info:
            merge_configs(12, 12)
        assert e_info.value.args[0] == SET_CONFIG_VALUE_ERR_MSG_INVALID_CONFIG

    def test_conflicting_configs(self):
        # can't replace scalar with dict
        with raises(ConfigurationError) as e_info:
            merge_configs({'a': 'a'}, {'a': {'b': 'c'}})
        assert e_info.value.args[0] == MERGE_CONFIGS_ERR_MSG_CONFIG_CONFLICT

        # can't replace dict with scalar
        with raises(ConfigurationError) as e_info:
            merge_configs({'a': {'b': 'c'}}, {'a': 'a'})
        assert e_info.value.args[0] == MERGE_CONFIGS_ERR_MSG_CONFIG_CONFLICT

        # can't replace dict with None
        with raises(ConfigurationError) as e_info:
            merge_configs({'a': {'b': 'c'}}, {'a': None})
        assert e_info.value.args[0] == MERGE_CONFIGS_ERR_MSG_CONFIG_CONFLICT

        # Note: you *can* replace None with dict (see below)

    def test_empty_both_configs(self):
        a = {}
        b = merge_configs(a, {})
        assert a == b == {}

    def test_empty_config(self):
        a = {}
        b = merge_configs(a, {'a': 123})
        assert a == b == {'a': 123}

    def test_empty_to_be_merged_config(self):
        a = {'a': 123}
        b = merge_configs(a, {})
        assert a == b == {'a': 123}

    def test_allow_replace_none_with_dict(self):
        a = {'a': None}
        b = merge_configs(a, {'a': {'c': 3}})
        assert a == b == {'a': {'c': 3}}

    def test_all(self):
        a = {'a': 123}
        b = merge_configs(a, {'b': {'c': 3}})
        assert a == b == {'a': 123, 'b': {'c': 3}}
        b = merge_configs(a, {'b': {'d': 5}})
        assert a == b == {'a': 123, 'b': {'c': 3, 'd': 5}}
        b = merge_configs(a, {'b': {'d': 19, 'e': 10}, 'f': 321})
        assert a == b == {'a': 123, 'b': {'c': 3, 'd': 19, 'e': 10}, 'f': 321}
