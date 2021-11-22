from django.urls import path
from .modules.login import LoginAPIView
from .modules.user_info import InfoAPIView
from .modules.register import RegisterAPIView
from .modules.edit_password import PasswordUpdateAPIView
from rest_framework_jwt.views import refresh_jwt_token, obtain_jwt_token

urlpatterns = [
	path('login/', LoginAPIView.as_view(), name='login'),
	path('user-info/', InfoAPIView.as_view(), name='user-info'),
]
