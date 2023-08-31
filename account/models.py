from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField  


class Halka(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    cnic = models.CharField(_('CNIC'), max_length=15)
    confirm_password = models.CharField(_('confirm password'), max_length=128)
    is_approved = models.BooleanField(_('approved'), default=False)
    registration_token = models.CharField(_('registration token'), max_length=40, blank=True, null=True)
    halka = models.ForeignKey(Halka, on_delete=models.CASCADE, blank=True, null=True)


    profile_picture = CloudinaryField(
        'profile_picture',
        null=True,  
        blank=True,  
    )

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username
