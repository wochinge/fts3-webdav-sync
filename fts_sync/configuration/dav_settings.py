from __future__ import absolute_import


class DAVSetting(object):

    def __init__(self, source_host, source_start_dir, destination_host, destination_start_dir, ssl_config, dav_settings):
        common = {
            'ssl_verify_peer': ssl_config.verify_host,
            'ssl_verify_host': ssl_config.verify_host,
            'cert_path': ssl_config.certificate_path,
            'key_path': ssl_config.key_path,
            'verbose': dav_settings.get('verbose', False)
        }
        self.source_start_directory = source_start_dir
        self.destination_start_directory = destination_start_dir

        self.source_options = {
            'webdav_hostname': source_host
        }

        self.destination_options = {
            'webdav_hostname': destination_host
        }

        self.source_options.update(common)
        self.destination_options.update(common)
