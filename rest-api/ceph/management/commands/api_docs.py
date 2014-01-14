from collections import defaultdict
from django.core.management.base import NoArgsCommand
import importlib
from jinja2 import Environment
import re
import rest_framework.viewsets
import traceback
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
import sys


class DocviewSetMixin(rest_framework.viewsets.ViewSetMixin):
    @classmethod
    def as_view(cls, actions=None, **initkwargs):
        view = super(DocviewSetMixin, cls).as_view(actions, **initkwargs)
        view._actions = actions
        return view


rest_framework.viewsets.ViewSetMixin = DocviewSetMixin

# >>> RsT table code borrowed from http://stackoverflow.com/a/17203834/99876


def make_table(grid):
    max_cols = [max(out) for out in map(list, zip(*[[len(item) for item in row] for row in grid]))]
    rst = table_div(max_cols, 1)

    for i, row in enumerate(grid):
        header_flag = False
        if i == 0 or i == len(grid) - 1:
            header_flag = True
        rst += normalize_row(row, max_cols)
        rst += table_div(max_cols, header_flag)
    return rst


def table_div(max_cols, header_flag=1):
    out = ""
    if header_flag == 1:
        style = "="
    else:
        style = "-"

    for max_col in max_cols:
        out += max_col * style + " "

    out += "\n"
    return out


def normalize_row(row, max_cols):
    r = ""
    for i, max_col in enumerate(max_cols):
        r += row[i] + (max_col - len(row[i]) + 1) * " "

    return r + "\n"
# <<< RsT table code borrowed from http://stackoverflow.com/a/17203834/99876


PAGE_TEMPLATE = """
API resources
=============

URL summary
-----------

{{url_summary_rst}}

API reference
-------------

{{resources_rst}}

"""


RESOURCE_TEMPLATE = """
{{name}}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{{help_text}}

URLs
____

{{url_table}}

Fields
______

{{field_table}}

"""


VERBS = ["GET", "PUT", "POST", "PATCH", "DELETE"]


def _url_pattern_methods(url_pattern):
    view_class = url_pattern.callback.cls

    if hasattr(url_pattern.callback, '_actions'):
        # An APIViewSet
        methods = [k.upper() for k in url_pattern.callback._actions.keys()]
    else:
        methods = view_class().allowed_methods

    if not methods:
        # A view that isn't using django rest framework?
        raise RuntimeError("No methods for url %s" % url_pattern.regex.pattern)

    return methods


def _pretty_url(prefix, url_regex):
    """
    Convert a URL regex into something prettier

    ^server/(?P<pk>[^/]+)$ becomes server/<pk>
    """
    url = prefix + url_regex.strip("^$")
    url = re.sub("\(.+?<(.+?)>.+?\)", "<\\1>", url)
    return "``%s``" % url


def _find_prefix(toplevel_mod, sub_mod):
    """
    Find the URL prefix of sub_mod in toplevel_mod
    """
    for toplevel_pattern in importlib.import_module(toplevel_mod).urlpatterns:
        if isinstance(toplevel_pattern, RegexURLResolver):
            if toplevel_pattern.urlconf_name.__name__ == sub_mod:
                regex_str = toplevel_pattern.regex.pattern
                return regex_str.strip("^")

    raise RuntimeError("'%s' not included in '%s', cannot find prefix" % (sub_mod, toplevel_mod))


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            self.gen_docs()
        except:
            print >>sys.stderr, traceback.format_exc()
            raise

    def gen_docs(self):
        url_module = 'ceph.urls.v2'

        view_to_url_patterns = defaultdict(list)

        def parse_urls(urls):
            for url_pattern in urls:
                if isinstance(url_pattern, RegexURLResolver):
                    parse_urls(url_pattern.urlconf_module)
                elif isinstance(url_pattern, RegexURLPattern):
                    if url_pattern.regex.pattern.endswith('\.(?P<format>[a-z]+)$'):
                        # Suppress the .<format> urls that rest_framework generates
                        continue

                    if hasattr(url_pattern.callback, 'cls'):
                        # This is a rest_framework as_view wrapper
                        view_cls = url_pattern.callback.cls
                        view_to_url_patterns[view_cls].append(url_pattern)

        prefix = _find_prefix("calamari_web.urls", url_module)
        parse_urls(importlib.import_module(url_module).urlpatterns)

        view_to_url_patterns = sorted(view_to_url_patterns.items(), cmp=lambda x, y: cmp(x[0].__name__, y[0].__name__))

        resources_rst = ""
        for view, url_patterns in view_to_url_patterns:
            class_name = view.__name__.split(".")[-1]
            name = view().metadata(None)['name']
            if class_name == "APIRoot":
                continue

            if view.__doc__:
                view_help_text = view.__doc__
            else:
                view_help_text = "*No description available*"

            url_table = [["URL"] + VERBS]
            for url_pattern in url_patterns:
                methods = _url_pattern_methods(url_pattern)

                row = [_pretty_url(prefix, url_pattern.regex.pattern)]
                for v in VERBS:
                    if v in methods:
                        row.append("Yes")
                    else:
                        row.append("")
                url_table.append(row)

            url_table_rst = make_table(url_table)

            if hasattr(view, 'serializer_class') and view.serializer_class:
                field_table = [["Name", "Type", "Readonly", "Description"]]
                fields = view.serializer_class().get_fields()
                for field_name, field in fields.items():
                    if hasattr(field, 'help_text'):
                        field_help_text = field.help_text
                    else:
                        field_help_text = ""
                    field_table.append([field_name, field.type_label, str(field.read_only), field_help_text])
                field_table_rst = make_table(field_table)
            else:
                field_table_rst = "*No field data available*"

            resource_rst = Environment().from_string(RESOURCE_TEMPLATE).render(
                name=name,
                help_text=view_help_text,
                field_table=field_table_rst,
                url_table=url_table_rst
            )

            resources_rst += resource_rst

        url_table = [["URL"] + VERBS]
        for view, url_patterns in view_to_url_patterns:
            for url_pattern in url_patterns:
                methods = _url_pattern_methods(url_pattern)
                row = [_pretty_url(prefix, url_pattern.regex.pattern)]
                for v in VERBS:
                    if v in methods:
                        row.append("Yes")
                    else:
                        row.append("")
                url_table.append(row)

        urls_table_rst = make_table(url_table)

        print Environment().from_string(PAGE_TEMPLATE).render(resources_rst=resources_rst, url_summary_rst=urls_table_rst)
