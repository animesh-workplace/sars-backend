import os
import datetime
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
File_objects 			= File_Handler.objects.all()

class UserFileUploadSerializer(CustomSerializer):
	class Meta:
		model  = File_Handler
		fields = [
			'metadata',
			'sequences'
		]

	def validate(self, value):
		user 		= self.context['request'].user
		request 	= self.context['request'].data
		metadata 	= request.get('metadata')
		sequences 	= request.get('sequences')

		if(metadata != None and sequences != None):
			qs = User.objects.filter(Q(username__iexact=user) | Q(email__iexact=user)).distinct()
			if(qs.count() == 1):
				user_obj 	= qs.first()
				if(user_obj.is_active):
					file_obj = File_Handler(
						user 	  = user,
						sequences = sequences,
						metadata  = metadata
					)
					file_obj.save()
					return value
				raise serializers.ValidationError({'message': 'User Inactive'})
			raise serializers.ValidationError({'message': 'Invalid Credentials'})
		raise serializers.ValidationError({'message': 'Required field not present'})

class UserFileUploadHandlerAPI(generics.CreateAPIView):
	queryset                = File_objects
	serializer_class        = UserFileUploadSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(request.user.is_authenticated):
			serializer = self.get_serializer(data = request.data)
			if(serializer.is_valid()):
				return Response({
					'message': 'File uploaded Successfully',
				})
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Not Authenticated'}, status=status.HTTP_400_BAD_REQUEST)

