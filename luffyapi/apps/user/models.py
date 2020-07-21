from django.db import models

# Create your models here.

from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    telephone = models.CharField(max_length=11, verbose_name='手机')
    icon = models.ImageField(upload_to='icon', default='icon/default.png', verbose_name='头像')
    is_delete = models.BooleanField(default=False)