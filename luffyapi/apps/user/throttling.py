from rest_framework.throttling import SimpleRateThrottle
from django.conf import settings


class AccountThrottling(SimpleRateThrottle):
    scope = 'account'
    THROTTLE_RATES = {
        'account': settings.THROTTLING_RATES,
    }

    def get_cache_key(self, request, view):
        account = request.query_params.get('account')
        return self.cache_format % {'scope': self.scope, 'ident': account}
