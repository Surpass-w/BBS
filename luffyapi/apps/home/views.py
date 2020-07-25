from django.shortcuts import render

# Create your views here.

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from . import models
from .serializer import BannerModelSerializer
from django.conf import settings

from rest_framework.response import Response
from django.core.cache import cache
from django_redis import get_redis_connection


class BannerView(GenericViewSet, ListModelMixin):
    queryset = models.Banner.objects.filter(is_delete=False, is_show=True).order_by('display_order')[
               :settings.BANNER_COUNTER]
    serializer_class = BannerModelSerializer

    # 需要重写list方法
    def list(self, request, *args, **kwargs):
        """
        先从缓存中去取，没有查询数据库，同时返还一份给缓存保存；若缓存中有，直接将缓存中的值返回
        """
        banner_list = cache.get(settings.BANNER_LIST_CACHE)
        if not banner_list:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            cache.set(settings.BANNER_LIST_CACHE, serializer.data,60*60)
            return Response(data=serializer.data)
        return Response(data=banner_list)

        # banner_list = cache.get('banner_list')
        # if not banner_list:
        #     response = super().list(request,*args,**kwargs)
        #     # 加到缓存中
        #     cache.set('banner_list',response.data,60*60)
        #     return response
        # return Response(data=banner_list)
