from __future__ import absolute_import
from fts_sync.dav.dav_client import DavClient
from fts_sync.fts.fts import FTS
from fts_sync.file_tree.diff_tree import DiffedTree
from time import time, sleep
from fts_sync.configuration.configuration import read_configuration_file
import logging

logger = logging.getLogger('Synchronization runner')


class SynchronizationRunner(object):

    def __init__(self, configuration_file_path):
        self.configuration_file_path = configuration_file_path
        self.configuration = None

    def run(self):
        while True:
            start_time = time()
            self.configuration = self._get_configuration()

            logger.info('Start Synchronization')
            logger.debug('Getting the contents')
            source_tree = self._populate_file_tree(self.configuration.source_url,
                                                   self.configuration.dav,
                                                   self.configuration.dav.source_start_directory)
            destination_tree = self._populate_file_tree(self.configuration.destination_url,
                                                        self.configuration.dav,
                                                        self.configuration.dav.destination_start_directory)
            logger.debug('Comparing the contents')
            file_diff = DiffedTree(destination_tree, source_tree)
            logger.info('New files:\n{}'.format(file_diff.new_files()))
            logger.info('Modified files:\n{}'.format(file_diff.modified_files()))

            if not self.configuration.sync_settings.dry_run:
                fts = FTS(self.configuration)
                fts.submit(file_diff)
            else:
                logger.debug('Not submitting changes as we are running in dry mode')

            if self.configuration.sync_settings.single_run:
                break
            else:
                sync_duration = time() - start_time
                time_till_next_run = self.configuration.sync_settings.interval - sync_duration
                logger.info('Synchronization took {} seconds'.format(sync_duration))
                logger.debug('Next run will start in {} minutes'.format(time_till_next_run / 60.0))
                sleep(time_till_next_run)

    def _get_configuration(self):
        return read_configuration_file(self.configuration_file_path)

    def _populate_file_tree(self, host, dav_config, start_directory=''):
        client = DavClient(host, dav_config)
        return client.list(start_directory)
