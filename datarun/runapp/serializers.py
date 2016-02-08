from rest_framework import serializers
from .models import RawData, Submission, SubmissionFold


class RawDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawData
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


class SubmissionFoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionFold
        fields = '__all__'
