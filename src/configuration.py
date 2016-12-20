import ruamel.yaml as yaml
import os.path
from pykwalify.core import Core as YamlValidator
import logging

import warnings
warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)

READ_MODE = 'r'


class Configuration(object):

    required_keys = ['Essential Settings', 'SSL settings']
    required_ssl_keys = ['Path of user certificate', 'Path of user key']

    def __init__(self, configuration_as_map):
        self.fts_url = configuration_as_map['Essential settings']['fts3 REST endpoint']
        self.source_url = configuration_as_map['Essential settings']['source endpoint']
        self.destination_url = configuration_as_map['Essential settings']['destination endpoint']
        self.ssl_settings = SSLSetting(configuration_as_map['SSL settings'])
        self.dav_source_options = {}
        self.dav_destination_options = {}
        self._init_dav_config(configuration_as_map)

        log_config = configuration_as_map.get('Logging', None)
        if log_config:
            self._init_logging(log_config)

    def _init_dav_config(self, configuration):
        common = {
            'ssl_verify_peer': self.ssl_settings.verify_host,
            'ssl_verify_host': self.ssl_settings.verify_host,
            'cert_path': self.ssl_settings.certificate_path,
            'key_path': self.ssl_settings.key_path,
            'verbose': configuration.get('DAV settings', {}).get('verbose', False)
        }
        self.dav_source_options = {
            'webdav_hostname': self.source_url
        }

        self.dav_destination_options = {
            'webdav_hostname': self.destination_url
        }

        self.dav_source_options.update(common)
        self.dav_destination_options.update(common)

    def _init_logging(self, logging_config):
        level = logging_config.get('log level', logging.DEBUG)
        path = logging_config.get('Logging', {}).get('path of logging file', None)
        logging.basicConfig(level=level, filename=path)


class SSLSetting(object):

    def __init__(self, configuration):
        self.verify_host = configuration.get('verify host', True)
        self.certificate_path = configuration['path of user certificate']
        self.key_path = configuration['path of user key']


def read_configuration_file(path):
    if not os.path.isfile(path):
        raise IOError('Log file was not found at this path: {}'.format(path))

    validator = YamlValidator(source_file=path, schema_files=['../config_schema.yaml'])
    validator.validate(raise_exception=True)
    with open(path, READ_MODE) as configuration_file:
        configuration = yaml.load(configuration_file)
    return Configuration(configuration)


