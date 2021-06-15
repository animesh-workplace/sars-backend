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
				task_id = self.scope['user'].username
				await self.accept()
				await self.channel_layer.group_add(task_id, self.channel_name)
				data = {
					'message': f'Welcome! {task_id} to Frontend Websocket',
				}
				await self.send_json(data)
		except:
			await self.close()

	async def receive_json(self, event):
		task_id = self.scope['user'].username
		await self.channel_layer.group_send(
			task_id,
				{
					'type': 'task_message',
					'data': event["data"],
				}
		)

	async def disconnect(self, close_code):
		task_id = self.scope['user'].username
		await self.channel_layer.group_discard(task_id, self.channel_name)
		await self.close()

	async def task_message(self, event):
		data = {
			"message": event['data']
		}
		await self.send_json(data)


class BackendConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		task_id = 'Backend_Update_Consumer'
		await self.accept()
		await self.channel_layer.group_add(task_id, self.channel_name)
		data = {
			'message': f'You have connected to {task_id}',
		}
		await self.send_json(data)

	async def receive_json(self, event):
		task_id = 'Backend_Update_Consumer'
		if(event['type'] == 'SUCCESS'):
			send_email_success(event['data'])
		elif(event['type'] == 'ERROR'):
			send_email_error(event['data'])
		elif(event['type'] == 'SUCCESS_ZIP'):
			create_download_link(event['data'])

	async def disconnect(self, close_code):
		task_id = 'Backend_Update_Consumer'
		await self.channel_layer.group_discard(task_id, self.channel_name)
		await self.close()

