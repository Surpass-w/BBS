from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from .models import User
from django.core.cache import cache
from django.conf import settings

import re
import time


def get_token(user):
    """
    通过user对象获取到荷载payload
    通过payload获取到token
    """
    payload = jwt_payload_handler(user)
    jwt_value = jwt_encode_handler(payload)
    return jwt_value


class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['telephone', 'password', 'code', 'username']
        extra_kwargs = {
            'password': {'max_length': 18, 'min_length': 8},
            'username': {'read_only': True},
            'telephone': {'write_only': True},
        }

    def _check_telephone(self, telephone):
        if not re.match(r'^1[3-9][0-9]{9}$', telephone):
            return False, '手机号格式不合法'
        user = User.objects.filter(telephone=telephone, is_delete=False).first()
        if user:
            return False, '用户已存在，请直接登录'
        cache_key = settings.ACCOUNT_CACHE_KEY % {'key': telephone}
        return cache.get(cache_key, None)

    def validate(self, attrs):
        """
        前端校验后，后端还需要再校验一下，存在绕过浏览器注册的场景，因此在这里需要再校验一下
        """
        telephone = attrs.get('telephone', None)
        code = attrs.get('code', None)
        ret = self._check_telephone(telephone)
        if not ret:
            raise ValidationError('验证码已过期')
        if isinstance(ret, tuple):
            _, msg = ret
            raise ValidationError(msg)
        if code == ret:
            attrs['username'] = telephone
            return attrs
        raise ValidationError('验证码错误')

    def create(self, validated_data):
        validated_data.pop('code')
        instance = User.objects.create_user(**validated_data)
        return instance


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

    def _get_user(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get('password', None)
        if re.match(r'^1[3-9][0-9]{9}$', username):
            user = User.objects.filter(telephone=username, is_delete=False).first()
        elif re.match(r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', username):
            user = User.objects.filter(email=username, is_delete=False).first()
        else:
            user = User.objects.filter(username=username, is_delete=False).first()
        if not user:
            raise ValidationError('用户不存在')
        if not user.check_password(password):
            raise ValidationError('密码错误')
        return user

    def validate(self, attrs):
        user = self._get_user(attrs)
        login_info = {
            'username': user.username,
            'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'token': get_token(user)
        }
        for attr, value in login_info.items():
            self.context[attr] = value
        return attrs


class CodeLoginSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)
    account = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['account', 'code']

    @staticmethod
    def check_account(account):
        reg_phone = r'^1[3-9][0-9]{9}$'
        reg_email = r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
        if not re.match(reg_phone, account) and not re.match(reg_email, account):
            return False, '账号格式不合法'
        elif re.match(reg_phone, account):
            user = User.objects.filter(telephone=account, is_delete=False).first()
        else:
            user = User.objects.filter(email=account, is_delete=False).first()
        return user or (False, '账号未注册')

    def _get_user(self, attrs):
        account = attrs.get('account')
        code = attrs.get('code')
        ret = self.check_account(account)
        if isinstance(ret, tuple):
            _, msg = ret
            raise ValidationError(msg)
        cache_key = settings.ACCOUNT_CACHE_KEY % {'key': account}
        if code == cache.get(cache_key):
            cache.delete(cache_key)
            return ret
        else:
            raise ValidationError('验证码错误')

    def validate(self, attrs):
        user = self._get_user(attrs)
        login_info = {
            'username': user.username,
            'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'token': get_token(user)
        }
        for attr, value in login_info.items():
            self.context[attr] = value
        return attrs
