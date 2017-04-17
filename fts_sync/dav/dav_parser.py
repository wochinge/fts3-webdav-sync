import lxml.etree as etree

from fts_sync.file_tree.file import File
from fts_sync.file_tree.directory import Directory
from fts_sync.utils.string_util import remove_quotes

import logging

logger = logging.getLogger('dav_parser')

path_separator = '/'

type_key = './/{DAV:}resourcetype'
path_key = './/{DAV:}href'
size_key = './/{DAV:}getcontentlength'
etag_key = './/{DAV:}getetag'


def parse_response(dav_response):
    files = {}
    directories = {}

    logger.debug(dav_response)
    tree = etree.fromstring(dav_response.encode('utf-8'))
    file_infos = tree.findall('.//{DAV:}response')

    # exclude directory itself
    for info in file_infos[1:]:
        __parse_file(info, files, directories)

    return directories, files


def __parse_file(file_info, files, directories):
    file_path = file_info.findtext(path_key)
    file_name = __filename(file_path)
    file_size = file_info.findtext(size_key)
    file_etag = remove_quotes(file_info.findtext(etag_key))

    if __is_directory(file_info):
        directories[file_name] = Directory(path=file_path, etag=file_etag)
    else:
        files[file_name] = File(path=file_path, size=file_size, etag=file_etag)


def __filename(file_path):
    path_split = file_path.split(path_separator)
    return path_split[-2] + path_separator if path_split[-1] == '' else path_split[-1]


def __is_directory(file_info):
    resource_type = file_info.find('.//{DAV:}resourcetype')
    if resource_type is None:
        raise RuntimeError('Your WebDAV server does not support the property. Therefore, directories and files cannot be distinguished!')
    else:
        directory_info = file_info.find('.//{DAV:}collection')
        return directory_info is not None
