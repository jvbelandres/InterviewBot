from django.db.models import fields
from rest_framework import serializers

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
        fields = ('id', 'admin_id', 'title', 'description')

class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ['user', 'job']

class CreateJobSerializer(serializers.ModelSerializer):
    admin = FewAccountDetailsSerializer()
    class Meta:
        model = CreateJob
        fields = ['id', 'title', 'description', 'admin']

class AppliedJobSerializer(serializers.ModelSerializer):
    job = CreateJobSerializer()
    class Meta:
        model = AppliedJob
        fields = ('final_score', 'job')

class ApplicantViewingSerializer(serializers.ModelSerializer):
    user = AccountSerializer()
    class Meta:
        model = AppliedJob
        fields = ('final_score', 'user')

class SavedJobUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateJob
        fields = ['id', 'title', 'description']

class AppliedJobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedJob
        fields = ['job_id', 'final_score']