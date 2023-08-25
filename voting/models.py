from django.db import models
from cloudinary.models import CloudinaryField
from account.models import CustomUser  

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
