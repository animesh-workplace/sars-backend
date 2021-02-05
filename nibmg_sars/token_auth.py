from django.conf import settings
from urllib.parse import parse_qs
from django.db import close_old_connections
from rest_framework.response import Response
from channels.exceptions import DenyConnection
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode, InvalidSignatureError, ExpiredSignatureError, DecodeError
from django.http import HttpResponse

class TokenAuthMiddleware:
	"""
	Custom token auth middleware
	"""

	def __init__(self, inner):
		# Store the ASGI application we were passed
		self.inner = inner

	def __call__(self, scope):

		# Close old database connections to prevent usage of timed out connections
		close_old_connections()

		# headers = dict(scope['headers'])
		# cookie  = headers[b'cookie'].decode('ascii')
		# cookie_split = cookie.split('; ')

		# for i in cookie_split:
		#     temp = i.split('=')
		#     if(temp[0] == 'auth._refresh_token.local'):
		#         if(temp[1] != 'false'):
		#             try:
		#                 token = temp[1]
		#                 # token = token[:len(token)-1]
		#                 payload = jwt_decode(token, settings.SECRET_KEY)
		#             except InvalidSignatureError:
		#                 # raise ValueError("InvalidSignatureError")
		#                 raise DenyConnection()
		#             except ExpiredSignatureError:
		#                 raise ValueError("ExpiredSignatureError")
		#             except DecodeError:
		#                 raise ValueError("DecodeError")
		#             except:
		#                 raise ValueError("Error")
		#         else:
		#             raise ValueError("falsevalue")
		#             DenyConnection()
					# raise ValueError("Not Authenticated")

		# Get the token
		# token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]

		# decoded_data = jwt_decode(token, settings.SECRET_KEY)
		# print(decoded_data)
		# Get the user using ID

		user = get_user_model().objects.get(id=1)
		# Return the inner application directly and let it run everything else
		return self.inner(dict(scope, user=user))
