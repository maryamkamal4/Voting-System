from django import forms
from .models import Party, CandidateApplication

class CandidateApplicationForm(forms.ModelForm):
    party_name = forms.CharField(max_length=100, label='Party Name')
    symbol = forms.ImageField(label='Party Symbol', required=False)

    class Meta:
        model = CandidateApplication
        fields = []

    def save(self, user=None, commit=True):  # Pass the user as a parameter
        party_name = self.cleaned_data.get('party_name')
        symbol = self.cleaned_data.get('symbol')
        
        party, created = Party.objects.get_or_create(name=party_name)
        if symbol:
            party.symbol = symbol
            party.save()

        application = super().save(commit=False)
        application.user = user  # Use the user parameter
        application.party = party
        if commit:
            application.save()
        return application
