from rest_framework import serializers
from .models import Account, AppliedJob, Contact, CreateJob, SavedJob
from user import models

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'is_active', 'staff', 'admin', 'firstname', 'lastname', 'phone', 'password', 'gender')

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class CreateJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateJob
        fields = '__all__'

class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = '__all__'

class AppliedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedJob
        fields = '__all__'