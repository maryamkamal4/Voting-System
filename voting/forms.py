from django import forms
from account.models import CustomUser
from .models import Party, CandidateApplication, PollingSchedule, Vote
from cloudinary.forms import CloudinaryFileField

class CandidateApplicationForm(forms.ModelForm):
    party_name = forms.CharField(max_length=100, label='Party Name')
    symbol = CloudinaryFileField(label='Party Symbol', required=True)  # Use CloudinaryFileField

    class Meta:
        model = CandidateApplication
        fields = []

    def save(self, user=None, commit=True):
        party_name = self.cleaned_data.get('party_name')
        symbol = self.cleaned_data.get('symbol')
        
        party, created = Party.objects.get_or_create(name=party_name)
        if symbol:
            party.symbol = symbol
            party.save()

        application = super().save(commit=False)
        application.user = user
        application.party = party
        if commit:
            application.save()
        return application

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
