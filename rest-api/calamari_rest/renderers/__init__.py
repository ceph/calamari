from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer, StaticHTMLRenderer


class CalamariBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        if view.get_view_name() == 'Crush Map':
            return StaticHTMLRenderer()
        else:
            return JSONRenderer()
