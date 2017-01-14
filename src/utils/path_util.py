import logging

logger = logging.getLogger('utils.path_util')


def path_with_timestamp(file_object):
    return _with_timestamp(file_object.path, file_object)


def _with_timestamp(text, file_object):
    time = file_object.etag
    split = text.split('.')
    if len(split) == 1:
        return '{}_({})'.format(split[0], time)
    elif len(split) == 2:
        return '{}_({}).{}'.format(split[0], time, split[1])
    else:
        logger.warn('Could not format path with timestamp for file {}'.format(text))
        return ''


def name_with_timestamp(name, file_object):
    return _with_timestamp(name, file_object)