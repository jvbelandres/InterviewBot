from django import forms
from django.core import validators
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from user.models import Account

User = get_user_model()
choices = [
    ('Male', 'Male*'),
    ('Female', 'Female*'),
]

class AdminRegisterForm(forms.ModelForm):
    firstname = forms.CharField(widget=forms.TextInput(attrs={'id':'firstName','placeholder':'First Name*'}),required=True)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'id':'lastName','placeholder':'Last Name*'}),required=True)
    phone = forms.CharField(widget=forms.NumberInput(attrs={'id':'phone', 'oninput':'limit_input()','placeholder':'Phone*', 'title':'Must be 11 digits','placeholder':'Password*'}), validators=[validators.RegexValidator(r'\d{11,11}',
            'Invalid Phone Number', 'Invalid number')], required=True)
    gender = forms.CharField(widget=forms.Select(choices=choices, attrs={'id':'gender'}),required=True)
    email = forms.CharField(widget=forms.EmailInput(attrs={'id':'emailAdd','placeholder':'Email Address*'}),required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id':'pass','pattern':'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{6,20}',
                                'title':'Must contain at least one number and one uppercase and lowercase letter and at least 6 not greater than 20 characters.','placeholder':'Password*'}),required=True)
    password_2 = forms.CharField(widget=forms.PasswordInput(attrs={'id':'pass2','placeholder':'Confirm Password*'}),required=True)

    class Meta:
        model = Account
        fields = ('firstname','lastname','phone', 'gender', 'email', 'password')

    def clean_email(self): # Verify email is available
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        # Save the created admin account
        user = super().save(commit=False)
        firstname = self.cleaned_data["firstname"]
        lastname = self.cleaned_data["lastname"]
        phone = self.cleaned_data["phone"]
        cleaned_phone = str(phone)
        gender = self.cleaned_data["gender"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        if commit:
        	u = Account.objects.create_superuser(firstname=firstname, lastname=lastname, 
        		gender=gender, phone=cleaned_phone, email=email, password=password)
        return user

class StaffRegisterForm(forms.ModelForm):
    firstname = forms.CharField(widget=forms.TextInput(attrs={'id':'firstName','placeholder':'First Name*'}),required=True)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'id':'lastName','placeholder':'Last Name*'}),required=True)
    phone = forms.CharField(widget=forms.NumberInput(attrs={'id':'phone', 'oninput':'limit_input()','placeholder':'Phone*', 'title':'Must be 11 digits','placeholder':'Password*'}), validators=[validators.RegexValidator(r'\d{11,11}',
            'Invalid Phone Number', 'Invalid number')], required=True)
    gender = forms.CharField(widget=forms.Select(choices=choices, attrs={'id':'gender'}),required=True)
    email = forms.CharField(widget=forms.EmailInput(attrs={'id':'emailAdd','placeholder':'Email Address*'}),required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id':'pass','pattern':'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,20}',
                                'title':'Must contain at least one number and one uppercase and lowercase letter and at least 6 not greater than 20 characters.','placeholder':'Password*'}),required=True)
    password_2 = forms.CharField(widget=forms.PasswordInput(attrs={'id':'pass2','placeholder':'Confirm Password*'}),required=True)

    class Meta:
        model = Account
        fields = ('firstname','lastname','phone', 'gender', 'email', 'password')

    def clean_email(self): # Verify email is available
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        # Save the created staff account
        user = super().save(commit=False)
        firstname = self.cleaned_data["firstname"]
        lastname = self.cleaned_data["lastname"]
        phone = self.cleaned_data["phone"]
        cleaned_phone = str(phone)
        gender = self.cleaned_data["gender"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        if commit:
            u = Account.objects.create_staffuser(firstname=firstname, lastname=lastname, 
                gender=gender, phone=cleaned_phone, email=email, password=password)
        return user