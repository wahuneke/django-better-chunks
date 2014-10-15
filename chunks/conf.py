# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings as _settings

DEFAULTS = {
    # The default cache timeout to use for chunks. 0 == no cache
    'CHUNKS_CACHE_TIMEOUT': 0,
    # If the chunks context processor runs for context, then these chunks will be
    # automatically retrieved and placed in the context
    'CHUNKS_COMMON_CHUNKS': [],
}


class ChunksSettings(object):
    def __init__(self, wrapped_settings):
        self.wrapped_settings = wrapped_settings

    def __getattr__(self, name):
        if hasattr(self.wrapped_settings, name):
            return getattr(self.wrapped_settings, name)
        elif name in DEFAULTS:
            return DEFAULTS[name]
        else:
            raise AttributeError("'%s' setting not found" % name)

settings = ChunksSettings(_settings)
