import xadmin

# 注册banner表
from . import models
xadmin.site.register(models.Banner)
