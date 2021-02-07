from django.db.models import Q
from accounts.api.tasks import *
from django.utils import timezone
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from .custom_serializer import CustomSerializer
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status, generics

User = get_user_model()

jwt_encode_handler 				= api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler 			= api_settings.JWT_PAYLOAD_HANDLER
jwt_response_payload_handler	= api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
expire_delta					= api_settings.JWT_REFRESH_EXPIRATION_DELTA

class UserRegisterSerializer(serializers.ModelSerializer):
	password2  = serializers.CharField(style={'input_type': 'password'}, write_only=True)
	class Meta:
		model   = User
		fields  = [
			'username',
			'password',
			'password2',
		]
		extra_kwargs    = {'password': {'write_only': True}}
		sequence        = ('username', 'is_active')

	def validate_username(self, value):
		qs = User.objects.filter(username__iexact=value)
		if qs.exists():
			raise serializers.ValidationError({'message': 'User with this username already exists'})
		return value

	def validate(self, data):
		pw  = data.get('password')
		pw2 = data.pop('password2')
		if pw != pw2:
			raise serializers.ValidationError({'message': 'Passwords must match'})
		return data

	def create(self, validated_data):
		user_obj = User(
				username    = validated_data.get('username'),
		)
		user_obj.set_password(validated_data.get('password'))
		user_obj.is_active = False
		user_obj.save()
		return user_obj

class RegisterAPIView(generics.CreateAPIView):
	queryset                = User.objects.all()
	serializer_class        = UserRegisterSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(not request.user.is_authenticated):
			self.create(request, *args, **kwargs)
			return Response({'message': 'Registered Successfully'})
		return Response({'message': 'Already Authenticated'}, status=status.HTTP_400_BAD_REQUEST)
