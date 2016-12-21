import logging

logger = logging.getLogger('utils.path_util')


def path_with_timestamp(file_object):
    time = file_object.etag
    split = file_object.path.rsplit('.', 1)
    if len(split) == 1:
        return '{}_({})'.format(split[0], time)
    elif len(split) == 2:
        return '{}_({}).{}'.format(split[0], time, split[1])
    else:
        logger.warn('Could not format path with timestamp for file {}'.format(file_object.path))
        return ''
