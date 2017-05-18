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
    url(r'^lot/$', views.lot, name='lot'),
    url(r'^house/$', views.house, name='house'),
    url(r'^room_types/$', views.select_house, name='room_types'),
    url(r'^select_feature/$', views.select_feature, name='select_feature'),
    url(r'^select_room_upgrade/$', views.select_room_upgrade, name='select_room_upgrade'),
    url(r'^login/$', views.login, name="login"),
    url(r'^authenticate_user/$', views.authenticate_user, name="authenticate_user"),
    url(r'^create_user/$', views.create_user, name="create_user"),
    url(r'^logout_view/$', views.logout_view, name="logout_view"),
    url(r'^select_room_type/$', views.select_room_type, name="select_room_type"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
