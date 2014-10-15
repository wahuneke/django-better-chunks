from django.contrib import admin
from django import forms
from models import Chunk


class ChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'content', 'lang_code', 'site', )
    list_filter = ('site', 'lang_code', )
    search_fields = ('key', 'content')
    list_editable = ('key', 'content', 'lang_code', 'site', )
    list_display_links = ('id', )
    actions = ('clone_chunks', )

    # If we dont do this, then the content column winds up being huge. We want it to be
    # easy to modify small chunks right from the main admin
    def get_changelist_form(self, request, **kwargs):
        class TheForm(forms.ModelForm):
            class Meta(object):
                model = Chunk
                widgets = {'content': forms.TextInput()}
        kwargs.setdefault('form', TheForm)
        return super(ChunkAdmin, self).get_changelist_form(request, **kwargs)

    def clone_chunks(self, request, queryset):
        """
        For each chunk object, take a look to make sure that chunks exist for the other sites. Create new chunk
        with identical content for other sites if doesnt already exist.
        """
        for chunk in queryset.all():
            chunk.clone_for_all_sites()

admin.site.register(Chunk, ChunkAdmin)
