"""
ASGI config for nibmg_sars project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv
from django.conf.urls import url
from sequences.api.consumer import *
from django.urls import include, re_path
from .token_auth import JWTAuthMiddleware
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nibmg_sars.settings')
django_asgi_app = get_asgi_application()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

application = ProtocolTypeRouter({
	'http': django_asgi_app,
	'websocket': AllowedHostsOriginValidator(
			JWTAuthMiddleware(
					URLRouter(
							[
								re_path(os.getenv('BASE_URL'), URLRouter([
									re_path(r'^wsa/backend/$', BackendConsumer.as_asgi(), name='backend-consumer'),
									re_path(r'^wsa/frontend/$', FrontendConsumer.as_asgi(), name='frontend-consumer'),
								]))

							]
						)
				)
		)
})
