from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('bank.views',
    # Example:
    # (r'^rpgmanager_django/', include('rpgmanager_django.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^lancamentos/(?P<conta_id>\d+)/$', 'showConta'),
    (r'^lancamentos/(?P<conta_id>\d+)/(?P<year>\d+)/$', 'showConta'),
    (r'^lancamentos/(?P<conta_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', 'showConta'),
    (r'^transacoes/(?P<transacao_id>\d+)/confirmar/$', 'confirmarTransacao'),
    (r'^contas/(?P<user_id>\d+)/$', 'showContas'),
)
