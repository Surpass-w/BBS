from django.shortcuts import render

from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.decorators import action
from .serializer import RegisterSerializer, LoginSerializer, CodeLoginSerializer
from luffyapi.utils.apiresponse import APIResponse

from luffyapi.libs.tx_sms import send_message
from luffyapi.libs.send_email import send_email
from utils.randomcode import get_random_code
from .throttling import AccountThrottling
from django.core.cache import cache

from .models import User
import re
from django.conf import settings


# Create your views here.

class RegisterView(GenericViewSet):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.save()

    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return APIResponse(msg='用户注册成功', data=serializer.data)
        else:
            return APIResponse(msg='用户注册失败', error=serializer.errors)


class LoginView(ViewSet):
    """
    ViewSet 相当于 ViewSetMixin, views.APIView
    """

    @action(methods=['POST', ], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return APIResponse(msg='用户登录成功', data=serializer.context)
        else:
            return APIResponse(code=101, msg='用户登录失败', data={'result': serializer.errors})


class CodeLoginView(ViewSet):

    @action(methods=['POST', ], detail=False)
    def code_login(self, request, *args, **kwargs):
        serializer = CodeLoginSerializer(data=request.data)
        if serializer.is_valid():
            return APIResponse(msg='用户登录成功', data=serializer.context)
        else:
            return APIResponse(code=101, msg='用户登录失败', data={'result': serializer.errors})


class CheckAccount(object):
    reg_phone = r'^1[3-9][0-9]{9}$'
    reg_email = r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'

    def account_is_valid(self, account):
        if not re.match(self.reg_phone, account) and not re.match(self.reg_email, account):
            return (False, '账号格式不合法')
        elif re.match(self.reg_phone, account):
            user = User.objects.filter(telephone=account, is_delete=False).first()
        else:
            user = User.objects.filter(email=account, is_delete=False).first()
        if not user:
            return (False, '账号未注册')
        return True


class CheckAccountView(ViewSet, CheckAccount):

    @action(methods=['GET', ], detail=False)
    def check_account(self, request, *args, **kwargs):
        account = request.query_params.get('account')
        ret = self.account_is_valid(account)
        if isinstance(ret, tuple):
            _, msg = ret
            return APIResponse(code=101, msg=msg)
        return APIResponse(msg='账号检测成功')


class SendCodeView(ViewSet, CheckAccount):
    reg_phone = r'^1[3-9][0-9]{9}$'
    reg_email = r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
    random_code = get_random_code()
    throttle_classes = [AccountThrottling, ]

    def account_is_valid(self, account):
        if not re.match(self.reg_phone, account) and not re.match(self.reg_email, account):
            return False, '账号格式不合法'
        elif re.match(self.reg_phone, account):
            return 'phone'
        else:
            return 'email'

    @property
    def email_configure(self):
        """
        send_email(link, random_code, subject, text_content, html_content, recv_email)
        """
        return {
            'link': '<a href="http://www.mzitu.com" style="text-decoration: none">详情链接</a>',
            'random_code': '<a href="#" style="text-decoration: none">%s</a>' % self.random_code,
            'subject': 'Django REST FRAMEWORK官方注册邮件',
            'text_content': '这是一封非常重要的邮件',
            'html_content': """
                <p>尊敬的用户:</p><br>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;您好，欢迎注册Django DRF，您的验证码为:%(code)s,3分钟有效。更多详情请点击链接:%(link)s!<p>
            """,
        }

    @action(methods=['GET'], detail=False)
    def send_code(self, request, *args, **kwargs):
        account = request.query_params.get('account')
        ret = self.account_is_valid(account)
        if isinstance(ret, tuple):
            _, msg = ret
            return APIResponse(code=101, msg=msg)
        if ret == 'phone':
            result = send_message(account, self.random_code)
            if not result:
                return APIResponse(code=101, msg='验证码发送失败')
        else:
            email_configure = self.email_configure
            email_configure['recv_email'] = account
            send_email(**email_configure)
        cache.set(settings.ACCOUNT_CACHE_KEY % {'key': account}, self.random_code, 180)
        return APIResponse(msg='验证码发送成功')
