# 生成一个6位的随机验证码
from random import randint


def get_random_code():
    random_code = ''
    for i in range(6):
        random_code += str(randint(0, 9))
    return random_code
