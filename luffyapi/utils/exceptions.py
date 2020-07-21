# 方法,加日志

from rest_framework.views import exception_handler
# from luffyapi.utils import response
from .apiresponse import APIResponse
from .logger import log


def common_exception_handler(exc, context):
    log.error('view是：%s ，错误是%s' % (context['view'].__class__.__name__, str(exc)))
    # context['view']  是TextView的对象，想拿出这个对象对应的类名
    ret = exception_handler(exc, context)  # 是Response对象，它内部有个data

    if not ret:  # drf内置处理不了，丢给django 的，我们自己来处理
        # 好多逻辑，更具体的捕获异常
        if isinstance(exc, KeyError):
            return APIResponse(code=0, msg='key error')

        return APIResponse(code=0, msg='error', result=str(exc))
    else:
        return APIResponse(code=0, msg='error', result=ret.data)
