from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from . import views

app_name = 'chats'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create_board/$', views.create_board, name='create_board'),
    url(r'^(?P<board_id>[0-9]+)/$', views.board, name='board'),
    url(r'^(?P<board_id>[0-9]+)/post$', views.post_message, name='post_message'),
    url(r'^(?P<board_id>[0-9]+)/get$', views.get_message, name='get_message'),
    url(r'^(?P<board_id>[0-9]+)/status$', views.get_message, name='get_status'),
    url(r'^making_tomb/$', views.make_tomb, name='make_tomb'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
