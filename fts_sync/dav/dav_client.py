from __future__ import absolute_import
import pycurl
from StringIO import StringIO
from fts_sync.dav.dav_parser import parse_response
from fts_sync.file_tree.directory import Directory


class DavClient(object):

    def __init__(self, host_url, dav_settings):
        self.host_url = host_url

        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.SSLKEY, dav_settings.ssl_key)
        self.curl.setopt(pycurl.SSLCERT, dav_settings.ssl_cert)
        self.curl.setopt(pycurl.SSL_VERIFYHOST, dav_settings.verify_host)
        self.curl.setopt(pycurl.SSL_VERIFYPEER, dav_settings.verify_host)
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)

    def list(self, path, parent_directory=None):
        if parent_directory is None:
            parent_directory = Directory(path=path, etag='')

        # Prepare curl
        header = ['Accept: */*', 'Depth: 1']
        url = '{}{}'.format(self.host_url, path)
        self.__configure_curl(url, 'PROPFIND', header)

        # Execute request
        response = self.__execute_request()

        # Parse response
        parent_directory.directories, parent_directory.files = parse_response(response)
        for subdirectory in parent_directory.directories.values():
            self.list(path=subdirectory.path, parent_directory=subdirectory)

        return parent_directory

    def __configure_curl(self, url, request_method, header):
        self.curl.setopt(pycurl.CUSTOMREQUEST, request_method)
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.HTTPHEADER, header)

    def __execute_request(self):
        response_buffer = StringIO()
        self.curl.setopt(pycurl.WRITEDATA, response_buffer)
        self.curl.perform()
        return response_buffer.getvalue()