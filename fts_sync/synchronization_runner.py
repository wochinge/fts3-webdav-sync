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
            start_time_of_synchronization = time()

            self.configuration = self.__get_configuration()
            start_time_of_current_step = time()
            source_tree, destination_tree = self.__index_dav_servers()
            logger.debug('It took {} seconds to index the servers'.format(time() - start_time_of_current_step))

            start_time_of_current_step = time()
            file_diff = self.__calculate_delta(source_tree, destination_tree)
            logger.debug('It tooks {} seconds to calculate the differences'.format(time() - start_time_of_current_step))

            if not self.configuration.sync_settings.dry_run:
                fts = FTS(self.configuration)
                fts.submit(file_diff)
            else:
                logger.debug('Not submitting changes as we are running in dry mode')

            logger.info('Synchronization took {} seconds'.format(time() - start_time_of_synchronization))

            if self.configuration.sync_settings.single_run:
                break
            else:
                self.__sleep_till_next_run(start_time_of_synchronization)

    def __get_configuration(self):
        logger.debug('Read configuration')
        return read_configuration_file(self.configuration_file_path)

    def __index_dav_servers(self):
        logger.debug('Getting the contents')
        source_tree_queue, source_tree_process = self.__populate_file_tree(self.configuration.source_url,
                                                                           self.configuration.dav.source_start_directory)
        destination_tree_queue, destination_tree_process = self.__populate_file_tree(self.configuration.destination_url,
                                                                                     self.configuration.dav.destination_start_directory)

        source_file_tree = source_tree_queue.get()
        destination_tree = destination_tree_queue.get()
        source_tree_process.join()
        destination_tree_process.join()

        return source_file_tree, destination_tree

    def __populate_file_tree(self, host, start_directory=''):
        client = DavClient(host, self.configuration.dav, self.configuration.sync_settings.excluded)
        queue = Queue()
        process = Process(target=client.list, args=(queue, start_directory))
        process.start()
        return queue, process

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