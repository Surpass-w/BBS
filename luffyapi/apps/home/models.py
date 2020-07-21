from django.db import models
from utils.models import BaseModel


# Create your models here.

class Banner(BaseModel):
    name = models.CharField(max_length=32, verbose_name='图片名称')
    img = models.ImageField(upload_to='banner', verbose_name='轮播图', help_text='轮播图的尺寸必须是: 3840*800', null=True)
    link = models.CharField(max_length=32, verbose_name='跳转链接')
    info = models.TextField(verbose_name='图片简介')

    def __str__(self):
        return self.name
