from django.conf.urls import patterns, include, url

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

    # Examples:
    # url(r'^$', 'calamari.views.home', name='home'),
    # url(r'^calamari/', include('calamari.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^admin/(?P<path>.*)$', 'calamari.views.serve_dir_or_index',
        {'document_root': '/opt/calamari/webapp/content/admin/'}),

    url(r'^dashboard/(?P<path>.*)$', 'calamari.views.dashboard',
        {'document_root': '/opt/calamari/webapp/content/dashboard/'}, name='dashboard'),
)
