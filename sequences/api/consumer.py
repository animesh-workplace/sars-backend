import json
from .tasks import *
from time import sleep
from colorama import Fore, init
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

init(autoreset=True)

class FrontendConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
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
			result = {
				"type": "MY_METADATA",
				"data": get_my_metadata(self.scope["user"])
			}
		elif(event["type"] == "ALL_METADATA"):
			result = {
				"type": "ALL_METADATA",
				"data": get_all_metadata(self.scope["user"])
			}
		else:
			result = {
				"type": "ERROR"
			}
		await self.send_json(result)
		# await self.channel_layer.group_send(
		# 	username,
		# 		{
		# 			"type": "task_message",
		# 			"result": result,
		# 		}
		# )

	async def disconnect(self, close_code):
		username = self.scope['user'].username
		await self.channel_layer.group_discard(username, self.channel_name)
		await self.close()

	async def task_message(self, event):
		result = event["result"]
		await self.send_json(result)


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
			create_download_link(event["data"])
		elif(event["type"] == "SUCCESS_METADATA"):
			create_frontend_entry(event["data"])

	async def disconnect(self, close_code):
		group_name = "Backend_Update_Consumer"
		await self.channel_layer.group_discard(group_name, self.channel_name)
		await self.close()

