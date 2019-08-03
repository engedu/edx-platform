"""
Course API URLs
"""
from .views import *
from django.conf.urls import url

urlpatterns = [
    url(r'^line-login', line_login),
    url(r'^revoke_token', revoke_token),
    url(r'^callback', callback),
    url(r'^complete', complete, name='complete'),
    url(r'^post_message', post_message),
    url(r'^check_status', check_status),
    url(r'^save_config', save_config)
]
