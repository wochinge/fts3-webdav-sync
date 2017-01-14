IGNORE_MODIFIED = 'ignore'
OVERWRITE_MODIFIED = 'overwrite'
KEEP_BOTH = 'keep_both'


class SynchronizationSetting(object):

    def __init__(self, config):
        self.strategy = config.get('action for modified file', IGNORE_MODIFIED)        self.interval = config.get('sync interval in minutes', 30) * 60
        self.interval = config.get('sync interval in minutes', 30) * 60
        self.dry_run = config.get('dry run', False)
