from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from .models import User

import re
import time


class RegisterSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=32, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 're_password', 'telephone', 'email']

    def validate_username(self, username):
        if username.startswith('sb') and username.endswith('sb'):
            raise ValidationError("username中包含敏感词'sb'")
        if User.objects.filter(username=username, is_delete=False):
            raise ValidationError('用户已存在')
        return username

    def validate_telephone(self, telephone):
        if not re.match(r'^1[3-9][0-9]{9}$', telephone):
            raise ValidationError('手机的格式非法')
        return telephone

    def validate_email(self, email):
        if not re.match(r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            raise ValidationError('邮箱格式不正确')
        return email

    def validate(self, attrs):
        password = attrs.get('password', None)
        re_password = attrs.pop('re_password', None)
        if not re_password == password:
            raise ValidationError('两次密码输入不一致')
        return attrs

    def create(self, validated_data):
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

    def _get_token(self, user):
        """
        通过user对象获取到荷载payload
        通过payload获取到token
        """
        payload = jwt_payload_handler(user)
        jwt_value = jwt_encode_handler(payload)
        return jwt_value

    def validate(self, attrs):
        user = self._get_user(attrs)
        login_info = {
            'username': user.username,
            'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'token': self._get_token(user)
        }
        for attr, value in login_info.items():
            self.context[attr] = value
        return attrs
