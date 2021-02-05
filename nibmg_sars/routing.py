"""
ASGI config for nsm_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

# from jobs.api.consumer import *
from django.conf.urls import url
from django.urls import include, re_path
from .token_auth import TokenAuthMiddleware
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator


application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
			TokenAuthMiddleware(
					URLRouter(
							[
								# url(r'^wsa/jobs/(?P<task_id>[^/]+)/$', JobConsumer, name='job-consumer'),
								# url(r'^wsa/jobs/(?P<task_id>[^/]+)/usage$', JobConsumerUsage, name='job-consumer-usage'),

							]
						)
				)
		)
})

