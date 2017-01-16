from __future__ import absolute_import
import webdav.client as wc
from fts_sync.fts.fts import FTS
import fts_sync.file_tree.directory as tree
from fts_sync.file_tree.diff_tree import DiffedTree
from time import time, sleep
from fts_sync.configuration.configuration import read_configuration_file
import logging

logger = logging.getLogger('fts')


class SynchronizationRunner(object):

    def __init__(self, configuration_file_path):
        self.configuration_file_path = configuration_file_path

    def run(self):
        while True:
            start_time = time()
            configuration = self._get_configuration()

            logger.info('Start Synchronization')
            logger.debug('Getting the contents')
            source_tree = self._populate_file_tree(configuration.dav.source_options, 'webdav/')
            destination_tree = self._populate_file_tree(configuration.dav.destination_options, 'webdav/')
            logger.debug('Comparing the contents')
            file_diff = DiffedTree(destination_tree, source_tree)

            logger.info('New files:\n{}'.format(file_diff.new_files()))
            logger.info('Modified files:\n{}'.format(file_diff.modified_files()))

            if not configuration.sync_settings.dry_run:
                fts = FTS(configuration)
                fts.submit(file_diff)
            else:
                logger.debug('Not submitting changes as we are running in dry mode')

            if configuration.sync_settings.single_run:
                break
            else:
                sync_duration = time() - start_time
                time_till_next_run = configuration.sync_settings.interval - sync_duration
                logger.info('Synchronization took {} seconds'.format(sync_duration))
                logger.debug('Next run will start in {} minutes'.format(time_till_next_run / 60.0))
                sleep(time_till_next_run)

    def _get_configuration(self):
        return read_configuration_file(self.configuration_file_path)

    def _populate_file_tree(self, dav_config, start_directory=''):
        client = wc.Client(dav_config)
        file_tree = tree.Directory(client, start_directory)
        file_tree.populate()
        return file_tree
