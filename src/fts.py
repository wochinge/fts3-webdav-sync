import fts3.rest.client.easy as fts3


class FTS(object):

    def __init__(self, config):
        self.context = fts3.Context(config.fts_url, config.ssl_settings.certificate_path,
                                    config.ssl_settings.key_path, config.ssl_settings.verify_host)
        self.source = config.source_url
        self.destination = config.destination_url

    def submit(self, files, overwrite=False):
        if len(files) < 1:
            return

        transfers = map(lambda f: self._create_transfer(self.source, self.destination, f), files)
        job = fts3.new_job(transfers, verify_checksum=False, overwrite=overwrite)
        return fts3.submit(self.context, job)

    def _create_transfer(self, source, destination, file):
        absolute_source = '{}{}'.format(source, file)
        absolute_destination = '{}{}'.format(destination, file)
        return fts3.new_transfer(absolute_source, absolute_destination)