class SSLSetting(object):

    def __init__(self, configuration):
        self.verify_host = configuration.get('verify host', True)
        self.certificate_path = configuration['path of user certificate']
        self.key_path = configuration['path of user key']