from django.urls import path

from . import views

urlpatterns = [
    path('get_links', views.get_links, name='get_links'),

] 