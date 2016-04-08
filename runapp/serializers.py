from rest_framework import serializers
from .models import RawData, Submission, SubmissionFold


class RawDataSerializer(serializers.ModelSerializer):
    """
    Serializer for the RawData model with all fields
    """
    class Meta:
        model = RawData
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Submission model with all fields
    """
    class Meta:
        model = Submission
        fields = '__all__'


class SubmissionFoldSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubmissionFold model with all fields
    """
    class Meta:
        model = SubmissionFold
        fields = '__all__'


class TestPredSubmissionFoldSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubmissionFold model with the id, the predictions on the
    test dataset, and the model performances
    """
    class Meta:
        model = SubmissionFold
        fields = ('databoard_sf_id', 'test_predictions', 'train_time',
                  'validation_time', 'test_time', 'train_cpu_time',
                  'train_memory', 'test_cpu_time', 'test_memory')
