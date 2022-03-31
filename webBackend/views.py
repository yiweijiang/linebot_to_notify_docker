from django.shortcuts import render
from .Features.pttCrawler import PTTCrawler
from .Features.NotifyFunc import Line_Notify
from pttApp.models import User_Info, User_Focus
import requests
from datetime import datetime
import os
# Create your views here.

# 爬取八卦版資料
def ptt_Gossiping_crawler(request):
	t = datetime.now()
	t_str = t.strftime('%Y-%m-%d %H:%H:%S')
	print(f'現在時間：{t_str}')
	res = PTTCrawler('Gossiping').main(20)
	broadcast = User_Focus.objects.filter(board='Gossiping')
	for i in broadcast:
		users = User_Info.objects.filter(uid=i.uid)
		for user in users:
			print(f'Send msg to {user.name}')
			token = user.notify
			r = Line_Notify().post_text(res, token)
			if not r:
				User_Info.objects.filter(notify=token).delete()
				User_Focus.objects.filter(uid=i.uid).delete()
	return render(request, 'index.html')

# 爬取股版買賣超圖片
def ptt_Stock_crawler(request):
	t = datetime.now()
	t_str = t.strftime('%Y-%m-%d %H:%H:%S')
	print(f'現在時間：{t_str}')
	res_lst = PTTCrawler('Stock').StockCrawler()
	broadcast = User_Focus.objects.filter(board='Stock')
	for i in broadcast:
		users = User_Info.objects.filter(uid=i.uid)
		for user in users:
			print(f'Send msg to {user.name}')
			token = user.notify
			for idx, data in enumerate(res_lst):
				r = requests.get(data[-1], stream=True)
				if r.status_code == 200:
					with open(f"./{idx}.jpg", 'wb') as f:
						f.write(r.content)
					file = open(f"./{idx}.jpg", 'rb')
					status_code = Line_Notify().post_image(data[0], token, file)
					os.remove(f"./{idx}.jpg")
				if not status_code:
					User_Info.objects.filter(notify=token).delete()
					User_Focus.objects.filter(uid=i.uid).delete()
	return render(request, 'index.html')