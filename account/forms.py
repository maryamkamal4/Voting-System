from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from .models import CustomUser

class SignUpForm(UserCreationForm):
    email = forms.EmailField()
    groups = forms.ModelChoiceField(queryset=Group.objects.all().exclude(name='admin'), required=True)  # Add this line

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'cnic', 'password1', 'password2', 'groups')

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
