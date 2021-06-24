# from django.conf import settings
# from urllib.parse import parse_qs
# from rest_framework.response import Response
# from django.contrib.auth import get_user_model
# from jwt import decode as jwt_decode, InvalidSignatureError, ExpiredSignatureError, DecodeError
# from django.http import HttpResponse

from http import cookies
from django.db import close_old_connections
from channels.auth import AuthMiddlewareStack
from channels.exceptions import DenyConnection
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication


class JWTAuthenticationFromScope(BaseJSONWebTokenAuthentication):
    """
    Extracts the JWT from a channel scope (instead of an http request)
    """
    def get_jwt_value(self, scope):
        try:
            cookie = next(x for x in scope['headers'] if x[0].decode('utf-8') == 'cookie')[1].decode('utf-8')
            return cookies.SimpleCookie(cookie)['c_uid'].value
        except:
            return None


class JWTAuthMiddleware(BaseJSONWebTokenAuthentication):
    """
    Token authorization middleware for Django Channels 2
    """
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):

        try:
            # Close old database connections to prevent usage of timed out connections
            close_old_connections()

            user, jwt_value = JWTAuthenticationFromScope().authenticate(scope)
            scope['user'] = user
        except:
            DenyConnection()

        return self.inner(scope)
