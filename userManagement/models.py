from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(_("email address"), unique=True)
    age = models.IntegerField()