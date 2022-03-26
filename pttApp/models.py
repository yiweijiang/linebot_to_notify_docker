#models.py
from django.db import models

# Create your models here.
class User_Info(models.Model):
    uid = models.CharField(max_length=50,null=False,default='')         #user_id
    name = models.CharField(max_length=255,blank=True,null=False)       #LINE名字
    pic_url = models.CharField(max_length=255,null=False)               #大頭貼網址
    mtext = models.CharField(max_length=255,blank=True,null=False)      #文字訊息紀錄
    notify = models.CharField(max_length=255,blank=True,null=False)     #Notify Access Token
    mdt = models.DateTimeField(auto_now=True)                           #物件儲存的日期時間 

    def __str__(self):
        return self.name

class User_Focus(models.Model):
    uid = models.CharField(max_length=50,null=False,default='')         # user_id
    board = models.CharField(max_length=255,blank=True,null=False)      # 關注的板
    mdt = models.DateTimeField(auto_now=True)                           # 物件儲存的日期時間 

class Ptt_Info(models.Model):
    TITLE = models.TextField()
    URL = models.URLField()
    NRECS = models.IntegerField()
    C_TIME = models.DateTimeField(auto_now_add=True)

class Group_Info(models.Model):
    name = models.CharField(max_length=255,blank=True,null=False)       #Group名字
    notify = models.CharField(max_length=255,blank=True,null=False)     #Notify Access Token
    mdt = models.DateTimeField(auto_now=True)                           #物件儲存的日期時間