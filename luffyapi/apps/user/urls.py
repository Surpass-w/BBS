from django.urls import path, re_path
from .views import RegisterView, LoginView

urlpatterns = [
    # 用户注册接口
    path('register/', RegisterView.as_view(actions={'post': 'register'})),
    # 用户登录接口
    path('login/', LoginView.as_view(actions={'post': 'login'}))
]
