from __future__ import absolute_import


class DAVSetting(object):

    def __init__(self, source_host, source_start_dir, destination_host, destination_start_dir, ssl_config, dav_settings):
        self.verify_host = ssl_config.verify_host
        self.ssl_key = ssl_config.key_path
        self.ssl_cert = ssl_config.certificate_path
        self.verbose = dav_settings.get('verbose', False)

        self.source_start_directory = source_start_dir
        self.destination_start_directory = destination_start_dir

        self.destination_host = destination_host
        self.source_host = source_host
