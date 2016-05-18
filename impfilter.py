# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals
)

from beets.plugins import BeetsPlugin
from beets.importer import action
from beets.library import parse_query_string
from beets.library import Item
from beets.library import Album


__author__ = 'Joker.Qyou@gmail.com'
__version__ = '0.1'
__doc__ = '''
Based on https://git.io/vr81H, original author: baobab@heresiarch.info
'''


def summary(task):
    """Given an ImportTask, produce a short string identifying the
    object.
    """
    if task.is_album:
        return u'Album {1} by artist: {0}'.format(
            task.cur_artist or 'Unknown', task.cur_album or 'Unknown'
        )
    else:
        return u'Track {1} by artist: {0}'.format(
            task.item.artist or 'Unknown', task.item.title or 'Unknown'
        )


class ImpFilterPlugin(BeetsPlugin):
    def __init__(self):
        super(ImpFilterPlugin, self).__init__()
        self.register_listener(
            'import_task_created',
            self.handle_import_task_created
        )
        self.config.add({
            'warn': [],
            'skip': [],
        })

    @classmethod
    def hit(cls, task, action_patterns):
        if action_patterns:
            for query_string in action_patterns:
                query, _ = parse_query_string(
                    query_string,
                    Album if task.is_album else Item,
                )
                if any(query.match(item) for item in task.items):
                    return True
        return False

    def handle_import_task_created(self, session, task):
        skip_queries = self.config['skip'].as_str_seq()
        warn_queries = self.config['warn'].as_str_seq()

        if skip_queries or warn_queries:
            self._log.debug(u'processing')
            if self.hit(task, skip_queries):
                task.choice_flag = action.SKIP
                self._log.warn(u'skipped: {0}', summary(task))
                return
            if self.hit(task, warn_queries):
                self._log.warn(u'warning: {0}', summary(task))
        else:
            self._log.debug(u'nothing to do')
