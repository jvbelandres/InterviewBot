from InterviewBot import views
from rest_framework import viewsets
from . import models
from . import serializers

class AccountViewset(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer

class ContactViewset(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer

class CreateJobViewset(viewsets.ModelViewSet):
    queryset = models.CreateJob.objects.all()
    serializer_class = serializers.CreateJobSerializer

class SavedJobViewset(viewsets.ModelViewSet):
    queryset = models.SavedJob.objects.all()
    serializer_class = serializers.SavedJobSerializer

class AppliedJobViewset(viewsets.ModelViewSet):
    queryset = models.AppliedJob.objects.all()
    serializer_class = serializers.AppliedJobSerializer