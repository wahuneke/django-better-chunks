from django.db import models
from django.contrib.sites.models import Site
from chunks.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import template
from django.core.cache import cache


# We export the settings symbol because it's hard/impossible to get that symbol from templatetags.chunks because
# that module has the same name as the chunks package and thus it is impossible to import chunks.conf from there ...
# I guess
__all__ = ['Chunk', 'settings', ]

# The variable name used in contexts that carry the language code
LANG_CODE_VAR = template.Variable('LANGUAGE_CODE')
# The variable name used in contexts that carry the site ID
SITE_ID_VAR = template.Variable('SITE_ID')


def deduce_site_lang(request=None, context=None):
    """
    If there is some way to get current site and or current language from the provided request and context, then return
    that as a tuple

    :param request: a request object
    :param context: a context object
    :return: site, lang_code
    """
    lang = site = None

    # Get language
    if not request is None and hasattr(request, "LANGUAGE_CODE"):
        # A language code in request gets first priority
        lang = request.LANGUAGE_CODE
    elif not context is None:
        # Language code in the context gets second priority
        try:
            lang = LANG_CODE_VAR.resolve(context)
        except template.VariableDoesNotExist:
            # no LANGUAGE_CODE variable found in context, just return ''
            lang = settings.LANGUAGE_CODE
    else:
        # We have no way to get language, just assume default language
        lang = settings.LANGUAGE_CODE

    # If there is a setting in the context then that overrides the "current site"
    if not context is None:
        try:
            site_id = SITE_ID_VAR.resolve(context)
            try:
                site = Site.objects.get(id=site_id)
            except Site.DoesNotExist:
                pass
        except template.VariableDoesNotExist:
            # no SITE_ID variable found in context, just go default
            pass

    if site is None:
        # Just default to using the "current" site
        site = Site.objects.get_current()

    return site, lang


class Chunk(models.Model):
    """
    A Chunk is a piece of content associated
    with a unique key that can be inserted into
    any template with the use of a special template
    tag
    """
    CACHE_PREFIX = "chunk_"

    key = models.CharField(help_text="A unique name for this chunk of content", blank=False, max_length=255)
    content = models.TextField(blank=True)
    lang_code = models.CharField(verbose_name=_(u"language"), default=settings.LANGUAGE_CODE,
                                 help_text="Language code, if this chunk is translated. Same format as LANGUAGE_CODE "
                                           "setting, e.g. sv-se, or de-de, etc.", blank=True, max_length=5)
    site = models.ForeignKey(Site, default=settings.SITE_ID, blank=True, null=True, verbose_name=_('site'))

    class Meta(object):
        unique_together = (('key', 'lang_code', 'site'),)

    @classmethod
    def get_chunk(cls, name, lang=None, request=None, context=None, cache_time=None, site=None):
        """
        Get the named string chunk
        :param name: name of chunk to retrieve
        :param lang: specify a language code here to manually set language, otherwise we'll try to read from context
        :param request: provide the HTTP request object if available
        :param context: request context (if available) so we can get language code
        :param cache_time: number of seconds this value can be cached
        :param site: if site is provided then we use that, otherwise, read current site
        """

        if cache_time is None:
            cache_time = settings.CHUNKS_CACHE_TIMEOUT

        site_suggested, lang_suggested = deduce_site_lang(request=request, context=context)

        lang = lang or lang_suggested
        site = site or site_suggested

        cache_key = cls.CACHE_PREFIX + name + lang + str(site.id)
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

    def clone_for_all_sites(self):
        """
        use the current chunk key and check for other chunks with same key for other sites. If there is any site
        that doesnt have this key then create a new chunk for that site using this key.

        This makes it easy to populate the database with all the chunks needed for each site
        """
        #TODO: I'm sure there's a faster way to do this
        # Sites that have this chunk key for current lang code
        have_key = Chunk.objects.filter(key=self.key, lang_code=self.lang_code).values_list('site_id', flat=True)
        other_sites = Site.objects.exclude(id__in=have_key)
        for site in other_sites:
            Chunk.objects.create(key=self.key, lang_code=self.lang_code, site=site, content=self.content)

    def __unicode__(self):
        return u"%s" % (self.key,)
