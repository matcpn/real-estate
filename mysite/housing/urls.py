from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from . import views

admin.autodiscover()

app_name = 'housing'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^subdivision/$', views.subdivision, name='subdivision'),
    url(r'^house/$', views.house, name='house'),
    url(r'^select_house/$', views.select_house, name='select_house'),
    url(r'^select_feature/$', views.select_feature, name='select_feature'),
    url(r'^select_kitchen_material/$', views.select_kitchen_material, name='select_kitchen_material'),
    url(r'^select_bathroom_material/$', views.select_bathroom_material, name='select_bathroom_material'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
