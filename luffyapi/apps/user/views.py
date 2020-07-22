from django.shortcuts import render

from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.decorators import action
from .serializer import RegisterSerializer, LoginSerializer
from luffyapi.utils.apiresponse import APIResponse

from luffyapi.libs.tx_sms import send_message, get_random_code

from .models import User

import re


# Create your views here.

class RegisterView(GenericViewSet):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.save()

    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(msg='用户注册成功', data=serializer.data)


class LoginView(ViewSet):
    """
    ViewSet 相当于 ViewSetMixin, views.APIView
    """

    @action(methods=['POST', ], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.context, type(serializer.context))
            return APIResponse(msg='用户登录成功', data=serializer.context)
        else:
            return APIResponse(code=101, msg='用户登录失败', data={'result': '数据校验未通过'})


class CheckPhone(object):
    def phone_is_valid(self, telephone):
        if not re.match(r'^1[3-9][0-9]{9}$', telephone):
            return False, '手机号格式不合法'
        if not User.objects.filter(telephone=telephone):
            return False, '手机号未注册'
        return True


class CheckPhoneView(ViewSet, CheckPhone):
    """
    后端校验手机格式是否合法，主要针对绕过浏览器给后端发送请求
    """

    @action(methods=['GET'], detail=False)
    def check_phone(self, request, *args, **kwargs):
        telephone = request.query_params.get('telephone')
        ret = self.phone_is_valid(telephone)
        if isinstance(ret, tuple):
            _, msg = ret
            return APIResponse(code=101, msg=msg)
        return APIResponse(msg='手机号检测成功')


class SendMessageView(ViewSet, CheckPhone):

    def phone_is_valid(self, telephone):
        if not re.match(r'^1[3-9][0-9]{9}$', telephone):
            return False, '手机号格式不合法'
        return True

    @action(methods=['GET'], detail=False)
    def send_msg(self, request, *args, **kwargs):
        telephone = request.query_params.get('telephone')
        ret = self.phone_is_valid(telephone)
        if isinstance(ret, tuple):
            _, msg = ret
            return APIResponse(code=101, msg=msg)
        random_code = get_random_code()
        result = send_message(telephone, random_code)
        if not result:
            return APIResponse(code=101, msg='短信验证失败')
        return APIResponse(msg='短信验证成功')
