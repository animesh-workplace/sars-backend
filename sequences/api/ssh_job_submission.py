import os
from dotenv import load_dotenv
from django.conf import settings
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException

load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

class RemoteClient:
	def __init__(self, host, user, port, ssh_key_filepath, remote_path):
		self.host 				= host
		self.user 				= user
		self.port				= port
		self.remote_path 		= remote_path
		self.ssh_key_filepath 	= ssh_key_filepath
		self.client 			= None
		self.__upload_ssh_key()

	def __get_ssh_key(self):
		try:
			self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
			print(f'Found SSH key at self {self.ssh_key_filepath}')
		except SSHException as error:
			print(error)
		return self.ssh_key

	def __upload_ssh_key(self):
		try:
			os.system(f'ssh-copy-id -i {self.ssh_key_filepath} {self.user}@{self.host}>/dev/null 2>&1')
			os.system(f'ssh-copy-id -i {self.ssh_key_filepath}.pub {self.user}@{self.host}>/dev/null 2>&1')
			print(f'{self.ssh_key_filepath} uploaded to {self.host}')
		except FileNotFoundError as error:
			print(error)

	def __connect(self):
		try:
			self.client = SSHClient()
			self.client.load_system_host_keys()
			self.client.set_missing_host_key_policy(AutoAddPolicy())
			self.client.connect(
                                timeout			= 5000,
                                look_for_keys	= True,
                                port			= self.port,
								hostname		= self.host,
                                username 		= self.user,
                                key_filename 	= self.ssh_key_filepath
                                )
			print(f'Connected successfully to {self.user}@{self.host}')
		except AuthenticationException as error:
			print('Authentication failed: did you remember to create an SSH key?')
			print(error)
			raise error
		finally:
			return self.client

	def connect_to_remote(self):
		if self.client is None:
			self.client = self.__connect()

	def disconnect_from_remote(self):
		self.client.close()
