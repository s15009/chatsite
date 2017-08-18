from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'twitter'
urlpatterns = [
    url(r'^$', views.home, name='home'),
	url(r'^login/$', auth_views.login,{'template_name': 'twitter/login.html',},name='login'),
        url(r'^logout/$',auth_views.logout, {'template_name': 'twitter/logged_out.html'}, name='logout'),
	url(r'^create/$', views.create, name='create'),
	url(r'^new/$', views.new, name='new'),
]
