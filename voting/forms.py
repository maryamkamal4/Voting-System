from datetime import datetime
from django import forms
import pytz
from account.models import CustomUser
from .models import Party, CandidateApplication, PollingSchedule, Vote
from cloudinary.forms import CloudinaryFileField

class CandidateApplicationForm(forms.ModelForm):
    party_name = forms.CharField(max_length=100, label='Party Name')
    symbol = CloudinaryFileField(label='Party Symbol', required=True)  # Use CloudinaryFileField

    class Meta:
        model = CandidateApplication
        fields = []

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['candidate']

    def __init__(self, *args, **kwargs):
        user_halka = kwargs.pop('user_halka')  # Get the user's halka from kwargs
        super().__init__(*args, **kwargs)
        self.fields['candidate'].queryset = CustomUser.objects.filter(groups__name='candidate', halka=user_halka)


class PollingScheduleForm(forms.ModelForm):
    class Meta:
        model = PollingSchedule
        fields = ['start_datetime', 'end_datetime']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }