from django.shortcuts import render

from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from .serializer import RegisterSerializer,LoginSerializer
from luffyapi.utils.apiresponse import APIResponse




# Create your views here.

class RegisterView(ViewSetMixin, GenericAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.save()

    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(msg='用户注册成功', data=serializer.data)


class LoginView(ViewSetMixin, APIView):

    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={})
        serializer.is_valid(raise_exception=True)
        return APIResponse(msg='用户登录成功', data=serializer.context)

