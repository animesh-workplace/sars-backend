from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from .custom_serializer import CustomSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status, generics

User = get_user_model()

jwt_encode_handler 				= api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler 			= api_settings.JWT_PAYLOAD_HANDLER
jwt_response_payload_handler	= api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
expire_delta					= api_settings.JWT_REFRESH_EXPIRATION_DELTA

class UserLoginSerializer(CustomSerializer):
	username			= serializers.CharField(max_length=150)
	password			= serializers.CharField(max_length=150)
	class Meta:
		model  = User
		fields = [
			'username',
			'password'
		]

	def validate(self, data):
		request 	= self.context['request'].data
		username	= request.get('username')
		password	= request.get('password')
		if(username != None and password != None):
			qs = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).distinct()
			if(qs.count() == 1):
				user_obj = qs.first()
				if(user_obj.check_password(password)):
					if(user_obj.is_active):
						user_obj.last_login = timezone.now()
						user_obj.save()
						payload = jwt_payload_handler(user_obj)
						token = jwt_encode_handler(payload)
						return {
							'username'  : username,
							'token'	 : token,
							'expires'   : timezone.now() + api_settings.JWT_EXPIRATION_DELTA
						}
					raise serializers.ValidationError({'message' :'User inactive'})
				raise serializers.ValidationError({'message' :'Invalid Credentials'})
			raise serializers.ValidationError({'message' :'Invalid Credentials'})
		raise serializers.ValidationError({'message' :'Required field not present'})

class LoginAPIView(generics.CreateAPIView):
	queryset				= User.objects.all()
	serializer_class		= UserLoginSerializer
	permission_classes		= []

	def post(self, request, *args, **kwargs):
		if(not request.user.is_authenticated):
			serializer = self.get_serializer(data = request.data)
			if(serializer.is_valid()):
				token = serializer.object.get('token')
				response = Response(serializer.object)
				if(api_settings.JWT_AUTH_COOKIE):
					expiration = (timezone.now() + api_settings.JWT_EXPIRATION_DELTA)
					response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, expires=expiration, httponly=False, secure=False)
					return response
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Already Authenticated'}, status=status.HTTP_400_BAD_REQUEST)

