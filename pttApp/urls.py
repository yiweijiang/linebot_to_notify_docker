# For Line Bot API
from django.urls import path
from . import views

urlpatterns = [
    path('callback', views.callback),
    path('notify',views.notify),
]
