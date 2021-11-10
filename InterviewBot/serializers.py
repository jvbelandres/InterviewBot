from django.db.models import fields
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import Account, CreateJob, SavedJob, AppliedJob

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('is_active', 'staff', 'admin', 'email', 'firstname', 'lastname', 'gender', 'phone', 'password')

class JobOfferingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateJob
        fields = ('admin_id', 'title', 'description')

class JobOfferingDetailedSerializer(serializers.ModelSerializer):
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
        fields = ('user_id', 'job_id', 'final_score')
