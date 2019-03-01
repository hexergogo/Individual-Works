"""EarphoneMall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from Buyers.views import *

urlpatterns = [  #主路由绑定app
    path('ckeditor/',include('ckeditor_uploader.urls')),
    path('shops/',include('Shops.urls')),
    path('buyers/',include('Buyers.urls')),
    path('blog/',include('Blog.urls')),

]

urlpatterns += [  #首页与注册页路由
    re_path('^$', daohang),
    path('index/',index),
    path('login/', login),
    path('loginout/', logout),
    path('reg/', register),
    path('sendMessage/', sendMessage),
    path('get_verify_img/',get_verify_img)
]

urlpatterns += [   #商品路由
    re_path('products/(\d+)/',products),
    re_path('productsdetail/(\d+)/', product_details),
]
