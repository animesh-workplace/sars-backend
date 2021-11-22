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

class UserInfoSerializer(CustomSerializer):
	class Meta:
		model  = User

	def validate(self, data):
		request     = self.context['request'].data
		username    = self.context['request'].user
		qs = User.objects.filter(Q(username__iexact = username) | Q(email__iexact = username)).distinct()
		if(qs.count() == 1):
			user_obj = qs.first()
			if(user_obj.is_active):
				return_dict = {
					'export'	: user_obj.export,
					'username'	: username.username,
					'download'	: user_obj.download,
				}
				return return_dict
			raise serializers.ValidationError({'message': 'User Inactive'})
		raise serializers.ValidationError({'message': 'Invalid Credentials'})

		return return_dict

class InfoAPIView(generics.GenericAPIView):
	queryset                = User.objects.all()
	serializer_class        = UserInfoSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(request.user.is_authenticated):
			if(not bool(request.data)):
				serializer = self.get_serializer(data = request.data)
				if(serializer.is_valid()):
					return Response(serializer.object)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			return Response({'message': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Not Authenticated'}, status=status.HTTP_400_BAD_REQUEST)

