import fts3.rest.client.easy as fts3
import configuration
from utils.path_util import path_with_timestamp
import logging

logger = logging.getLogger('fts')


class FTS(object):

    def __init__(self, config):
        self.context = fts3.Context(config.fts_url, config.ssl_settings.certificate_path,
                                    config.ssl_settings.key_path, verify=config.ssl_settings.verify_host)
        self.source = config.source_url
        self.destination = config.destination_url
        self.strategy = config.sync_settings.strategy

    def submit(self, file_differences):
        if len(file_differences) < 1 or (len(file_differences.new) < 1 and self.strategy == configuration.IGNORE_MODIFIED):
            return

        transfers_for_new_file = map(self._create_transfer, file_differences.new)
        transfers_for_modified = []
        if self.strategy != configuration.IGNORE_MODIFIED and len(file_differences.modified) > 0:
            transfers_for_modified = map(self._create_transfers_for_modified, file_differences.modified)
        all_transfers = transfers_for_new_file + transfers_for_modified
        job = fts3.new_job(all_transfers, verify_checksum=False, overwrite=self.strategy == configuration.OVERWRITE_MODIFIED)
        return fts3.submit(self.context, job)

    def _create_transfer(self, file):
        absolute_source = '{}{}'.format(self.source, file.path)
        absolute_destination = '{}{}'.format(self.destination, file.path)
        return fts3.new_transfer(absolute_source, absolute_destination)

    def _create_transfers_for_modified(self, modified_file):
        if self.strategy == configuration.OVERWRITE_MODIFIED:
            return self._create_transfer(modified_file)
        elif self.strategy == configuration.KEEP_BOTH:
            absolute_source = '{}{}'.format(self.source, modified_file.path)
            absolute_destination = '{}{}'.format(self.destination, path_with_timestamp(modified_file))
            return fts3.new_transfer(absolute_source, absolute_destination)
        else:
            logging.error('Unknown strategy for modified files: {}'.format(self.strategy))
            return

