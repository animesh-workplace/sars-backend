from django.conf.urls import url
from .modules.login import LoginAPIView
from .modules.user_info import InfoAPIView
from .modules.register import RegisterAPIView
from .modules.edit_password import PasswordUpdateAPIView
from rest_framework_jwt.views import refresh_jwt_token, obtain_jwt_token

urlpatterns = [
	url(r'^jwt/$', obtain_jwt_token),
	url(r'^jwt/refresh/$', refresh_jwt_token),
	url(r'^login/$', LoginAPIView.as_view(), name='login'),
	url(r'^user-info/$', InfoAPIView.as_view(), name='user-info'),
	url(r'^register/$', RegisterAPIView.as_view(), name='register'),
	url(r'^update-password/$', PasswordUpdateAPIView.as_view(), name='update-password'),
]
