from qcloudsms_py import SmsSingleSender
from luffyapi.utils.logger import log
from . import settings
from random import randint


# 生成一个6位的随机验证码
def get_random_code():
    random_code = ''
    for i in range(6):
        random_code += str(randint(0, 9))
    return random_code


def send_message(phone_number, random_code):
    msg_sender = SmsSingleSender(settings.SDKAppID, settings.SDKAppKey)
    params = [random_code,]
    try:
        result = msg_sender.send_with_param(86, phone_number,
                                            settings.TEMPLATE_ID, params, sign=settings.SMS_SIGN, extend="", ext="")
        return not bool(result.get('request')) or False
    except Exception as e:
        log.error(f'手机号:{phone_number},短信发送失败，错误信息为:{str(e)}')
