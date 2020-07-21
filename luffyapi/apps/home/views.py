from django.shortcuts import render

# Create your views here.

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from . import models
from .serializer import BannerModelSerializer
from django.conf import settings

from luffyapi.utils.apiresponse import APIResponse


class BannerView(GenericViewSet, ListModelMixin):
    queryset = models.Banner.objects.filter(is_delete=False, is_show=True).order_by('display_order')[
               :settings.BANNER_COUNTER]
    serializer_class = BannerModelSerializer
