from django.urls import path, include
from .views import RegisterView, LoginView, CheckPhoneView, SendMessageView
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', LoginView, 'login')
router.register('', CheckPhoneView, 'check_phone')
router.register('', SendMessageView, 'send_msg')

urlpatterns = [
    # 用户注册接口
    path('register/', RegisterView.as_view(actions={'post': 'register'})),
    # path('',include(router.urls)),
]

urlpatterns += router.urls
