from __future__ import absolute_import
import ruamel.yaml as yaml
import os.path
from pykwalify.core import Core as YamlValidator
import logging
from fts_sync.configuration.ssl_settings import SSLSetting
from fts_sync.configuration.synchronization_settings import SynchronizationSetting
from fts_sync.configuration.dav_settings import DAVSetting
from fts_sync.utils.path_util import split_in_url_and_directory

import warnings
warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)

READ_MODE = 'r'

ESSENTIAL = 'Essential settings'


class Configuration(object):

    required_keys = ['Essential Settings', 'SSL settings']
    required_ssl_keys = ['Path of user certificate', 'Path of user key']

    def __init__(self, configuration_as_map):
        self.fts_url = configuration_as_map[ESSENTIAL]['fts3 REST endpoint']

        source_url = configuration_as_map[ESSENTIAL]['source endpoint']
        self.source_url, source_start_directory = split_in_url_and_directory(source_url)

        destination_url = configuration_as_map[ESSENTIAL]['destination endpoint']
        self.destination_url, destination_start_directory = split_in_url_and_directory(destination_url)

        self.ssl_settings = SSLSetting(configuration_as_map['SSL settings'])
        self.dav = DAVSetting(self.source_url, source_start_directory,
                              self.destination_url, destination_start_directory,
                              self.ssl_settings, configuration_as_map.get('DAV settings', {}))

        log_config = configuration_as_map.get('Logging', None)
        if log_config:
            self._init_logging(log_config)

        synchronization_config = configuration_as_map.get('Synchronization settings', None)
        if synchronization_config:
            self.sync_settings = SynchronizationSetting(synchronization_config)

    def _init_logging(self, logging_config):
        level = logging_config.get('log level', logging.DEBUG)
        path = logging_config.get('Logging', {}).get('path of logging file', None)
        logging.basicConfig(level=level, filename=path)


def read_configuration_file(path):
    if not os.path.isfile(path):
        raise IOError('Log file was not found at this path: {}'.format(path))

    validator = YamlValidator(source_file=path, schema_files=['config_schema.yaml'])
    validator.validate(raise_exception=True)
    with open(path, READ_MODE) as configuration_file:
        configuration = yaml.load(configuration_file)
    return Configuration(configuration)


