import os
import datetime
from sequences.models import *
from django.db.models import Q
from sequences.api.tasks import *
from django.utils import timezone
from rest_framework.response import Response
from django.utils.encoding import force_text
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
			'metadata',
			'timestamp'
		]

	def validate(self, value):
		user 		= self.context['request'].user
		request 	= self.context['request'].data
		metadata 	= request.get('metadata')
		timestamp 	= request.get('timestamp')
		if(user.is_authenticated):
			if(user.is_active):
				metadata_obj = Metadata_Handler(
					user 			= user,
					metadata 		= metadata,
					submission_date = timezone.now()
				)
				metadata_obj.save()
				user_info = {
					'username': user.username,
					'uploaded': len(metadata)
				}
				update_landing_data()
				send_email_upload(user_info)
				# create_config_file.delay(user_info)
				return {'message': 'Upload Successful'}
			raise serializers.ValidationError({'message': 'User Inactive'})
		raise serializers.ValidationError({'message': 'Not Authenticated'})


class UserMetadataUploadAPI(generics.GenericAPIView):
	queryset                = Metadata_objects
	serializer_class        = UserMetadataUploadSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		serializer = self.get_serializer(data = request.data)
		if(serializer.is_valid()):
			return Response(serializer.object)
		return Response({'message': serializer.errors['message'][0]}, status=status.HTTP_400_BAD_REQUEST)

