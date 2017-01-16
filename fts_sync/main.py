import argparse
from fts_sync.synchronization_runner import SynchronizationRunner


def main():
    parser = argparse.ArgumentParser(description='Synchronizes two webdav servers using FTS3.')
    parser.add_argument('-c', '--configFile',
                        action='store',
                        dest='file_path_of_config_file',
                        default='fts3_sync.yaml',
                        help='Path to the yaml configuration file.')
    args = parser.parse_args()
    sync_runner = SynchronizationRunner(args.file_path_of_config_file)
    sync_runner.run()


if __name__ == "__main__":
    main()
