from django.db.models import fields
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import Account, CreateJob, SavedJob, AppliedJob

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('is_active', 'staff', 'admin', 'email', 'firstname', 'lastname', 'gender', 'phone', 'password')

class FewAccountDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'firstname', 'lastname')

class JobOfferingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateJob
        fields = ('admin_id', 'title', 'description')

class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ['user', 'job']

class CreateJobSerializer(serializers.ModelSerializer):
    admin = FewAccountDetailsSerializer()
    class Meta:
        model = CreateJob
        fields = ['title', 'description', 'admin']

class AppliedJobSerializer(serializers.ModelSerializer):
    job = CreateJobSerializer()
    class Meta:
        model = AppliedJob
        fields = ('final_score', 'job')

class SavedJobUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateJob
        fields = ['id', 'title', 'description']