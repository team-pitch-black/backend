from django.urls import include, path
from django.conf.urls import url

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('registration/', include('rest_auth.registration.urls')),
]
