from rest_framework import serializers
from .models import Transcript

class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'
        # fields = ('rawtext', 'date', 'summary', 'actionables')