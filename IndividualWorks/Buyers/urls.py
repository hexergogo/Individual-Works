from django.urls import path,re_path
from Buyers.views import *
urlpatterns = [
    path('cart/',cart,{'num':'0'}),
    re_path('cart/(\d+)/',cart),
    re_path('addCart/(\d+)/',addCart),
    re_path('delete_car_goods/(\d+)/',delete_car_goods),
    path('enterorder/',enterorder),
    path('enterpay/',enterpay),
    re_path('payVerify/(\d+)/',payVerify)
]