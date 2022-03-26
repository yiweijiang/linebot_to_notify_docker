from django.contrib import admin

# Register your models here.
from pttApp.models import *
from webBackend.models import *

class User_Info_Admin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'pic_url', 'mtext', 'notify', 'mdt')

class Ptt_Info_Admin(admin.ModelAdmin):
    list_display = ('TITLE', 'URL', 'NRECS', 'C_TIME')

class Group_Info_Admin(admin.ModelAdmin):
    list_display = ('name', 'notify', 'mdt')

class User_Focus_Admin(admin.ModelAdmin):
    list_display = ('uid', 'board', 'mdt')

class Ptt_News_Admin(admin.ModelAdmin):
    list_display = ('TITLE', 'BOARD', 'URL', 'NRECS', 'C_TIME')

admin.site.register(User_Info, User_Info_Admin)
admin.site.register(Ptt_Info, Ptt_Info_Admin)
admin.site.register(Group_Info, Group_Info_Admin)
admin.site.register(User_Focus, User_Focus_Admin)
admin.site.register(Ptt_News, Ptt_News_Admin)