from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from pttApp.models import User_Info, Group_Info, User_Focus
import requests
import os
import re
from .Func.pttCrawler import PTTCrawler

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def Notify_MSG(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)

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
                print(event)
                msg = ''
                mtext = event.message.text # USER傳送的文字
                uid = event.source.user_id # USER ID
                profile = line_bot_api.get_profile(uid)
                name = profile.display_name # USER的名字
                pic_url = profile.picture_url # USER的大頭貼
                token = None

                message=[]
                if User_Info.objects.filter(uid=uid).exists()==False:
                    # 建立用戶資料
                    User_Info.objects.create(uid=uid,name=name,pic_url=pic_url,mtext=mtext)
                else:
                    # 更新用戶資料
                    User_Info.objects.filter(uid=uid).update(name=name,pic_url=pic_url,mtext=mtext)
                    token = User_Info.objects.filter(uid=uid)[0].notify # 獲得 token

                print('token', token)
                # 確保有先取得token
                if not token:
                    # url = f'https://notify-bot.line.me/oauth/authorize?response_type=code&client_id={settings.LINE_NOTIFY_CLIENT_ID}&redirect_uri={settings.NOTIFY_URL}&scope=notify&state=NO_STATE'
                    url = settings.NOTIFY_CONNECT_URL
                    msg = f'請先綁定 Line Notify\n點擊下方連結即可開始綁定\n{url}'
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )
                else:
                    if mtext == '連動Notify':
                        # url = f'https://notify-bot.line.me/oauth/authorize?response_type=code&client_id={settings.LINE_NOTIFY_CLIENT_ID}&redirect_uri={settings.NOTIFY_URL}&scope=notify&state=NO_STATE'
                        url = settings.NOTIFY_CONNECT_URL
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=url)
                        )

                    # 測試 LINE Notify 傳送訊息
                    elif mtext == 'Notify TEST':
                        msg = 'TEST!'
                        Notify_MSG(token, msg)

                    # 測試能否用 LINE Notify 傳送 PTT八卦版訊息
                    elif mtext == 'PTT TEST':
                        msg = PTTCrawler()
                        if msg != '\n':
                            Notify_MSG(token, msg)

                    # 測試是否可以成功傳送訊息到USER及GROUP中
                    elif mtext == '全體提醒':
                        users = User_Info.objects.all()
                        groups = Group_Info.objects.all()
                        msg = 'TEST'
                        for i in users:
                            Notify_MSG(i.notify, msg)
                        for i in groups:
                            Notify_MSG(i.notify, msg)

                    # 新增看板
                    elif 'ADD' in mtext:
                        msg = '目前沒有開放這個版喔~'
                        board = mtext.split()[-1]
                        boards = ['Gossiping', 'Stock']
                        if board in boards:
                            if User_Focus.objects.filter(uid=uid, board=board).exists()==False:
                                User_Focus.objects.create(uid=uid, board=board)
                                msg = f'幫你追蹤{board}版囉'
                            else:
                                msg = f'你已經追蹤{board}版囉'
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=msg)
                        )

                    # 取消看板
                    elif 'Cancel' in mtext:
                        msg = '目前沒有開放這個版喔~'
                        board = mtext.split()[-1]
                        boards = ['Gossiping', 'Stock']
                        if board in board:
                            if User_Focus.objects.filter(uid=uid, board=board).exists():
                                User_Focus.objects.filter(uid=uid, board=board).delete()
                                msg = f'幫你取消追蹤{board}版囉'
                            else:
                                msg = f'你沒追蹤{board}版喔'
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=msg)
                        )

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# 用來連動 LINE NOTIFY
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

    print(f'token:{token}')

    #抓取user的info
    user_info_url = 'https://notify-api.line.me/api/status'
    headers = {'Authorization':'Bearer '+token}
    get_user_info = requests.get(user_info_url,headers=headers)
    notify_user_info = get_user_info.json()
    if notify_user_info['targetType']=='USER':
        User_Info.objects.filter(name=notify_user_info['target']).update(notify=token)
    elif notify_user_info['targetType']=='GROUP':
        if Group_Info.objects.filter(name=notify_user_info['target']).exists():
            Group_Info.objects.filter(name=notify_user_info['target']).update(notify=token)
        else:
            Group_Info.objects.create(name=notify_user_info['target'], notify=token)

    return HttpResponse()