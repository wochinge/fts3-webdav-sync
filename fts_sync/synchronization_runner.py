from __future__ import absolute_import
from time import time, sleep
from multiprocessing import Process, Queue

from fts_sync.dav.dav_client import DavClient
from fts_sync.fts.fts import FTS
from fts_sync.file_tree.diff_tree import DiffedTree
from fts_sync.configuration.configuration import read_configuration_file
import logging

logger = logging.getLogger('Synchronization runner')


class SynchronizationRunner(object):

    def __init__(self, configuration_file_path):
        self.configuration_file_path = configuration_file_path
        self.configuration = None

    def run(self):
        while True:
            logger.info('Start Synchronization')
            start_time = time()

            self.configuration = self.__get_configuration()

            source_tree, destination_tree = self.__index_dav_servers()
            file_diff = self.__calculate_delta(source_tree, destination_tree)

            if not self.configuration.sync_settings.dry_run:
                fts = FTS(self.configuration)
                fts.submit(file_diff)
            else:
                logger.debug('Not submitting changes as we are running in dry mode')

            logger.info('Synchronization took {} seconds'.format(time() - start_time))

            if self.configuration.sync_settings.single_run:
                break
            else:
                self.__sleep_till_next_run(start_time)

    def __get_configuration(self):
        logger.info('Read configuration')
        return read_configuration_file(self.configuration_file_path)

    def __index_dav_servers(self):
        logger.debug('Getting the contents')
        source_tree_queue = self.__populate_file_tree(self.configuration.source_url,
                                                      self.configuration.dav,
                                                      self.configuration.dav.source_start_directory)
        destination_tree_queue = self.__populate_file_tree(self.configuration.destination_url,
                                                           self.configuration.dav,
                                                           self.configuration.dav.destination_start_directory)

        return source_tree_queue.get(), destination_tree_queue.get()

    def __populate_file_tree(self, host, dav_config, start_directory=''):
        client = DavClient(host, dav_config)
        queue = Queue()
        process = Process(target=client.list, args=(queue, start_directory))
        process.start()
        return queue

    def __calculate_delta(self, source_tree, destination_tree):
        logger.debug('Comparing the contents')
        file_diff = DiffedTree(destination_tree, source_tree)
        logger.info('New files:\n{}'.format(file_diff.new_files()))
        logger.info('Modified files:\n{}'.format(file_diff.modified_files()))
        return file_diff

    def __sleep_till_next_run(self, start_time):
        sync_duration = time() - start_time
        time_till_next_run = self.configuration.sync_settings.interval - sync_duration
        logger.debug('Next run will start in {} minutes'.format(time_till_next_run / 60.0))
        sleep(time_till_next_run)