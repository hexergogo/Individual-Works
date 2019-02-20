from django.urls import path,re_path
from Shops.views import *

urlpatterns = [
    re_path('^$',index),
    path('index/',index),
    path('goodsadd/',goodsAdd),
    path('goodslist/',goodsList),
    path('login/',login),
    path('loginout/',loginout),
    path('goodstypeadd/',goodsTypeAdd),
    re_path('goodschange/(\d+)/',goodsChange),
    re_path('goodsdel/(\d+)/',goodsDel),
    re_path('goodsdetails/(\d+)/',goodsDetails)
]