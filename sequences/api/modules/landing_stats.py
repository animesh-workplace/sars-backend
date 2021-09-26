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

class LandingStatsSerializer(CustomSerializer):
	class Meta:
		model  = Frontend_Handler
		fields = [
			'user'
		]

	def validate(self, value):
		return get_dashboard()


class LandingStatsAPI(generics.GenericAPIView):
	queryset                = Frontend_Handler
	serializer_class        = LandingStatsSerializer
	permission_classes      = []

	def post(self, request, *args, **kwargs):
		if(not bool(request.data)):
			serializer = self.get_serializer(data = request.data)
			if(serializer.is_valid()):
				return Response(serializer.object)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'message': 'Invalid Payload'}, status=status.HTTP_400_BAD_REQUEST)

