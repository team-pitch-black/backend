from django.conf.urls import url
from . import api

urlpatterns = [
    url('map', api.get_map),
    url('init', api.initialize),
    url('move', api.move),
    url('say', api.say),
]