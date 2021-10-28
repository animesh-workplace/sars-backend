from .modules.login import LoginAPIView
from .modules.user_info import InfoAPIView
from .modules.register import RegisterAPIView
from django.urls import path, include, re_path
from .modules.edit_password import PasswordUpdateAPIView
from rest_framework_jwt.views import refresh_jwt_token, obtain_jwt_token

urlpatterns = [
	path('jwt/', obtain_jwt_token),
	path('jwt/refresh/', refresh_jwt_token),
	path('login/', LoginAPIView.as_view(), name='login'),
	path('user-info/', InfoAPIView.as_view(), name='user-info'),
	path('register/', RegisterAPIView.as_view(), name='register'),
	path('update-password/', PasswordUpdateAPIView.as_view(), name='update-password'),
]
