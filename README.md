# LineBOT-django-notify
## docker串接django設定
### requirements.txt
會用到的套件
```
Django>=3.0,<4.0
psycopg2>=2.8
requests==2.27.1
line-bot-sdk==2.1.0
python-dotenv==0.19.2
```
### setting.py
把資料庫改為postgresql
```python
import os
   
[...]
   
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
}
```
### docker-compose.yml
基本參考[官方](https://docs.docker.com/samples/django/)就好
depend_on: 啟動順序，可用來等待特定容器先啟動完成  

```
docker-compose run web django-admin startproject pttLineBOT .
docker-compose up
```
到[http://localhost:8000/](http://localhost:8000/) 可以看到Django成功執行 

第一次執行會出現以下畫面
![](https://i.imgur.com/RdUhs0V.jpg)
是因為一開始還沒建構資料庫  

可以進入django的容器執行指令 `python manage.py migrate`  

進入容器的語法 `docker exec -it 容器ID bash`  

可透過`docker ps`查詢容器ID  
![](https://i.imgur.com/0nVWiN4.jpg)  

要離開容器輸入`exit`即可

```
python manage.py startapp pttApp
python manage.py makemigrations
python manage.py migrate
```
如果有新增套件在requirements.txt中，須執行
```
docker-compose build
```
重新build

## 串接Line BOT
### setting.py
```python
from dotenv import load_dotenv
# 載入敏感資料(.env)
load_dotenv()

#LINE Bot憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")


INSTALLED_APPS = [
      ...
      ...
      ...
    'pttApp',
]
```
透過 python-dotenv 載入本地端的.env檔案
.env格式如下
```
LINE_CHANNEL_ACCESS_TOKEN=xxxxxxxxxxxxxx
LINE_CHANNEL_SECRET=xxxxxxxxxxxxxx
```

### 在pttApp底下建立新的 urls.py
建立callback
```python
# For Line Bot API
from django.urls import path
from . import views

urlpatterns = [
    path('callback', views.callback),
]

```

### views.py
串接API
```python
from django.shortcuts import render
from pttApp.models import *
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# Create your views here.
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=event.message.text)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
```

## Test
### 透過 ngrok 在本地端測試，設定callback網址
![image](https://user-images.githubusercontent.com/33425754/159720900-27699148-5189-40d0-a7bb-57f0541448a4.png)