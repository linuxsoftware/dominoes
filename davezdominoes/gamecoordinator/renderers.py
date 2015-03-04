# ------------------------------------------------------------------------------
# Better rendering support
# Based on https://gist.github.com/jvanasco/6529591
# ------------------------------------------------------------------------------
import logging
log = logging.getLogger(__name__)

def gif_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        if request:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'image/gif'
        return value
    return _render

def png_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        if request:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'image/png'
        return value
    return _render

def includeme(config):
    """Install our own renderers."""
    config.add_renderer('gif',   gif_renderer_factory)
    config.add_renderer('png',   png_renderer_factory)

    log.info("renderers added")

