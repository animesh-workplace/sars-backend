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

class UserPasswordUpdateSerializer(CustomSerializer):
	old_password            = serializers.CharField(max_length=150)
	new_password            = serializers.CharField(max_length=150)
	class Meta:
		model  = User
		fields = [
			'old_password',
			'new_password'
		]
		extra_kwargs    = {
			'old_password': {'write_only': True},
			'new_password': {'write_only': True}
		}

	def validate(self, data):
		request         = self.context['request'].data
		username        = self.context['request'].user
		old_password    = request.get('old_password')
		new_password    = request.get('new_password')
		qs = User.objects.filter(Q(username__iexact=username)).distinct()
		if(qs.count() == 1):
			user_obj = qs.first()
			if(user_obj.is_active):
				if(user_obj.check_password(old_password)):
					user_obj.set_password(new_password)
					user_obj.save()
					return data
				raise serializers.ValidationError({'message': 'Invalid Credentials'})
			raise serializers.ValidationError({'message': 'User Inactive'})
		raise serializers.ValidationError({'message': 'Invalid Credentials'})

class PasswordUpdateAPIView(generics.CreateAPIView):
	queryset                = User.objects.all()
	serializer_class        = UserPasswordUpdateSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(request.user.is_authenticated):
			serializer = self.get_serializer(data = request.data)
			if(serializer.is_valid()):
				return Response({'message': 'Password Change Successful'})
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Not Authenticated'}, status=status.HTTP_400_BAD_REQUEST)

