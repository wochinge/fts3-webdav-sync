
class DAVSetting(object):

    def __init__(self, source_url, destination_url, ssl_config, dav_settings):
        common = {
            'ssl_verify_peer': ssl_config.verify_host,
            'ssl_verify_host': ssl_config.verify_host,
            'cert_path': ssl_config.certificate_path,
            'key_path': ssl_config.key_path,
            'verbose': dav_settings.get('verbose', False)
        }
        self.source_options = {
            'webdav_hostname': source_url
        }

        self.destination_options = {
            'webdav_hostname': destination_url
        }

        self.source_options.update(common)
        self.destination_options.update(common)