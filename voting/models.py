from django.db import models
from cloudinary.models import CloudinaryField
from account.models import CustomUser, Halka  
from django.utils import timezone


# Create your models here.

class Party(models.Model):
    name = models.CharField(max_length=100)
    symbol = CloudinaryField('party_symbol', null=True, blank=True)

    def __str__(self):
        return self.name


class CandidateApplication(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Vote(models.Model):
    voter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='votes_given')
    candidate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='votes_received')
    halka = models.ForeignKey(Halka, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.voter.username} -> {self.candidate.username}'
    
 
class PollingSchedule(models.Model):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def is_polling_active(self):
        current_time = timezone.now()
        return self.start_datetime <= current_time <= self.end_datetime
