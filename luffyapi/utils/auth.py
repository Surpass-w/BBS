from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.utils import jwt_decode_handler
import jwt


class XJOSNWebTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        jwt_value = request.META.get('HTTP_AUTHORIZATION', None)
        if not jwt_value:
            raise AuthenticationFailed('未携带认证参数token')
        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('签证已过期')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('无效的token')
        except Exception as e:
            raise AuthenticationFailed(str(e))
        user = self.authenticate_credentials(payload)
        return user, jwt_value
