from django import forms
from django.contrib.auth.forms import UserCreationForm
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
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.halka = self.cleaned_data.get('halka')  # Assign the selected Halka instance
        if commit:
            user.save()
        return user

class HalkaForm(forms.ModelForm):
    class Meta:
        model = Halka
        fields = ['name']  # Customize fields as needed
