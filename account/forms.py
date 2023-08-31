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
        user.halka = self.cleaned_data.get('halka')  
        if commit:
            user.save()
        return user

class HalkaForm(forms.ModelForm):
    class Meta:
        model = Halka
        fields = ['name']  

class InvitationForm(forms.Form):
    selected_user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(groups__name='voter'),
        empty_label="Select a user",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['halka'] = forms.ModelChoiceField(
            queryset=Halka.objects.all(),
            empty_label="Select a halka",
            widget=forms.Select(attrs={'class': 'form-control'})
        )
