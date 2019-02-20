#coding:utf-8
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Seller(models.Model):  #卖家信息表
    username = models.CharField(max_length = 32)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    password = models.CharField(max_length=32)
    nickname = models.CharField(max_length = 32)
    photo = models.ImageField(upload_to = "image")


class Types(models.Model):  #耳机分类表
    label =  models.CharField(max_length = 32)
    description = models.TextField()

class Goods(models.Model):  #商品
    goods_name = models.CharField(max_length=32)
    goods_id = models.CharField(max_length = 32)
    goods_price = models.FloatField() #原价
    goods_now_price = models.FloatField() #当前价格
    goods_num = models.IntegerField() #库存
    goods_description = models.TextField() #概述
    goods_content = RichTextUploadingField() #详情
    types = models.ForeignKey(Types,on_delete = True) #一个分类会有多个商品
    seller = models.ForeignKey(Seller, on_delete=True) #一家店铺会有多个商品
    taobao = models.CharField(max_length=1024)

class Image(models.Model):  #商品展示托盘
    img_path = models.ImageField(upload_to = "image")
    img_label = models.CharField(max_length = 32)
    goods = models.ForeignKey(Goods, on_delete=True)  # 一个商品多张图片

# Create your models here.
