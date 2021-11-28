from django import forms
from django.core import validators
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import *

User = get_user_model()
choices = [
    ('Male', 'Male*'),
    ('Female', 'Female*'),
]

class RegisterForm(forms.ModelForm):
    firstname = forms.CharField(widget=forms.TextInput(attrs={'id':'firstName','placeholder':'First Name*'}),required=True)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'id':'lastName','placeholder': 'Last Name*'}),required=True)
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
            raise forms.ValidationError('Invalid email')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if (len(phone) != 11):
            raise forms.ValidationError('Invalid phone number')
        return phone

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        firstname = self.cleaned_data["firstname"]
        lastname = self.cleaned_data["lastname"]
        phone = self.cleaned_data["phone"]
        gender = self.cleaned_data["gender"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        if commit:
            Account.objects.create_user(firstname=firstname, lastname=lastname, 
                gender=gender, phone=phone, email=email, password=password)
        return user

class UserAdminCreationForm(forms.ModelForm): 
# A form for creating new users. Includes all the required fields, plus a repeated password.
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']

    def clean(self): # Verify both passwords match.
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            self.add_error("password_2", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True): # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'is_active', 'admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'id':'emailAdd','placeholder':'Email Address','autofocus':True}),required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id':'pass','placeholder':'Password'}),required=True)

class ContactForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={'id':'subject','placeholder':'Subject'}),required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'id':'message','placeholder':'Message'}),required=True)

    class Meta:
      model = Contact
      fields = ('email','subject','message')

# class UpdateForm(forms.ModelForm):

# 	class Meta:
# 		model = Accounts
# 		fields = ('firstname', 'lastname', 'password', 'email')