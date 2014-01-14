from collections import defaultdict
from django.core.management.base import NoArgsCommand
import importlib
import rest_framework.viewsets
import traceback
from django.core.urlresolvers import (RegexURLPattern,
    RegexURLResolver, LocaleRegexURLResolver)

class DocviewSetMixin(rest_framework.viewsets.ViewSetMixin):
    @classmethod
    def as_view(cls, actions=None, **initkwargs):
        view = super(DocviewSetMixin, cls).as_view(actions, **initkwargs)
        view._actions = actions
        return view

rest_framework.viewsets.ViewSetMixin = DocviewSetMixin


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            self.gen_docs()
        except:
            print traceback.format_exc()

    def gen_docs(self):
        url_mods = ['ceph.urls.v2']

        view_to_url_patterns = defaultdict(list)
        def parse_urls(urls):
            for url_pattern in urls:
                if isinstance(url_pattern, RegexURLResolver):
                    parse_urls(url_pattern.urlconf_module)
                elif isinstance(url_pattern, RegexURLPattern):
                    if hasattr(url_pattern.callback, 'cls'):
                        regex = url_pattern.regex
                        # This is a rest_framework as_view wrapper
                        view_cls = url_pattern.callback.cls
                        view_to_url_patterns[view_cls].append(url_pattern)
                        #print dir(view_cls)
                        #print "%s: %s %s" % (view_cls.__name__, view_cls.http_method_names, regex.pattern)

        for url_mod in url_mods:
            parse_urls(importlib.import_module(url_mod).urlpatterns)

        for view, url_patterns in view_to_url_patterns.items():
            if view.__name__.split(".")[-1] != "ServerViewSet":
                # hack, debug this one alone
                continue

            print """{view_name} - {view_summary}
==================================================

""".format(view_name=view.__name__.split(".")[-1], view_summary="summary"),
            if view.__doc__:
                print """
                {view_docstring}
    """.format(view_docstring=view.__doc__)
            print """URL patterns:

""",
            for url_pattern in url_patterns:
                if url_pattern.regex.pattern.endswith('\.(?P<format>[a-z]+)$'):
                    # Suppress the .<format> urls that rest_framework generates
                    continue
                if hasattr(url_pattern.callback, '_actions'):
                    methods = [k.upper() for k in url_pattern.callback._actions.keys()]
                else:
                    methods = ['unknown']
                print """- {methods} {pattern}
""".format(methods=methods, pattern=url_pattern.regex.pattern),
            print "\n",

            print """Fields
------

"""
            if hasattr(view, 'serializer'):
                fields = view.serializer().get_fields()
                for field_name, field in fields.items():
                    print """{field_name}
  {field_desc}

""".format(field_name=field_name, field_desc=field.type_label),
            else:
                print "No field metadata available"