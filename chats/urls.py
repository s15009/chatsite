from django.conf.urls import include, url

from . import views

app_name = 'chats'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create_board/$', views.create_board, name='create_board'),
    url(r'^(?P<board_id>[0-9]+)/$', views.board, name='board'),
    url(r'^(?P<board_id>[0-9]+)/post$', views.post_message, name='post_message'),
    url(r'^(?P<board_id>[0-9]+)/get$', views.get_message, name='get_message'),
]
