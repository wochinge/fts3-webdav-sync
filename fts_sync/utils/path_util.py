import logging

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


def absolute_path(*path_elements):
    return ''.join(path_elements)