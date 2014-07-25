from rest_framework.renderers import BrowsableAPIRenderer, StaticHTMLRenderer


class CalamariBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        if view.get_view_name() == 'Crush Map':
            return StaticHTMLRenderer()
        else:
            renderer = super(CalamariBrowsableAPIRenderer, self).get_default_renderer(view)
            return renderer
