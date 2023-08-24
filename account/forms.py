from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from .models import CustomUser

class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'cnic', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
