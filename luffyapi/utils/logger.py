
# import logging
# # log=logging.getLogger('名字') # 跟配置文件中loggers日志对象下的名字对应
# log=logging.getLogger('django')


from logging import getLogger
from logging import config
from luffyapi.settings import dev

config.dictConfig(dev.LOGGING)
log = getLogger("django")