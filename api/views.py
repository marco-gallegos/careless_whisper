from rest_framework import viewsets
from.serializer import TranscriptSerializer
from .models import Transcript

# Create your views here.
class TrancriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer