from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Halka
from cloudinary.forms import CloudinaryFileField


class SignUpForm(UserCreationForm):
    email = forms.EmailField()
    profile_picture = CloudinaryFileField(
        options={"folder": "profile_pictures/"},
        required=True,
        label="Profile Picture"
    )
    halka = forms.ModelChoiceField(queryset=Halka.objects.all(), label="Select Halka")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'cnic', 'profile_picture', 'halka', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser

class HalkaForm(forms.ModelForm):
    class Meta:
        model = Halka
        fields = ['name']  # Customize fields as needed
