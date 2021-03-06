from django import template
from django.db import models
from django.db.models.loading import get_app

register = template.Library()

Chunk = models.get_model('chunks', 'Chunk')
# This silliness is necessary because the current file has the same name as the package that we need
# I just want to import chunks.conf.settings but I think this is the only way to do it
chunks_models = get_app('chunks')
settings = chunks_models.settings


def do_get_chunk(parser, token):
    # split_contents() knows not to split quoted strings.
    tokens = token.split_contents()
    cnt = len(tokens)
    if cnt == 2:
        # Called with just a chunk key
        tag_name, key = tokens
        cache_time = settings.CHUNKS_CACHE_TIMEOUT
        output_variable = None
    elif cnt == 3:
        # Called with chunk key and cache time
        tag_name, key, cache_time = tokens
        output_variable = None
    elif cnt == 4 and tokens[-2] == 'as':
        # Called with variable assignment but no cache time
        tag_name, key, _as, output_variable = tokens
        cache_time = settings.CHUNKS_CACHE_TIMEOUT
    elif cnt == 5 and tokens[-2] == 'as':
        # Called with variable assignment and cache time
        tag_name, key, cache_time, _as, output_variable = tokens
    else:
        raise template.TemplateSyntaxError, "%r tag should have either 2 or 3 arguments" % (tokens[0],)

    # Check to see if the key is properly double/single quoted
    if not (key[0] == key[-1] and key[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    # Send key (without quotes) and caching time
    return ChunkNode(key[1:-1], cache_time, output_variable)
    

class ChunkNode(template.Node):
    def __init__(self, key, cache_time=settings.CHUNKS_CACHE_TIMEOUT, output_variable=None):
        self.key = key
        self.output_variable = output_variable
        self.cache_time = int(cache_time)

    def render(self, context):
        content = Chunk.get_chunk(self.key, context=context, cache_time=self.cache_time)
        if self.output_variable is None:
            return content
        else:
            context[self.output_variable] = content
            return ''

register.tag('chunk', do_get_chunk)
