from django.db.models import fields
from rest_framework import serializers

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .tokens import account_activation_token
from .models import Account

class AccountRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'is_active', 'staff', 'admin', 'firstname', 'lastname', 'phone', 'password', 'gender')

    def create(self, validated_data):
        newUser =  Account(
            email = validated_data['email'],
            is_active = validated_data['is_active'],
            staff = validated_data['staff'],
            admin = validated_data['admin'],
            firstname = validated_data['firstname'],
            lastname = validated_data['lastname'],
            phone = validated_data['phone'],
            gender = validated_data['gender'],
        )
        newUser.set_password(validated_data['password'])
        newUser.save()

        mail_subject = 'Activate your account.'
        message = render_to_string('account_activation/user/acc_active_email.html', {
            'user': newUser,
            'domain': "127.0.0.1:8000",
            'uid':urlsafe_base64_encode(force_bytes(newUser.pk)),
            'token':account_activation_token.make_token(newUser),
        })
        to_email = validated_data['email']
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        return newUser