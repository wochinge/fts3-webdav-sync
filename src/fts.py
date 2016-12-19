import fts3.rest.client.easy as fts3


class FTS(object):

    def __init__(self, fts_endpoint, user_certificate, user_key, verify=True):
        self.context = fts3.Context(fts_endpoint, user_certificate, user_key, verify=verify)

    def submit(self, source, destination, files, overwrite=False):
        if len(files) < 1:
            return

        transfers = map(lambda f: self._create_transfer(source, destination, f), files)
        job = fts3.new_job(transfers, verify_checksum=False, overwrite=overwrite)
        return fts3.submit(self.context, job)

    def _create_transfer(self, source, destination, file):
        absolute_source = '{}{}'.format(source, file)
        absolute_destination = '{}{}'.format(destination, file)
        return fts3.new_transfer(absolute_source, absolute_destination)