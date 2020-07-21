from django.utils.deprecation import MiddlewareMixin


class CorsMiddleware(MiddlewareMixin):
    ALLOW_HOST = 'http://127.0.0.1:8004' # 可以放到配置文件中

    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = self.ALLOW_HOST
        if request.method == 'OPTIONS':
            response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
