import os
import datetime
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

class UserMetadataUploadSerializer(CustomSerializer):
	class Meta:
		model  = Metadata_Handler
		fields = [
			'user',
			'metadata'
		]

	def validate(self, value):
		user 		= self.context['request'].user
		request 	= self.context['request'].data
		metadata 	= request.get('metadata')
		qs = User.objects.filter(Q(username__iexact=user) | Q(email__iexact=user)).distinct()
		if(qs.count() == 1):
			user_obj = qs.first()
			if(user_obj.is_active):
				metadata_obj = Metadata_Handler(
					user 			= user_obj,
					metadata 		= metadata,
					submission_date = timezone.now()
				)
				metadata_obj.save()
				return {'message': 'Upload Successful'}
			raise serializers.ValidationError({'message': 'User Inactive'})
		raise serializers.ValidationError({'message': 'Invalid Credentials'})


class UserMetadataUploadAPI(generics.GenericAPIView):
	queryset                = Metadata_objects
	serializer_class        = UserMetadataUploadSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(request.user.is_authenticated):
			serializer = self.get_serializer(data = request.data)
			if(serializer.is_valid()):
				return Response(serializer.object)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Not Authenticated'}, status=status.HTTP_400_BAD_REQUEST)

