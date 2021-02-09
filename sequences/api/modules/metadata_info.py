import os
import json
import datetime
import itertools
from sequences.models import *
from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .custom_serializer import CustomSerializer
from django_celery_results.models import TaskResult
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, generics, status

User 					= get_user_model()
Metadata_objects 		= Metadata_Handler.objects.all()

class UserMetadataInfoSerializer(CustomSerializer):
	class Meta:
		model  = Metadata_Handler
		fields = [
			'user'
		]

	def validate(self, value):
		user = self.context['request'].user
		qs = User.objects.filter(Q(username__iexact=user) | Q(email__iexact=user)).distinct()
		if(qs.count() == 1):
			user_obj = qs.first()
			if(user_obj.is_active):
				metadata_qs = Metadata_Handler.objects.filter(Q(user=user_obj))
				if(metadata_qs.count() > 0):
					temp = []
					for index,i in enumerate(metadata_qs):
						temp.append(i.metadata)
					return_dict = itertools.chain(*temp)
					return return_dict
				return {'message': 'No Data Found'}
			raise serializers.ValidationError({'message': 'User Inactive'})
		raise serializers.ValidationError({'message': 'Invalid Credentials'})


class UserMetadataInfoAPI(generics.GenericAPIView):
	queryset                = Metadata_objects
	serializer_class        = UserMetadataInfoSerializer
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

