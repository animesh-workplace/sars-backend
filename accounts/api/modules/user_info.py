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
		fields = [
			'city',
			'email',
			'state',
			'address',
			'pin_code',
			'last_name',
			'institute',
			'first_name',
		]

	def validate(self, data):
		request     = self.context['request'].data
		username    = self.context['request'].user
		city        = request.get('city')
		email       = request.get('email')
		state       = request.get('state')
		address     = request.get('address')
		pin_code    = request.get('pin_code')
		last_name   = request.get('last_name')
		institute   = request.get('institute')
		first_name  = request.get('first_name')

		return_dict = {
			'username': username
		}

		if(city != None):
			return_dict['city'] = city
		if(email != None):
			return_dict['email'] = email
		if(state != None):
			return_dict['state'] = state
		if(address != None):
			return_dict['address'] = address
		if(pin_code != None):
			return_dict['pin_code'] = pin_code
		if(last_name != None):
			return_dict['last_name'] = last_name
		if(institute != None):
			return_dict['institute'] = institute
		if(first_name != None):
			return_dict['first_name'] = first_name

		return return_dict

	def update(self, validated_data):
		update_context = list(validated_data.keys())
		username = validated_data[update_context.pop(0)]
		qs = User.objects.filter(Q(username__iexact=username)).distinct()
		if(qs.count() == 1):
			user_obj = qs.first()
			if(user_obj.is_active):
				for i in update_context:
					setattr(user_obj, i, validated_data[i])
				user_obj.save()
				return user_obj
			raise serializers.ValidationError({'message': 'User Inactive'})
		raise serializers.ValidationError({'message': 'Invalid Credentials'})

class InfoAPIView(generics.GenericAPIView):
	queryset                = User.objects.all()
	serializer_class        = UserInfoSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(request.user.is_authenticated):
			if(not bool(request.data)):
				username = request.user
				qs = User.objects.filter(Q(username__iexact=username)).distinct()
				if(qs.count() == 1):
					user_obj = qs.first()
					return Response({
						'city'        : user_obj.city,
						'email'       : user_obj.email,
						'state'       : user_obj.state,
						'address'     : user_obj.address,
						'pin_code'    : user_obj.pin_code,
						'username'    : user_obj.username,
						'last_name'   : user_obj.last_name,
						'institute'   : user_obj.institute,
						'first_name'  : user_obj.first_name,
						'joining_date': user_obj.date_joined,
					})
				return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
			return Response({'message': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Not Authenticated'}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, *args, **kwargs):
		if(request.user.is_authenticated):
			if(bool(request.data)):
				serializer = self.get_serializer(data = request.data)
				if(serializer.is_valid()):
					serializer.update(serializer.validated_data)
					return Response({'message': 'Update Successful'})
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			return Response({'message': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Not Authenticated'}, status=status.HTTP_400_BAD_REQUEST)

