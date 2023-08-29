from django.db import models
from cloudinary.models import CloudinaryField
from account.models import CustomUser, Halka  
from datetime import datetime
import pytz


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
    voter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    candidate = models.ForeignKey(CustomUser, related_name='votes_received', on_delete=models.CASCADE)
    halka = models.ForeignKey(Halka, on_delete=models.CASCADE)
    vote_count = models.PositiveIntegerField(default=0)  # New field for vote count

    def __str__(self):
        return f"{self.vote_count} votes for {self.candidate.username}"


class PollingSchedule(models.Model):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def is_voting_open(self):
        now = datetime.now(pytz.timezone('Asia/Karachi'))

        start_date = self.start_datetime.date()
        end_date = self.end_datetime.date()

        start_time = self.start_datetime.time()
        end_time = self.end_datetime.time()

        current_date = now.date()
        current_time = now.time()

        if start_date <= current_date <= end_date:
            if start_time <= current_time <= end_time:
                return True
        
        return False

    


