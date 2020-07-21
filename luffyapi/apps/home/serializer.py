from rest_framework import serializers
from .models import Banner


class BannerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['name', 'link', 'img']
