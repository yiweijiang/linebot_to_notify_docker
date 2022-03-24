from django.contrib import admin

# Register your models here.
from pttApp.models import User_Info, Ptt_Info

class User_Info_Admin(admin.ModelAdmin):
    list_display = ('uid','name','pic_url','mtext','notify','mdt')

class Ptt_Info_Admin(admin.ModelAdmin):
    list_display = ('TITLE', 'URL','NRECS','C_TIME')

admin.site.register(User_Info, User_Info_Admin)
admin.site.register(Ptt_Info, Ptt_Info_Admin)