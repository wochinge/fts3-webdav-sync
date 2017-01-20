from __future__ import absolute_import
import fts3.rest.client.easy as fts3
import fts_sync.configuration.synchronization_settings as SyncStrategy
from fts_sync.utils.path_util import path_with_timestamp, absolute_url
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

        new_files = file_differences.new_files()
        modified_files = file_differences.modified_files()
        total_changes = len(new_files) + (0 if self.strategy == SyncStrategy.IGNORE_MODIFIED else len(modified_files))
        if total_changes < 1:
            logger.info('No changes to synchronize')
            return

        transfers_for_new_file = map(self._create_transfer, new_files)
        transfers_for_modified = []
        if self.strategy != SyncStrategy.IGNORE_MODIFIED and len(file_differences.modified_files()) > 0:
            transfers_for_modified = map(self._create_transfers_for_modified, modified_files)

        all_transfers = transfers_for_new_file + transfers_for_modified
        job = fts3.new_job(all_transfers, verify_checksum=False, overwrite=self.strategy == SyncStrategy.OVERWRITE_MODIFIED)
        return fts3.submit(self.context, job)

    def _create_transfer(self, file):
        absolute_source = absolute_url(self.source, file.path)
        absolute_destination = absolute_url(self.destination, file.path)
        return fts3.new_transfer(absolute_source, absolute_destination)

    def _create_transfers_for_modified(self, modified_file):
        if self.strategy == SyncStrategy.OVERWRITE_MODIFIED:
            return self._create_transfer(modified_file)
        elif self.strategy == SyncStrategy.KEEP_BOTH:
            absolute_source = absolute_url(self.source, modified_file.path)
            absolute_destination = absolute_url(self.destination, path_with_timestamp(modified_file))
            return fts3.new_transfer(absolute_source, absolute_destination)
        else:
            logging.error('Unknown strategy for modified files: {}'.format(self.strategy))
            return

