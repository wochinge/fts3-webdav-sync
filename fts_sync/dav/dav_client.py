from __future__ import absolute_import
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import grequests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from fts_sync.dav.dav_parser import parse_response
from fts_sync.file_tree.directory import Directory
from fts_sync.utils.path_util import remove_excluded

import logging

logger = logging.getLogger('dav_client')


class DavClient(object):

    def __init__(self, host_url, dav_settings, patterns_to_exclude):
        self.host_url = host_url
        self.exclude_patterns = patterns_to_exclude
        self.__setup_request_session(dav_settings)

    def __setup_request_session(self, dav_settings):
        self.session = requests.Session()
        self.session.cert = (dav_settings.ssl_cert, dav_settings.ssl_key)
        self.session.headers['Depth'] = '1'
        self.session.headers['Accept'] = 'Accept: */*'
        self.session.verify = dav_settings.verify_host

    def list(self, queue, path, parent_directory=None):
        if parent_directory is None:
            parent_directory = Directory(path=path, etag='')

        request = [self.__request_for(path)]
        response = grequests.map(request, exception_handler=exception_handler)[0]
        parent_directory.directories, parent_directory.files = self.__files_and_dirs(response)

        self.__list(parent_directory)
        queue.put(parent_directory)

    def __list(self, parent_directory):
        subdirectory_requests = [self.__request_for(sub.path) for sub in parent_directory.directories.values()]
        responses = grequests.map(subdirectory_requests, exception_handler=exception_handler)

        for index, sub in enumerate(parent_directory.directories.values()):
            subdirectory_response = responses[index]
            sub.directories, sub.files = self.__files_and_dirs(subdirectory_response)
            self.__list(sub)

        return parent_directory

    def __request_for(self, path):
        url = '{}{}'.format(self.host_url, path)
        return grequests.request('PROPFIND', url, session=self.session)

    def __files_and_dirs(self, response):
        if response.status_code not in range(200, 299):
            logger.error('HTTP error {} while indexing {}.'.format(response.status_code, self.host_url))
            return {}, {}

        parsed = parse_response(response.text)
        return self.__remove_excluded(parsed)

    def __remove_excluded(self, (files, directories)):
        return remove_excluded(files, self.exclude_patterns), remove_excluded(directories, self.exclude_patterns)


def exception_handler(_, exception):
    logger.error(exception)
