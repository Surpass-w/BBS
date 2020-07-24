from django.urls import path
from .views import RegisterView, LoginView, CheckAccountView, SendCodeView, CodeLoginView
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', LoginView, 'login')
router.register('', CheckAccountView, 'check_account')
router.register('', SendCodeView, 'send_code')
router.register('', CodeLoginView, 'code_login')

urlpatterns = [
    # 用户注册接口
    path('register/', RegisterView.as_view(actions={'post': 'register'})),
    # path('',include(router.urls)),
]

urlpatterns += router.urls
