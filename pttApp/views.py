from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from pttApp.models import *
import requests
import os
import re

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
                # 獲取用戶資料
                mtext=event.message.text
                uid=event.source.user_id
                profile=line_bot_api.get_profile(uid)
                name=profile.display_name
                pic_url=profile.picture_url

                message=[]
                if User_Info.objects.filter(uid=uid).exists()==False:
                    # 建立用戶資料
                    User_Info.objects.create(uid=uid,name=name,pic_url=pic_url,mtext=mtext)
                else:
                    # 更新用戶資料
                    User_Info.objects.filter(uid=uid).update(name=name,pic_url=pic_url,mtext=mtext)

                if mtext == '連動Notify':
                    url = f'https://notify-bot.line.me/oauth/authorize?response_type=code&client_id={settings.LINE_NOTIFY_CLIENT_ID}&redirect_uri={settings.NOTIFY_URL}&scope=notify&state=NO_STATE'
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=url)
                    )

                # # 回傳一樣的話
                # line_bot_api.reply_message(
                #     event.reply_token,
                #     TextSendMessage(text=event.message.text)
                # )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def notify(request):
    pattern = 'code=.*&'

    code = None
    raw_uri = request.get_raw_uri()

    codes = re.findall(pattern,raw_uri)
    for code in codes:
        code = code[5:-1]

    #抓取user的notify token
    user_notify_token_get_url = 'https://notify-bot.line.me/oauth/token'
    params = {
        'grant_type':'authorization_code',
        'code':code,
        'redirect_uri':settings.NOTIFY_URL,
        'client_id':settings.LINE_NOTIFY_CLIENT_ID,
        'client_secret':settings.LINE_NOTIFY_CLIENT_SECRET
    }
    get_token = requests.post(user_notify_token_get_url,params=params)
    token = get_token.json()['access_token']

    #抓取user的info
    user_info_url = 'https://notify-api.line.me/api/status'
    headers = {'Authorization':'Bearer '+token}
    get_user_info = requests.get(user_info_url,headers=headers)
    notify_user_info = get_user_info.json()
    if notify_user_info['targetType']=='USER':
        User_Info.objects.filter(name=notify_user_info['target']).update(notify=token)
    elif notify_user_info['targetType']=='GROUP':
        pass
    return HttpResponse()