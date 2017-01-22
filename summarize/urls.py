from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /summarize/
    url(r'^$', views.index, name='index'),
    # ex: /summarize/detatils/
    url(r'^(details/)', views.detail, name='detail'),

    # ex: /summarize/pop9118/
    url(r'^(pop9118/)', views.populateData, name='populateData'),
]