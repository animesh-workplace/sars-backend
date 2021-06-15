"""
ASGI config for nsm_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
from django.conf.urls import url
from sequences.api.consumer import *
from django.urls import include, re_path
from .token_auth import JWTAuthMiddleware
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
			JWTAuthMiddleware(
					URLRouter(
							[
								url(os.getenv('BASE_URL'), URLRouter([
									url(r'^wsa/data/$', TestConsumer, name='test-consumer'),
									url(r'^wsa/backend/$', BackendConsumer, name='backend-consumer'),
								]))

							]
						)
				)
		)
})

