import os
import json
import datetime
import itertools
from sequences.models import *
from django.db.models import Q
from sequences.api.tasks import *
from django.utils import timezone
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .custom_serializer import CustomSerializer
from django_celery_results.models import TaskResult
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, generics, status

User 					= get_user_model()
Metadata_objects 		= Metadata_Handler.objects.all()

class UserMetadataStatsSerializer(CustomSerializer):
	class Meta:
		model  = Metadata_Handler
		fields = [
			'user'
		]

	def validate(self, value):
		metadata_qs = Metadata_Handler.objects.all()
		if(metadata_qs.count() > 0):
			temp = {}
			return_dict = {}
			for i in metadata_qs:
				if(not i.user.username in list(temp.keys())):
					temp[i.user.username] = []
				temp[i.user.username].append(i.metadata)
			for k,v in temp.items():
				return_dict[k] = len(list(itertools.chain(*v)))
			return return_dict
		return {'message': 'No Data Found'}


class UserMetadataStatsAPI(generics.GenericAPIView):
	queryset                = Metadata_objects
	serializer_class        = UserMetadataStatsSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(not bool(request.data)):
			serializer = self.get_serializer(data = request.data)
			if(serializer.is_valid()):
				return Response(serializer.object)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)

class UserMetadataStateStatsSerializer(CustomSerializer):
	class Meta:
		model  = Metadata_Handler
		fields = [
			'user'
		]

	def validate(self, value):
		return get_state_info()


class UserMetadataStateStatsAPI(generics.GenericAPIView):
	queryset                = Metadata_objects
	serializer_class        = UserMetadataStateStatsSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(not bool(request.data)):
			serializer = self.get_serializer(data = request.data)
			if(serializer.is_valid()):
				return Response(serializer.object)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)
