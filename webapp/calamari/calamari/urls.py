from django.conf.urls import patterns, include, url

from settings import STATIC_DOC_ROOT, DEBUG, GRAPHITE_API_PREFIX

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'calamari.views.home'),

    url(r'^api/v1/', include('ceph.urls')),
    url(r'^api/v1/auth/login', 'calamari.views.login'),
    url(r'^api/v1/auth/logout', 'calamari.views.logout'),
    url(r'^api/v1/auth2/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/info', 'calamari.views.info'),

    url(r'^admin/(?P<path>.*)$', 'calamari.views.serve_dir_or_index',
        {'document_root': '%s/admin/' % STATIC_DOC_ROOT}),

    url(r'^login/$', 'django.views.static.serve',
        {'document_root': '%s/login/' % STATIC_DOC_ROOT, 'path': "index.html"}),

    url(r'^login/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '%s/login/' % STATIC_DOC_ROOT}),

    url(r'^dashboard/(?P<path>.*)$', 'calamari.views.dashboard',
        {'document_root': '%s/dashboard/' % STATIC_DOC_ROOT},
        name='dashboard'),

    url(r'^render/?', include('graphite.render.urls')),
    url(r'^metrics/?', include('graphite.metrics.urls')),
    url(r'^%s/dashboard/?' % GRAPHITE_API_PREFIX.lstrip('/'), include('graphite.dashboard.urls')),
)

if DEBUG:
    # Graphite dashboard client code is not CSRF enabled, but we have
    # global CSRF protection enabled.  Make exceptions for the views
    # that the graphite dashboard wants to POST to.
    from django.views.decorators.csrf import csrf_exempt
    import inspect

    def patch_views(mod):
        for name, member in mod.__dict__.items():
            if inspect.isfunction(member):
                setattr(mod, name, csrf_exempt(member))
    import graphite.metrics.views
    import graphite.dashboard.views
    patch_views(graphite.metrics.views)
    patch_views(graphite.dashboard.views)
