IGNORE_MODIFIED = 'ignore'
OVERWRITE_MODIFIED = 'overwrite'
KEEP_BOTH = 'keep_both'


class SynchronizationSetting(object):

    def __init__(self, config):
        self.strategy = config.get('action for modified file', IGNORE_MODIFIED)