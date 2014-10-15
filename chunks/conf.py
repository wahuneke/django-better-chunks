# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings as _settings

DEFAULTS = {
    # The default cache timeout to use for chunks. 0 == no cache
    'CHUNKS_CACHE_TIMEOUT': 0,

    # If the chunks context processor runs for context, then these chunks will be
    # automatically retrieved and placed in the context
    'CHUNKS_COMMON_CHUNKS': [],

    # If CHUNKS_COMMON_CHUNKS is defined and context processor is used, you can optionally
    # put all the chunk variables into a "namespace" so they'll be less likely to stomp
    # existing context variables
    # If this setting is None, then common chunks will go straight into context main namespace
    # If setting is not None, then common chunks go into a dictionary context variable with this name
    'CHUNKS_COMMON_NAMESPACE': 'CHUNKS',
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
