import logging
from re import split as split_with_regex
from fnmatch import fnmatch

logger = logging.getLogger('utils.path_util')


def path_with_timestamp(file_object):
    path = file_object.path
    split = path.rsplit('/', 1)
    directory = split[0] + '/'
    name = split[1]

    return _with_timestamp(name, file_object, directory)


def _with_timestamp(file_name, file_object, path=''):
    time = file_object.etag
    if not file_name:
        logger.warn('Could not format path with timestamp for file {}'.format(file_name))
        return ''

    if file_name.startswith('.'):
        path += '.'
        split = file_name[1:].split('.')
    else:
        split = file_name.split('.')

    path += split[0]
    if len(split) == 1:
        return '{}_({})'.format(path, time)
    elif len(split) >= 2:
        return '{}_({}).{}'.format(path, time, '.'.join(split[1:]))


def name_with_timestamp(name, file_object):
    return _with_timestamp(name, file_object)


def absolute_url(*path_elements):
    concatenated = ''.join(path_elements)
    return concatenated.replace(' ', '%20')


def split_in_url_and_directory(url):
    if not url.endswith('/'):
        url += '/'
    pattern = r'(http[s]?:\/\/.+?[^\/]\/)'
    result = split_with_regex(pattern, url)
    if len(result) != 3:
        raise ValueError("The url you provided is not valid.", url)
    return result[1], result[2]


def remove_excluded(files, patterns):
    if not patterns:
        return files
    return {name: file for name, file in files.iteritems() if _file_not_matches_patterns(file, patterns)}


def _file_not_matches_patterns(file, patterns):
    match_results = map(lambda pattern: fnmatch(file.path, pattern), patterns)
    return not any(match_results)

