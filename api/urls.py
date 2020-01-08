from django.urls import include, path, re_path
from django.conf.urls import url
from rest_framework.authtoken import views

# /api/login/
# ACCEPTS 'username', 'password'
# RETURNS "token":"kael45637ghghdu" (fake token)

# /api/registration/ 
# ACCEPTS 'username', 'password1', 'password2'
# RETURN "key":"kael45637ghghdu" (fake token/key)

urlpatterns = [
    re_path(r'^login/', views.obtain_auth_token),
    path('registration/', include('rest_auth.registration.urls')),
]
