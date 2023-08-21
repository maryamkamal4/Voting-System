from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    cnic = models.CharField(max_length=15)  # Assuming CNIC is a string with max length of 15
    confirm_password = models.CharField(max_length=128)  # To store the temporarily confirmed password
    
    # Add any other custom fields or methods as needed

    def __str__(self):
        return self.username

    class Meta:
        # Add this line to resolve the clash
        swappable = 'AUTH_USER_MODEL'