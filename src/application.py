import webdav.client as wc
from fts import FTS
import file_tree as tree
from time import time, sleep
import argparse
from configuration import read_configuration_file


def start_synchronizing(configuration_file_path):
    configuration = read_configuration_file(configuration_file_path)
    source_client = wc.Client(configuration.dav_source_options)
    source_tree = tree.FileTree(source_client, 'webdav/')
    source_tree.populate()

    destination_client = wc.Client(configuration.dav_destination_options)
    destination_tree = tree.FileTree(destination_client, 'webdav/')
    destination_tree.populate()

    new, modified, removed = destination_tree.diff(source_tree)
    #print(new)
    print(modified)
    fts = FTS(configuration)
    fts.submit(new)


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