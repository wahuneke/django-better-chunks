from django import template
from django.db import models

register = template.Library()

Chunk = models.get_model('chunks', 'Chunk')


def do_get_chunk(parser, token):
    # split_contents() knows not to split quoted strings.
    tokens = token.split_contents()
    if len(tokens) == 2:
        tag_name, key = tokens
        cache_time = 0
    elif len(tokens) == 3:
        tag_name, key, cache_time = tokens
    else:
        raise template.TemplateSyntaxError, "%r tag should have either 2 or 3 arguments" % (tokens[0],)

    # Check to see if the key is properly double/single quoted
    if not (key[0] == key[-1] and key[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    # Send key (without quotes) and caching time
    return ChunkNode(key[1:-1], cache_time)
    

class ChunkNode(template.Node):
    def __init__(self, key, cache_time=0):
       self.key = key
       self.cache_time = int(cache_time)

    def render(self, context):
        return Chunk.get_chunk(self.key, context, self.cache_time)


register.tag('chunk', do_get_chunk)
