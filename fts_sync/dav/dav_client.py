from __future__ import absolute_import
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import grequests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from fts_sync.dav.dav_parser import parse_response
from fts_sync.file_tree.directory import Directory

import logging

logger = logging.getLogger('dav_client')


class DavClient(object):

    def __init__(self, host_url, dav_settings):
        self.host_url = host_url

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
        parent_directory.directories, parent_directory.files = parse_response(response.text)

        self.__list(parent_directory)
        queue.put(parent_directory)

    def __list(self, parent_directory):
        subdirectory_requests = [self.__request_for(sub.path) for sub in parent_directory.directories.values()]
        responses = grequests.map(subdirectory_requests, exception_handler=exception_handler)

        for index, sub in enumerate(parent_directory.directories.values()):
            subdirectory_content = responses[index].text
            sub.directories, sub.files = parse_response(subdirectory_content)
            self.__list(sub)

        return parent_directory

    def __request_for(self, path):
        url = '{}{}'.format(self.host_url, path)
        return grequests.request('PROPFIND', url, session=self.session)


def exception_handler(_, exception):
    logger.error(exception)
