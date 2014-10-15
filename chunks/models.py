from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import template
from django.core.cache import cache


class Chunk(models.Model):
    """
    A Chunk is a piece of content associated
    with a unique key that can be inserted into
    any template with the use of a special template
    tag
    """
    CACHE_PREFIX = "chunk_"
    LANG_CODE_VAR = template.Variable('LANGUAGE_CODE')

    key = models.CharField(help_text="A unique name for this chunk of content", blank=False, max_length=255)
    content = models.TextField(blank=True)
    lang_code = models.CharField(verbose_name=_(u"language"), default=settings.LANGUAGE_CODE,
                                 help_text="Language code, if this chunk is translated. Same format as LANGUAGE_CODE "
                                           "setting, e.g. sv-se, or de-de, etc.", blank=True, max_length=5)
    site = models.ForeignKey(Site, default=settings.SITE_ID, blank=True, null=True, verbose_name=_('site'))

    class Meta(object):
        unique_together = (('key', 'lang_code', 'site'),)

    @classmethod
    def get_chunk(cls, name, context=None, cache_time=0):
        """
        Get the named string chunk
        :param name: name of chunk to retrieve
        :param context: request context (if available) so we can get language code
        :param cache_time: number of seconds this value can be cached
        """

        if context is None:
            lang = settings.LANGUAGE_CODE
        else:
            try:
                lang = cls.LANG_CODE_VAR.resolve(context)
            except template.VariableDoesNotExist:
                # no LANGUAGE_CODE variable found in context, just return ''
                return ''

        site = Site.objects.get_current().id  # Django caches get_current()
        cache_key = cls.CACHE_PREFIX + name + lang + str(site)
        content = cache.get(cache_key)
        if content is None:
            try:
                chunk = cls.objects.get(key=name, lang_code=lang, site=site)
                content = chunk.content
            except Chunk.DoesNotExist:
                # cache missing models as empty chunk strings
                content = ''
            if cache_time > 0:
                # don't even call cache if timeout is 0
                cache.set(cache_key, content, cache_time)
        return content

    def __unicode__(self):
        return u"%s" % (self.key,)
