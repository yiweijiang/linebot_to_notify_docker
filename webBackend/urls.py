# For Line Bot API
from django.urls import path
from . import views

urlpatterns = [
    path('pttGossipingCrawler', views.ptt_Gossiping_crawler),
    path('pttStockCrawler', views.ptt_Stock_crawler),
]