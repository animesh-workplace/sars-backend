from rest_framework import serializers

class CustomSerializer(serializers.Serializer):
    @property
    def object(self):
        return self.validated_data
