from django import forms

class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'id':'emailAdd','placeholder':'Email Address','autofocus':True}),required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id':'pass','placeholder':'Password'}),required=True)