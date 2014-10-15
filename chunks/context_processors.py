from chunks.conf import settings
from chunks.models import Chunk
import re


def common_chunks(request):
    def make_chunk_tuple(chunk_key):
        """
        Helper to make a tuple that can be turned into a dictionary to add to context
        """
        # Some chunk keys are not appropriate as template variable names. fix those
        var_name = re.sub(r'[ \-,\.;]', '_', chunk_key)
        if hasattr(request, 'LANGUAGE_CODE'):
            return var_name, Chunk.get_chunk(chunk_key, lang=request.LANGUAGE_CODE)
        else:
            return var_name, Chunk.get_chunk(chunk_key)

    ctx = dict(map(make_chunk_tuple, settings.CHUNKS_COMMON_CHUNKS))

    if settings.CHUNKS_COMMON_NAMESPACE:
        return {settings.CHUNKS_COMMON_NAMESPACE: ctx}
    else:
        return ctx
