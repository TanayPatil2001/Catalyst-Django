from rest_framework import serializers
from .models import LargeFile

class LargeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LargeFile
        fields = '__all__'
