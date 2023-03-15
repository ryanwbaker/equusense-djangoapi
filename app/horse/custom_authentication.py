from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if request.method == 'POST':
            request.user = None
            return None  # success, no authentication necessary
        else:
            raise AuthenticationFailed('Authentication credentials were not provided.')