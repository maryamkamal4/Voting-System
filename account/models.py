from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField  


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    cnic = models.CharField(_('CNIC'), max_length=15)
    confirm_password = models.CharField(_('confirm password'), max_length=128)
    is_approved = models.BooleanField(_('approved'), default=False)
    registration_token = models.CharField(_('registration token'), max_length=40, blank=True, null=True)

    profile_picture = CloudinaryField(
        'profile_picture',  # Cloudinary field name
        null=True,  # Allow NULL in the database
        blank=True,  # Allow blank field in forms
    )

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username


class Halka(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name