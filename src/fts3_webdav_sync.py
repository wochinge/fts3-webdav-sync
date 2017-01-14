import webdav.client as wc
from fts.fts import FTS
import file_tree.directory as tree
from time import time, sleep
import argparse
from configuration.configuration import read_configuration_file
import logging

logger = logging.getLogger('fts')


def start_synchronizing(configuration_file_path):
    while True:
        start_time = time()
        configuration = read_configuration_file(configuration_file_path)
        logger.info('Start Synchronization')
        logger.debug('Getting the contents')
        source_client = wc.Client(configuration.dav.source_options)
        source_tree = tree.Directory(source_client, 'webdav/')
        source_tree.populate()

        destination_client = wc.Client(configuration.dav.destination_options)
        destination_tree = tree.Directory(destination_client, 'webdav/')
        destination_tree.populate()

        logger.debug('Comparing the contents')
        file_diff = source_tree.diff_tree(destination_tree)

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


def main():
    parser = argparse.ArgumentParser(description='Synchronizes two webdav servers using FTS3.')
    parser.add_argument('-c', '--configFile',
                        action='store',
                        dest='file_path_of_config_file',
                        default='fts3_sync.yaml',
                        help='Path to the yaml configuration file.')
    args = parser.parse_args()
    start_synchronizing(args.file_path_of_config_file)


if __name__ == "__main__":
    main()

