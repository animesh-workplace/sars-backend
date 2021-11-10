import json
from .tasks import *
from time import sleep
from colorama import Fore, init
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from django.core.serializers.json import DjangoJSONEncoder
from channels.generic.websocket import AsyncJsonWebsocketConsumer

init(autoreset=True)

class FrontendConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		print('Consumer, here', self.scope['user'])
		try:
			if(self.scope['user'].is_authenticated):
				username = self.scope['user'].username
				await self.accept()
				await self.channel_layer.group_add(username, self.channel_name)
				data = {
					"type": "Message",
					"message": f"Welcome! {username} to Frontend Websocket",
				}
				await self.send_json(data)
		except:
			await self.close()

	async def receive_json(self, event):
		username = self.scope["user"].username
		if(event["type"] == "MY_METADATA"):
			search = event["filter"]["search"] if('search' in event["filter"].keys()) else None
			result = {
				"type": "MY_METADATA",
				"data": await get_my_metadata(self.scope["user"], event["filter"]["each_page"], event["filter"]["page"], search)
			}
		elif(event["type"] == "ALL_METADATA"):
			result = {
				"type": "ALL_METADATA",
				"data": await get_all_metadata(event["filter"]["each_page"], event["filter"]["page"])
			}
		elif(event["type"] == "SEARCH_METADATA"):
			result = {
				"type": "SEARCH_METADATA",
				"data": await search_my_metadata(self.scope["user"], event["filter"]["search"])
			}
		else:
			result = {
				"type": "ERROR"
			}
		await self.send_json(result)

	async def disconnect(self, close_code):
		try:
			username = self.scope['user'].username
			await self.channel_layer.group_discard(username, self.channel_name)
			await self.close()
		except:
			await self.close()

	@classmethod
	async def encode_json(cls, content):
		return json.dumps(content, cls = DjangoJSONEncoder)

class BackendConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		group_name = "Backend_Update_Consumer"
		await self.accept()
		await self.channel_layer.group_add(group_name, self.channel_name)
		data = {
			"message": f"You have connected to {group_name}",
		}
		await self.send_json(data)

	async def receive_json(self, event):
		group_name = "Backend_Update_Consumer"
		if(event["type"] == "SUCCESS"):
			send_email_success(event["data"])
		elif(event["type"] == "ERROR"):
			send_email_error(event["data"])
		elif(event["type"] == "SUCCESS_ZIP"):
			await create_download_link(event["data"])
		elif(event["type"] == "SUCCESS_METADATA"):
			await create_frontend_entry(event["data"]["message"])
		elif(event["type"] == "CLOSE"):
			await self.close()

	async def disconnect(self, close_code):
		group_name = "Backend_Update_Consumer"
		print('Closing a connection')
		await self.channel_layer.group_discard(group_name, self.channel_name)
		await self.close()

