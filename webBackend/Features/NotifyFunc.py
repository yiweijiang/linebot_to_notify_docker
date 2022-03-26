from bs4 import BeautifulSoup
import requests
import os

class Line_Notify():
	def __init__(self):
		self.url = 'https://notify-api.line.me/api/notify'

	def post_text(self, msg, token):
		if msg == '\n':
			return True
		headers = {
			"Authorization": "Bearer " + token,
			"Content-Type" : "application/x-www-form-urlencoded"
		}
		payload = {'message' : msg}
		res = requests.post(self.url, headers = headers, params = payload)
		if res.status_code == 200:
			return True
		else:
			return False
		
	def post_sticker(self, msg, token, packageId, stickerId):
		headers = {
			'Authorization' : 'Bearer {}'.format(token)
		}
		payload = {
			'message' : msg,
			'stickerPackageId' : packageId,
			'stickerId' : stickerId
		}
		res = requests.post(self.url, headers=headers, params=payload)
	
	def post_image(self, msg, token, file):
		headers = {
			'Authorization' : "Bearer " + token
			# "Content-Type" : "application/x-www-form-data"			
		}
		payload = {
			'message' : msg
		}
		files = {
			'imageFile': file
		}
		res = requests.post(self.url, headers=headers, params=payload, files=files)
		if res.status_code == 200:
			return True
		else:
			return False