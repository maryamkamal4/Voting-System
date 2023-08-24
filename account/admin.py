from django.contrib import admin
from account.models import CustomUser, Halka

# Register your models here.
admin.site.register(Halka)
admin.site.register(CustomUser)