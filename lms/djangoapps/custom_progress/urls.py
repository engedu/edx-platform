from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    url(r'v1/', views.show_progress, name='custom_progress_view'),
]
